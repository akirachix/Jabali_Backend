import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    
)
from sqlalchemy.dialects.postgresql import UUID


from database import Base


class UserGroup(str, enum.Enum):
    TREE_PLANTING = "tree_planting"
    TREE_NURSERY = "tree_nursery"
    FOREST_CLEANING = "forest_cleaning"
    FOREST_PATROL = "forest_patrol"
    FIRE_PREVENTION = "fire_prevention"
    FIRE_FIGHTING = "fire_fighting"
    FOREST_RESTORATION = "forest_restoration"
    INVASIVE_SPECIES_CONTROL = "invasive_species_control"
    WATER_SOURCE_PROTECTION = "water_source_protection"
    WILDLIFE_MONITORING = "wildlife_monitoring"
    BIODIVERSITY_MONITORING = "biodiversity_monitoring"
    ECO_TOURISM = "eco_tourism"
    ENVIRONMENTAL_EDUCATION = "environmental_education"
    COMMUNITY_AWARENESS = "community_awareness"
    TRAINING_WORKSHOP = "training_workshop"
    NURSERY_MAINTENANCE = "nursery_maintenance"
    TREE_MAINTENANCE = "tree_maintenance"
    AGROFORESTRY = "agroforestry"
    SUSTAINABLE_HARVESTING = "sustainable_harvesting"
    BEEKEEPING = "beekeeping"
    CONFLICT_RESOLUTION = "conflict_resolution"
    FOREST_BOUNDARY_MAPPING = "forest_boundary_mapping"
    ILLEGAL_ACTIVITY_REPORTING = "illegal_activity_reporting"
    FOREST_INVENTORY = "forest_inventory"
    COMMUNITY_MEETING = "community_meeting"


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=(uuid.uuid4()),
      
    )   


    created_by = Column(
    UUID(as_uuid=True),
    ForeignKey("users.user_id"),
    nullable=False,
    )

    
    
    zone_id = Column(
        UUID(as_uuid=True),
        ForeignKey("forest_zones.zone_id"),
        nullable=False,
    )
    activity_name = Column(
        String(100),
        nullable=False)


    scheduled_date = Column(
        DateTime(timezone=True),
        nullable=False)


    description = Column(
        Text,
        nullable=True)


    user_group = Column(
        Enum(UserGroup),
        nullable=True)



    expected_attendees = Column(
        Integer, 
        nullable=False)


    actual_attendees = Column(
        Integer, 
        nullable=False, default=0)


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )