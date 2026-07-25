from sqlalchemy import Column, Integer, String, DateTime, func

from app.utils.database import Base

class AppSettings(Base):
    """
    This table contains the user's details
    that will appear on generated invoices.
    """
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)

    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    address_line1 = Column(String(50), nullable=True)
    address_line2 = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(10), nullable=True)
    phone_num = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    
    setup_dt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_dt = Column(DateTime(timezone=True), onupdate=func.now())

