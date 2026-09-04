from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from rejesha_green.services import permit_payment_service


router = APIRouter(
    prefix="/permit-payments",
    tags=["Permit Payments"],
)


@router.post("/callback")
def payment_callback(
    payload:dict,
    db:Session=Depends(get_db),
):
    return permit_payment_service.process_permit_payment(
        db,
        payload,
    )

@router.post("/{permit_id}")
def initiate_payment(
    permit_id:int,
    db:Session=Depends(get_db),
):
    return permit_payment_service.initiate_permit_payment(
        db,
        permit_id,
    )

