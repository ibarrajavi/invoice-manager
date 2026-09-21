from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, model_validator


class LineItemCreateRequest(BaseModel):
    description: str
    qty: int
    unit_price: Decimal
    position: int


class LineItemDetailResponse(LineItemCreateRequest):
    id: int

    model_config = {"from_attributes": True}


class InvoiceFields(BaseModel):
    # Snapshot of bill to details
    bill_to_name: str | None = None
    bill_to_company: str | None = None
    bill_to_email: EmailStr | None = None
    bill_to_phone: str | None = None
    bill_to_addr_line1: str | None = None
    bill_to_addr_line2: str | None = None
    bill_to_city: str | None = None
    bill_to_state: str | None = None
    bill_to_zip_code: str | None = None


class InvoiceCreateRequest(InvoiceFields):
    client_id: int
    # `Field(min_length=1)` basically ensures that we
    # aren't creating an invoice with zero line items
    line_items: list[LineItemCreateRequest] = Field(min_length=1)


class InvoiceContentUpdateRequest(InvoiceFields):
    client_id: int | None = None
    line_items: list[LineItemCreateRequest] | None = None


class InvoiceStatusUpdateRequest(BaseModel):
    status: str

    # Validation to ensure that an invoice status
    # cannot be reverted to "draft"
    @model_validator(mode="after")
    def validate_status(self):
        if self.status not in ("sent", "paid", "void"):
            raise ValueError("Invalid status transition target")
        return self


class InvoiceDetailResponse(InvoiceFields):
    id: int
    invoice_no: str | None = None
    status: str
    total: Decimal
    line_items: list[LineItemDetailResponse]
    has_pdf: bool

    model_config = {"from_attributes": True}
