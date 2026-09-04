from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import Optional
from rejesha_green.models.forest_zone import ForestBlocks, ResourceTypes
from decimal import Decimal



class ForestZoneCreate(BaseModel):
    community_forest_association_id: UUID
    block_name: str
    resource_type: str
    is_available: bool = True
    resource_price: Decimal

    @field_validator("block_name")
    @classmethod
    def validate_block(cls, value):
        if value not in [block.value for block in ForestBlocks]:
            raise ValueError("Invalid forest block")
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource(cls, value):
        if value not in [resource.value for resource in ResourceTypes]:
            raise ValueError("Invalid resource type")
        return value


class ForestZoneUpdate(BaseModel):
   
    block_name: Optional[str] = None
    resource_type: Optional[str] = None
    is_available: Optional[bool] = None
    resource_price: Optional[Decimal] = None

    @field_validator("block_name")
    @classmethod
    def validate_block(cls, value):
        if value is None:
            return value

        if value not in [block.value for block in ForestBlocks]:
            raise ValueError("Invalid forest block")

        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource(cls, value):
        if value is None:
            return value

        if value not in [resource.value for resource in ResourceTypes]:
            raise ValueError("Invalid resource type")

        return value


class ForestZoneResponse(BaseModel):
    zone_id: UUID
    community_forest_association_id: UUID
    block_name: str
    resource_type: str
    is_available: bool
    resource_price: Decimal

    class Config:
        from_attributes = True


class ResourceUpdate(BaseModel):
    block_name: str
    resource_type: str
    is_available: bool
    resource_price: Decimal