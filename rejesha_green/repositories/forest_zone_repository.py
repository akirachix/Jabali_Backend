from sqlalchemy.orm import Session
from rejesha_green .models.forest_zone import ForestZone
from decimal import Decimal


def create_forest_zone(db: Session, zone):
    db_zone = ForestZone(**zone.dict())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


def get_all_forest_zones(db: Session):
    return db.query(ForestZone).all()


def get_forest_zone(db: Session, zone_id):
    return db.query(ForestZone).filter(
        ForestZone.zone_id == zone_id
    ).first()


def update_forest_zone(db: Session, zone_id, zone):

    db_zone = get_forest_zone(db, zone_id)

    if db_zone:

        if zone.block_name is not None:
            db_zone.block_name = zone.block_name

        if zone.resource_type is not None:
            db_zone.resource_type = zone.resource_type

        if zone.is_available is not None:
            db_zone.is_available = zone.is_available

        if zone.resource_price is not None:
            db_zone.resource_price = zone.resource_price

        db.commit()
        db.refresh(db_zone)

    return db_zone


def delete_forest_zone(db: Session, zone_id):
    db_zone = get_forest_zone(db, zone_id)

    if db_zone:
        db.delete(db_zone)
        db.commit()

    return db_zone


def get_resources_by_block(db: Session, block_name: str):
    return db.query(ForestZone).filter(
        ForestZone.block_name == block_name
    ).all()


def get_available_resources_by_block(db: Session, block_name: str):
    return db.query(ForestZone).filter(
        ForestZone.block_name == block_name,
        ForestZone.is_available == True
    ).all()


def update_resource_availability(
    db: Session,
    block_name: str,
    resource_type: str,
    is_available: bool,
    resource_price: Decimal
):
    resource = db.query(ForestZone).filter(
        ForestZone.block_name == block_name,
        ForestZone.resource_type == resource_type
    ).first()

    if resource:
        resource.is_available = is_available
        resource.resource_price = resource_price

        db.commit()
        db.refresh(resource)

    return resource




