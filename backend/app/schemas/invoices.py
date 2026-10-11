from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

InvoiceStatus = Literal["draft", "issued", "paid", "void"]
StatusTransitionTarget = Literal["issued", "paid", "void"]


class LineItemBase(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    qty: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0, decimal_places=2)


class LineItemCreateRequest(LineItemBase):
    # Position is assigned by the service from list order
    pass


class LineItemDetailResponse(LineItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    line_total: Decimal


class InvoiceCreateRequest(BaseModel):
    client_id: int
    address_id: int
    line_items: list[LineItemCreateRequest] = Field(min_length=1)


class InvoiceContentUpdateRequest(BaseModel):
    # Omitted fields stay UNSET in the service via model_dump(exclude_unset=True)
    client_id: int | None = None
    address_id: int | None = None
    line_items: list[LineItemCreateRequest] | None = Field(default=None, min_length=1)


class InvoiceStatusUpdateRequest(BaseModel):
    # Only checks the target value; whether the transition is
    # allowed from the current status is the service's job
    status: StatusTransitionTarget


class BillToSnapshot(BaseModel):
    # Populated by issue_invoice; null while the invoice is a draft
    bill_to_name: str | None = None
    bill_to_company: str | None = None
    bill_to_email: EmailStr | None = None
    bill_to_phone: str | None = None
    bill_to_addr_line1: str | None = None
    bill_to_addr_line2: str | None = None
    bill_to_city: str | None = None
    bill_to_state: str | None = None
    bill_to_zip_code: str | None = None


class InvoiceDetailResponse(BillToSnapshot):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    address_id: int
    invoice_no: str | None = None
    status: InvoiceStatus
    total: Decimal
    line_items: list[LineItemDetailResponse]
    has_pdf: bool
    setup_dt: datetime
    updated_dt: datetime | None
    issue_dt: datetime | None
    paid_dt: datetime | None
