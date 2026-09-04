from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db

from rejesha_green.schemas.forest_zone import (
    ForestZoneCreate,
    ForestZoneUpdate,
    ForestZoneResponse
)
from rejesha_green.models.forest_zone import ForestBlocks
from rejesha_green.services import forest_zone_service
from rejesha_green.security import require_role
from rejesha_green.models.user import UserRole


router = APIRouter(
    prefix="/forest-zones",
    tags=["Forest Zones"]
)


@router.post("/", response_model=ForestZoneResponse)
def create(
    zone: ForestZoneCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN.value,
            UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value,
            UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value
        )
    )
):
    return forest_zone_service.create_forest_zone(db, zone)


@router.get("/", response_model=list[ForestZoneResponse])
def get_all(
    db: Session = Depends(get_db)
):
    return forest_zone_service.get_all_forest_zones(db)


@router.get("/resources/{block_name}")
def get_resources(
    block_name: str,
    db: Session = Depends(get_db)
):
    result = forest_zone_service.get_resources_by_block(
        db,
        block_name
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid forest block"
        )

    return result


@router.get("/available-resources/{block_name}")
def get_available_resources(
    block_name: str,
    db: Session = Depends(get_db)
):
    result = forest_zone_service.get_available_resources_by_block(
        db,
        block_name
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid forest block"
        )

    return result
@router.get("/blocks")
def get_all_blocks():
    return [
        {
            "block_name": block.value,
        }
        for block in ForestBlocks
    ]


@router.get("/{zone_id}", response_model=ForestZoneResponse)
def get_one(
    zone_id: UUID,
    db: Session = Depends(get_db)
):
    result = forest_zone_service.get_forest_zone(
        db,
        zone_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Forest Zone not found"
        )

    return result


@router.put("/{zone_id}", response_model=ForestZoneResponse)
def update(
    zone_id: UUID,
    zone: ForestZoneUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN.value,
            UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value,
            UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value
        )
    )
):
    result = forest_zone_service.update_forest_zone(
        db,
        zone_id,
        zone
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Forest Zone not found"
        )

    return result


@router.delete("/{zone_id}")
def delete(
    zone_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN.value,
            UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value,
            UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value
        )
    )
):
    result = forest_zone_service.delete_forest_zone(
        db,
        zone_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Forest Zone not found"
        )

    return {
        "message": "Forest Zone deleted successfully"
    }