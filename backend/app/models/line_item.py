from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import relationship

from app.utils.database import Base


class LineItem(Base):
    """
    This table contains the item details
    for a row on an invoice.
    """

    __tablename__ = "line_item"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False, index=True)

    description = Column(String(500), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False, server_default=text("0.00"))
    position = Column(Integer, nullable=False)

    invoice = relationship("Invoice", back_populates="line_items")

    __table_args__ = (
        CheckConstraint("qty > 0", name="qty_positive_check"),
        CheckConstraint("unit_price >= 0", name="unit_price_nonnegative_check"),
        CheckConstraint("position >= 0", name="position_nonnegative_check"),
        Index("idx_line_item_invoice_id_position", "invoice_id", "position"),
    )

    @property
    def line_total(self) -> Decimal:
        return self.qty * Decimal(self.unit_price)
