from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, CheckConstraint, func, text
from sqlalchemy.orm import relationship

from app.utils.database import Base

class Invoice(Base):
    """
    This table contains all the data
    that will be displayed on an invoice.
    """
    __tablename__ = "invoice"
    
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String(32), nullable=True, unique=True, index=True)
    client_id  = Column(Integer, ForeignKey("client.id"), nullable=False, index=True)

    setup_dt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_dt = Column(DateTime(timezone=True), onupdate=func.now())
    issue_dt = Column(DateTime(timezone=True), nullable=True, index=True)
    paid_dt = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(10), nullable=False, server_default=text("'draft'"), index=True)
    total = Column(Numeric(12, 2), nullable=False, server_default=text("0.00"))
    pdf_path = Column(String(512), nullable=True)

    bill_to_name = Column(String(256), nullable=True)
    bill_to_company = Column(String(256), nullable=True)
    bill_to_email = Column(String(150), nullable=True)
    bill_to_phone = Column(String(20), nullable=True)

    bill_to_addr_line1 = Column(String(100), nullable=True)
    bill_to_addr_line2 = Column(String(100), nullable=True)
    bill_to_city = Column(String(50), nullable=True)
    bill_to_state = Column(String(50), nullable=True)
    bill_to_zip_code = Column(String(10), nullable=True)

    client = relationship("Client", back_populates="invoices")
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan", order_by="LineItem.position")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'sent', 'paid', 'void')", name="status_valid_values_check"),
        CheckConstraint("total >= 0", name="total_nonnegative_check"),
    )

    # `has_pdf` is a field in the InvoiceDetailResponse schema
    @property
    def has_pdf(self) -> bool:
        return self.pdf_path is not None