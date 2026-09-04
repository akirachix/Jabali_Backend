import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from rejesha_green.models.user import User, UserRole
from rejesha_green.models.forest_zone import ForestZone

from rejesha_green.repositories.permit_repository import (
    permit_repository,
)

from rejesha_green.schemas.permits import (
    PermitCreate,
    PermitInternalUpdate,
    PermitUpdate,
)

from rejesha_green.services import permit_payment_service


logger = logging.getLogger(__name__)


class PermitService:


    def get_member(
        self,
        db: Session,
        member_id: UUID,
        phone_number: str,
    ) -> User:

        print("USSD PHONE RECEIVED:", phone_number)

    # Normalize Africa's Talking format
        if phone_number.startswith("254"):
            phone_number = "0" + phone_number[3:]

        print("NORMALIZED PHONE:", phone_number)

        members = db.query(User).all()

        for m in members:
            print("DB MEMBER:", m.phone, m.role)

        member = (
        db.query(User)
        .filter(User.phone == phone_number)
        .first()
    )
        if not member:
            raise HTTPException(
                status_code=404,
                detail="Member not found.",
        )
        if member.user_id != member_id:
            raise HTTPException(
                status_code=403,
                detail="Member ID and phone number do not match.",
            )


        if not member.is_active:
            raise HTTPException(
                status_code=403,
                detail="Member account inactive.",
            )

        if member.role != UserRole.MEMBER:
            raise HTTPException(
                status_code=403,
                detail="Only members can request permits.",
            )

        if member.community_forest_association_id is None:
            raise HTTPException(
                status_code=403,
                detail="Member is not assigned to a CFA.",
            )

        return member



    def create_permit(
        self,
        db: Session,
        data: PermitCreate,
    ):

        member = self.get_member(
            db,
            data.member_id,
            data.phone_number,
        )


        existing = permit_repository.get_by_ussd_session_id(
            db,
            data.ussd_session_id,
        )

        if existing:
            return existing


        permit_data = {

            "member_id": member.user_id,

            "forest_zone_id": data.forest_zone_id,

            "requested_resources": data.requested_resources,

            "resource_price_at_purchase":
                data.resource_price_at_purchase,

            "phone_number":
                data.phone_number,

            "ussd_session_id":
                data.ussd_session_id,

            "current_step":
                "resource_selected",

            "permit_status":
                "ussd_started",

            "payment_status":
                "not_initiated",

            "is_available":
                True,
        }


        return permit_repository.create(
            db,
            permit_data,
        )



    def get_permit(
        self,
        db: Session,
        permit_id:int,
    ):

        permit = permit_repository.get(
            db,
            permit_id,
        )

        if not permit:
            raise HTTPException(
                status_code=404,
                detail="Permit not found.",
            )

        return permit



    def list_permits(
        self,
        db:Session,
        skip:int=0,
        limit:int=100,
    ):

        return permit_repository.get_all(
            db,
            skip,
            min(limit,100),
        )



    def list_permits_for_member(
        self,
        db:Session,
        member_id:UUID,
    ):

        return permit_repository.get_by_member(
            db,
            member_id,
        )



    def update_permit(
        self,
        db:Session,
        permit_id:int,
        data:PermitUpdate,
    ):

        permit = self.get_permit(
            db,
            permit_id,
        )


        if permit.payment_status in {
            "pending",
            "paid",
            "completed",
        }:
            raise HTTPException(
                status_code=409,
                detail="Permit cannot be edited.",
            )


        return permit_repository.update(
            db,
            permit,
            data,
        )



    def approve_permit(
        self,
        db:Session,
        permit_id:int,
    ):

        permit = self.get_permit(
            db,
            permit_id,
        )


        if permit.payment_status not in {
            "paid",
            "completed",
        }:
            raise HTTPException(
                status_code=400,
                detail="Payment required first.",
            )


        permit_number = (
            permit.permit_number
            or
            f"MAU-{datetime.now(timezone.utc):%Y%m%d}"
            f"-{permit.permit_id:06d}"
        )


        return permit_repository.update(
            db,
            permit,
            PermitInternalUpdate(
                permit_status="approved",
                permit_number=permit_number,
                issued_at=datetime.now(timezone.utc),
            ),
        )



    def list_pending_payments(
        self,
        db:Session,
    ):

        return permit_repository.get_pending_payments(
            db
        )



    def handle_ussd_request(
        self,
        db:Session,
        session_id:str,
        phone_number:str,
        text:str,
    ) -> str:


        member = (
            db.query(User)
            .filter(User.phone == phone_number)
            .first()
        )


        if not member:
            return (
                "END Register as a member first."
            )


        if not member.is_active:
            return "END Membership inactive."


        if member.role != UserRole.MEMBER:
            return "END Only members can request permits."


        if member.community_forest_association_id is None:
            return "END No CFA assigned."


        parts = text.split("*") if text else []



        if not parts:

            return (
                "CON Welcome to Rejesha Green\n"
                "1. Request permit"
            )



        resources = (
            db.query(ForestZone)
            .filter(
                ForestZone.community_forest_association_id ==
                member.community_forest_association_id,

                ForestZone.is_available.is_(True),
            )
            .all()
        )



        # STEP 1
        if parts[0] == "1" and len(parts)==1:


            if not resources:
                return "END No resources available."


            response = (
                "CON Select resource:\n"
            )


            for index, resource in enumerate(
                resources,
                start=1
            ):

                response += (
                    f"{index}. "
                    f"{resource.resource_type} "
                    f"Ksh {resource.resource_price}\n"
                )


            return response.rstrip()



        # STEP 2
        if parts[0]=="1" and len(parts)==2:


            try:

                selected = resources[
                    int(parts[1])-1
                ]

            except:

                return "END Invalid resource."



            permit = self.create_permit(
                db,

                PermitCreate(
                    member_id=member.user_id,

                    phone_number=phone_number,

                    requested_resources=
                    selected.resource_type,

                    forest_zone_id=
                    selected.zone_id,

                    resource_price_at_purchase=
                    selected.resource_price,

                    ussd_session_id=
                    session_id,
                ),
            )



            permit_repository.update(
                db,
                permit,

                PermitInternalUpdate(
                    current_step=
                    "confirm_payment",

                    payment_amount=
                    selected.resource_price,
                ),
            )


            return (
                "CON Confirm payment\n"
                f"{selected.resource_type}\n"
                f"Ksh {selected.resource_price}\n"
                "1. Pay\n"
                "2. Cancel"
            )



        # STEP 3
        if parts[0]=="1" and len(parts)==3:


            permit = (
                permit_repository
                .get_by_ussd_session_id(
                    db,
                    session_id,
                )
            )


            if not permit:
                return "END Session expired."



            if parts[2]=="1":

                permit_repository.update(
                    db,
                    permit,

                    PermitInternalUpdate(
                        current_step=
                        "waiting_payment_phone",
                    ),
                )


                return (
                    "CON Enter M-Pesa phone number"
                )


            return "END Payment cancelled."



        # STEP 4
        if (
            len(parts)==4
            and parts[0]=="1"
            and parts[2]=="1"
        ):


            permit = (
                permit_repository
                .get_by_ussd_session_id(
                    db,
                    session_id,
                )
            )


            if not permit:
                return "END Session expired."



            permit_repository.update(
                db,
                permit,

                PermitInternalUpdate(
                    phone_number=parts[3],

                    current_step=
                    "payment_initiated",
                ),
            )



            permit_payment_service.initiate_permit_payment(
                db,
                permit.permit_id,
            )


            return (
                "END Payment request sent. "
                "Check your phone."
            )



        return "END Invalid selection."



permit_service = PermitService()