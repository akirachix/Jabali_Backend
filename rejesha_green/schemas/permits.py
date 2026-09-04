from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    member_id: UUID

    phone_number: str = Field(
        min_length=10,
        max_length=20,
    )
    forest_zone_id: UUID

    requested_resources: str = Field(
        min_length=1,
        max_length=200,
    )

   
    resource_price_at_purchase: Decimal

    ussd_session_id: str = Field(

        min_length=1,
        max_length=100,
    )


class PermitUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_resources: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )


class PermitInternalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    forest_zone_id: Optional[UUID] = None       
    requested_resources: Optional[str] = None   
    resource_price_at_purchase: Optional[Decimal] = None 

    base_fee: Optional[Decimal] = None
    payment_amount: Optional[Decimal] = None
    phone_number: Optional[str] = None

    permit_number: Optional[str] = None
    permit_status: Optional[str] = None
    payment_status: Optional[str] = None
    is_available: Optional[bool] = None
    max_permit: Optional[int] = None
    issued_at: Optional[datetime] = None

    expiry_date: Optional[datetime] = None
    merchant_request_id: Optional[str] = None
    checkout_request_id: Optional[str] = None
    mpesa_receipt_number: Optional[str] = None
    payment_created_at: Optional[datetime] = None
    payment_completed_at: Optional[datetime] = None

    current_step: Optional[str] = None
    session_data: Optional[str] = None


class PermitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    permit_id: int
    member_id: UUID
    forest_zone_id: UUID

    
    resource_price_at_purchase: Decimal
    base_fee: Optional[Decimal] = None
    payment_amount: Optional[Decimal] = None
    phone_number: str

    permit_number: Optional[str] = None
    permit_status: str
    payment_status: str
    is_available: bool
    max_permit: Optional[int] = None
    issued_at: Optional[datetime] = None

    expiry_date: Optional[datetime] = None
    merchant_request_id: Optional[str] = None
    checkout_request_id: Optional[str] = None
    mpesa_receipt_number: Optional[str] = None

    payment_created_at: Optional[datetime] = None
    payment_completed_at: Optional[datetime] = None

    ussd_session_id: str
    current_step: str
    session_data: Optional[str] = None

    session_created_at: datetime
    session_updated_at: Optional[datetime] = None

    deleted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None       