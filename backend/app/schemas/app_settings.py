from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AppSettingsFields(BaseModel):
    invoice_prefix: str | None = Field(default=None, max_length=10)
    pdf_storage_dir: str | None = None
    fname: str | None = None
    lname: str | None = None
    addr_line1: str | None = None
    addr_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    phone_num: str | None = None
    email: EmailStr | None = None


class AppSettingsUpdateRequest(AppSettingsFields):
    # Omitted fields stay UNSET in the service via model_dump(exclude_unset=True)
    next_invoice_number: int | None = Field(default=None, ge=1)


class AppSettingsDetailResponse(AppSettingsFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    next_invoice_number: int
    setup_dt: datetime
    updated_dt: datetime | None
