from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.orm import relationship

from app.utils.database import Base

class Address(Base):
    """
    This table contains the company address for each client
    or job address tied to a specific client.
    """
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    client_id  = Column(Integer, ForeignKey("client.id"), nullable=False, index=True)

    is_default = Column(Boolean, default=False, nullable=False)
    label = Column(String(50), nullable=False, server_default=text("'billing'"))

    addr_line1 = Column(String(100), nullable=False)
    addr_line2 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(10), nullable=False)

    setup_dt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_dt = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", back_populates="addresses")

