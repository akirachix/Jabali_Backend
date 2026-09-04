from typing import List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
    Response,
    status,
)

from sqlalchemy.orm import Session

from database import get_db
from rejesha_green.schemas.permits import (
    PermitCreate,
    PermitRead,
    PermitUpdate,
)
from rejesha_green.services.permit_service import permit_service

router = APIRouter(
    prefix="/permits",
    tags=["Permits"],
)


@router.post(
    "/",
    response_model=PermitRead,
    status_code=status.HTTP_201_CREATED,
)
def create_permit(
    permit_in: PermitCreate,
    db: Session = Depends(get_db),
):
    return permit_service.create_permit(
        db,
        permit_in,
    )


@router.get(
    "/",
    response_model=List[PermitRead],
)
def list_permits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return permit_service.list_permits(
        db,
        skip,
        min(limit, 100),
    )


@router.get(
    "/payments/pending",
    response_model=List[PermitRead],
)
def list_pending_payments(
    db: Session = Depends(get_db),
):
    return permit_service.list_pending_payments(db)


@router.get(
    "/member/{member_id}",
    response_model=List[PermitRead],
)
def list_permits_for_member(
    member_id: UUID,
    db: Session = Depends(get_db),
):
    return permit_service.list_permits_for_member(
        db,
        member_id,
    )


@router.get(
    "/{permit_id}",
    response_model=PermitRead,
)
def get_permit(
    permit_id: int,
    db: Session = Depends(get_db),
):
    return permit_service.get_permit(
        db,
        permit_id,
    )


@router.patch(
    "/{permit_id}",
    response_model=PermitRead,
)
def update_permit(
    permit_id: int,
    permit_in: PermitUpdate,
    db: Session = Depends(get_db),
):
    return permit_service.update_permit(
        db,
        permit_id,
        permit_in,
    )


@router.post(
    "/{permit_id}/approve",
    response_model=PermitRead,
)
def approve_permit(
    permit_id: int,
    db: Session = Depends(get_db),
):
    return permit_service.approve_permit(
        db,
        permit_id,
    )


@router.delete(
    "/{permit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_permit(
    permit_id: int,
    db: Session = Depends(get_db),
):
    permit_service.delete_permit(
        db,
        permit_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


