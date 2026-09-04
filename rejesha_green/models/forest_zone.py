from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey
from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

class ForestBlocks(str, enum.Enum):
    MAJI_MAZURI = "Maji Mazuri"
    CHEMOROGOK = "Chemorogok"
    EASTERN_MAU = "Eastern Mau"
    EBURU = "Eburu"
    KILOMBE_HILL = "Kilombe Hill"
    LEMBUS = "Lembus"
    LONDIANI = "Londiani"
    WESTERN_MAU = "Western Mau"
    MAASAI_MAU = "Maasai Mau"
    MAU_NAROK = "Mau Narok"
    MOLO = "Molo"
    NORTHERN_TINDERET = "Northern Tinderet"
    OLPOSIMORU = "Olposimoru"
    METKEI = "Metkei"
    SOUTH_WEST_MAU = "South West Mau"
    SOUTH_MAU = "South Mau"
    TINDERET = "Tinderet"
    TRANSMARA = "Transmara"
    WEST_MOLO = "West Molo"
    TIMBOROA = "Timboroa"
    WEST_MAU = "West Mau"
    NABKOI = "Nabkoi"
    

class ResourceTypes(str, enum.Enum):
    FIREWOOD = "Firewood"
    GRASS = "Grass"
    BAMBOO = "Bamboo"
    HONEY = "Honey"
    MEDICINAL_PLANTS = "Medicinal plants"
    GRAZING = "Grazing"
    FODDER = "Fodder"
    FARMING = "Farming"
    SEEDLINGS = "Seedlings"
    POLES = "Poles"


class ForestZone(Base):
    __tablename__ = "forest_zones"

    zone_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    community_forest_association_id = Column(
    UUID(as_uuid=True),
    ForeignKey(
        "community_forest_associations.community_forest_association_id"
    ),
    nullable=False,
    index=True,
)
    block_name = Column(String(100), nullable=False)
    resource_type = Column(String(100),nullable=False)
    is_available = Column(Boolean,default=True,nullable=False)
    # resource_price = Column(Numeric(10,2),nullable=False)
    resource_price = Column("price", Numeric(10, 2), nullable=False)
    community_forest_association = relationship(
    "CommunityForestAssociation"
       
)