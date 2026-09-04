from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from rejesha_green.config import settings
from rejesha_green.models.permit import Permit
from rejesha_green.services.daraja_service import stk_push
from rejesha_green.services.sms_service import SMSService



def initiate_permit_payment(
    db: Session,
    permit_id: int,
):

    permit = (
        db.query(Permit)
        .filter(Permit.permit_id == permit_id)
        .first()
    )

    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permit not found",
        )

    if permit.payment_status in {
        "paid",
        "completed",
    }:
        raise HTTPException(
            status_code=400,
            detail="Permit already paid",
        )


    response = stk_push(
        phone=permit.phone_number,
        amount=int(
            permit.payment_amount
            or permit.resource_price_at_purchase
        ),
        account_reference=f"PERMIT-{permit.permit_id}",
        transaction_description="Forest resource permit",
        callback_url=settings.PERMIT_CALLBACK_URL,
    )


    permit.merchant_request_id = response.get(
        "MerchantRequestID"
    )

    permit.checkout_request_id = response.get(
        "CheckoutRequestID"
    )

    permit.payment_status = "pending"

    permit.payment_created_at = datetime.now(
        timezone.utc
    )


    db.commit()

    return response



def process_permit_payment(
    db: Session,
    payload: dict,
):

    callback = (
        payload
        .get("Body", {})
        .get("stkCallback", {})
    )


    permit = (
        db.query(Permit)
        .filter(
            Permit.checkout_request_id ==
            callback.get("CheckoutRequestID")
        )
        .first()
    )


    if not permit:
        return {
            "status": "failed",
            "message": "Permit not found",
        }


    if permit.payment_status == "paid":
        return {
            "status": "success",
            "message": "Already processed",
        }


    if callback.get("ResultCode") == 0:


        items = (
            callback
            .get("CallbackMetadata", {})
            .get("Item", [])
        )


        receipt = next(
            (
                i.get("Value")
                for i in items
                if i.get("Name")
                == "MpesaReceiptNumber"
            ),
            None,
        )


        now = datetime.now(
            timezone.utc
        )


        permit.payment_status = "paid"
        permit.mpesa_receipt_number = receipt
        permit.payment_completed_at = now

        permit.permit_status = "approved"
        permit.issued_at = now


        if not permit.permit_number:

            permit.permit_number = (
                f"MAU-{now:%Y%m%d}"
                f"-{permit.permit_id:06d}"
            )


        permit.expiry_date = (
            now + timedelta(days=30)
        )


        db.commit()
        db.refresh(permit)


        SMSService.send_sms(
            phone_number=permit.phone_number,
            message=(
                "Rejesha Green: Payment successful.\n"
                f"Permit No: {permit.permit_number}\n"
                f"Resource: {permit.requested_resources}\n"
                f"Valid until: "
                f"{permit.expiry_date:%d-%m-%Y}"
            ),
        )


    else:

        permit.payment_status = "failed"

        db.commit()


    return {
        "status": "success",
    }