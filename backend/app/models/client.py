from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.utils.database import Base


class Client(Base):
    """
    This table contains the client details
    that will be displayed on issued invoices.
    """

    __tablename__ = "client"

    id = Column(Integer, primary_key=True)

    fname = Column(String(150), nullable=True)
    lname = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True, unique=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    company_name = Column(String(256), nullable=True)

    active = Column(Boolean, nullable=False, default=True)

    setup_dt = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_dt = Column(DateTime(timezone=True), onupdate=func.now())

    invoices = relationship("Invoice", back_populates="client")
    addresses = relationship(
        "Address", back_populates="client", cascade="all, delete-orphan"
    )

    # Prioritize the company name and if there is no
    # company name, then return the full client name
    @property
    def display_name(self):
        if self.company_name:
            return self.company_name
        full_name = f"{self.fname or ''} {self.lname or ''}".strip()
        return full_name or f"Client #{self.id}"
