from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from database import Base

#from sqlalchemy.orm import relationship


class Permit(Base):
    __tablename__ = "permits"
    permit_id = Column(Integer,primary_key=True,index=True,)
    member_id = Column(UUID(as_uuid=True),ForeignKey("users.user_id"),nullable=False,index=True,)
    requested_resources = Column(String(200),nullable=False,)
    base_fee = Column(Numeric(10, 2),nullable=True,)
    payment_amount = Column(Numeric(10, 2),nullable=True,)
    phone_number = Column(String(20),nullable=False,index=True,)
    permit_number = Column(String(50),unique=True,nullable=True,index=True,)
    permit_status = Column(String(30),nullable=False,default="ussd_started",index=True,)
    is_available = Column(Boolean,nullable=False,default=True,)
    max_permit = Column(Integer,nullable=True,)
    issued_at = Column(DateTime(timezone=True),nullable=True,)
    payment_status = Column(String(30),nullable=False,default="not_initiated",index=True,)
    merchant_request_id = Column(String(100),nullable=True,index=True,)
    checkout_request_id = Column(String(100),unique=True,nullable=True,index=True,)
    mpesa_receipt_number = Column(String(50),unique=True,nullable=True,index=True,)
    payment_created_at = Column(DateTime(timezone=True),nullable=True,)
    payment_completed_at = Column(DateTime(timezone=True),nullable=True,)
    ussd_session_id = Column(String(100),unique=True,nullable=False,index=True,)
    forest_zone_id = Column(UUID(as_uuid=True),ForeignKey("forest_zones.zone_id"),nullable=False, index=True,)
    resource_price_at_purchase = Column(Numeric(10, 2),nullable=False,)
    expiry_date = Column(DateTime(timezone=True),nullable=True,)



# payments = relationship("Payment", back_populates="permit")
    current_step = Column(String(50),nullable=False,default="start",)
    session_data = Column(String(2000),nullable=True,)  
   
    session_created_at = Column( DateTime(timezone=True), server_default=func.now(),nullable=False,)
    session_updated_at = Column(DateTime(timezone=True),onupdate=func.now(),nullable=True,)
    deleted_at = Column(DateTime(timezone=True),nullable=True,index=True,)
    
