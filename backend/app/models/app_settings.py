from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, func, text

from app.utils.database import Base


class AppSettings(Base):
    """
    This table contains the user's details
    that will appear on generated invoices.
    """

    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)
    invoice_prefix = Column(String(10), nullable=True, server_default=text("'INV-'"))
    next_invoice_number = Column(Integer, nullable=False, server_default=text("1"))
    pdf_storage_dir = Column(String(500), nullable=True)

    fname = Column(String(50), nullable=True)
    lname = Column(String(50), nullable=True)
    addr_line1 = Column(String(50), nullable=True)
    addr_line2 = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(10), nullable=True)
    phone_num = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    setup_dt = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_dt = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "next_invoice_number >= 1", name="next_invoice_number_positive_check"
        ),
    )
