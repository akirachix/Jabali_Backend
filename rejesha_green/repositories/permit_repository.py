from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rejesha_green.models.permit import Permit
from rejesha_green.schemas.permits import (
    PermitInternalUpdate,
    PermitUpdate,
)


class PermitRepository:

    def create(
        self,
        db: Session,
        permit_data: dict,
    ) -> Permit:
        permit = Permit(**permit_data)

        try:
            db.add(permit)
            db.commit()
            db.refresh(permit)
            return permit
        except Exception:
            db.rollback()
            raise

    def get(
        self,
        db: Session,
        permit_id: int,
    ) -> Optional[Permit]:
        return (
            db.query(Permit)
.filter(
                Permit.permit_id == permit_id,
                Permit.deleted_at.is_(None),
            )
.first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            db.query(Permit)
.filter(Permit.deleted_at.is_(None))
.order_by(Permit.session_created_at.desc())
.offset(skip)
.limit(limit)
.all()
        )

    def get_by_member(
        self,
        db: Session,
        member_id: UUID,
    ):
        return (
            db.query(Permit)
.filter(
                Permit.member_id == member_id,
                Permit.deleted_at.is_(None),
            )
   .order_by(Permit.session_created_at.desc())
.all()
        )

    def get_by_ussd_session_id(
        self,
        db: Session,
        session_id: str,
    ) -> Optional[Permit]:
        return (
            db.query(Permit)
.filter(
                Permit.ussd_session_id == session_id,
                Permit.deleted_at.is_(None),
            )
.first()
        )

    def get_by_checkout_request_id(
        self,
        db: Session,
        checkout_request_id: str,
    ) -> Optional[Permit]:
        return (
            db.query(Permit)
.filter(
                Permit.checkout_request_id == checkout_request_id,
                Permit.deleted_at.is_(None),
            )
.first()
        )

    def get_pending_payments(self, db: Session):
        return (
            db.query(Permit)
.filter(
                Permit.payment_status == "pending",
                Permit.deleted_at.is_(None),
            )
.order_by(Permit.session_created_at.desc())
.all()
        )

    def update(
        self,
        db: Session,
        permit: Permit,
        data: PermitUpdate | PermitInternalUpdate,
    ) -> Permit:
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        for field, value in values.items():
            setattr(permit, field, value)

        try:
            db.commit()
            db.refresh(permit)
            return permit
        except Exception:
            db.rollback()
            raise

    def delete(
        self,
        db: Session,
        permit: Permit,
    ) -> None:
        permit.deleted_at = datetime.now(timezone.utc)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise


permit_repository = PermitRepository()
