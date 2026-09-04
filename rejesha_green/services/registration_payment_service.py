import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from rejesha_green.models.user import UserRole
from rejesha_green.models.registration_payment import RegistrationPayment, PaymentStatus
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.repositories.community_forest_association_repository import CommunityForestAssociationRepository
from rejesha_green.repositories.registration_payment_repository import RegistrationPaymentRepository
from rejesha_green.services.daraja_service import stk_push
from rejesha_green.services.sms_service import SMSService
from rejesha_green.services.user_service import generate_member_number
from rejesha_green.config import settings


def initiate_registration_payment(db: Session, member_id: uuid.UUID, current_user):

    user_repo = UserRepository(db)
    cfa_repo = CommunityForestAssociationRepository(db)
    payment_repo = RegistrationPaymentRepository(db)

    official = user_repo.get_user(uuid.UUID(current_user["sub"]))

    if not official or official.role != UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL:
        raise HTTPException(403, "Only CFA officials can initiate registration payments")

    member = user_repo.get_user(member_id)

    if not member:
        raise HTTPException(404, "Member not found")

    if member.role != UserRole.MEMBER:
        raise HTTPException(400, "User is not a member")

    if member.community_forest_association_id != official.community_forest_association_id:
        raise HTTPException(403, "Member does not belong to this CFA")

    cfa = cfa_repo.get(member.community_forest_association_id)

    if not cfa:
        raise HTTPException(404, "CFA not found")

    if member.membership_number:
        raise HTTPException(400, "Member already registered")

    if not cfa.registration_fee:
        raise HTTPException(400, "Invalid registration fee")

    pending = payment_repo.get_pending_by_member(member_id)

    if pending:
        return {
            "message": "Payment already pending",
            "checkout_request_id": pending.checkout_request_id
        }

    payment = payment_repo.create(
        RegistrationPayment(
            member_id=member.user_id,
            community_forest_association_id=cfa.community_forest_association_id,
            amount=cfa.registration_fee,
            phone=member.phone,
            status=PaymentStatus.PENDING
        )
    )

    try:

        result = stk_push(
            phone=member.phone,
            amount=int(cfa.registration_fee),
            account_reference=f"REG-{member.user_id}",
            transaction_description="CFA membership registration",
            callback_url=settings.REGISTRATION_CALLBACK_URL
        )

    except Exception as exc:

        print("REGISTRATION MPESA ERROR:", exc)

        payment.status = PaymentStatus.FAILED
        payment_repo.update(payment)

        raise HTTPException(
            502,
            "Failed to initiate M-Pesa payment"
        )


    if str(result.get("ResponseCode")) != "0":

        payment.status = PaymentStatus.FAILED
        payment_repo.update(payment)

        raise HTTPException(
            502,
            result.get(
                "ResponseDescription",
                "Daraja failed"
            )
        )


    payment.checkout_request_id = result.get("CheckoutRequestID")
    payment.merchant_request_id = result.get("MerchantRequestID")

    payment_repo.update(payment)


    return {
        "message":"Registration payment initiated",
        "payment_id":str(payment.payment_id),
        "member_id":str(member.user_id),
        "amount":payment.amount,
        "phone":payment.phone,
        "checkout_request_id":payment.checkout_request_id
    }



def process_registration_payment(db: Session, payload: dict):

    payment_repo = RegistrationPaymentRepository(db)

    callback = payload.get("Body",{}).get("stkCallback",{})

    checkout_id = callback.get("CheckoutRequestID")

    if not checkout_id:
        raise HTTPException(400,"CheckoutRequestID missing")


    payment = payment_repo.get_by_checkout_id(checkout_id)

    if not payment:
        raise HTTPException(404,"Payment not found")


    if callback.get("ResultCode") == 0:

        items = {
            x.get("Name"):x.get("Value")
            for x in callback.get("CallbackMetadata",{}).get("Item",[])
        }

        payment.status = PaymentStatus.PAID
        payment.mpesa_receipt = items.get("MpesaReceiptNumber")
        payment.paid_at = datetime.utcnow()

        payment_repo.update(payment)

        member = payment.member

        if not member.membership_number:
            member.membership_number = generate_member_number()

        db.commit()


        try:

            SMSService.send_sms(
                phone_number=member.phone,
                message=(
                    "Rejesha Green: Registration successful.\n"
                    f"Membership Number: {member.membership_number}"
                )
            )

        except Exception as exc:

            print("REGISTRATION SMS ERROR:",exc)


        return {
            "message":"Registration payment completed",
            "membership_number":member.membership_number
        }


    payment.status = PaymentStatus.FAILED
    payment_repo.update(payment)


    return {
        "message":"Registration payment failed",
        "result_code":callback.get("ResultCode")
    }