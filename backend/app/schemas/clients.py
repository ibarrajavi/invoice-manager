from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ClientFields(BaseModel):
    fname: str | None = None
    lname: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None


class ClientCreateRequest(ClientFields):
    # Name rules are enforced by the service (ClientNameError)
    pass


class ClientUpdateRequest(ClientFields):
    pass


class ClientDetailResponse(ClientFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    active: bool
    setup_dt: datetime
    updated_dt: datetime | None


class AddressFields(BaseModel):
    label: str
    addr_line1: str
    addr_line2: str | None = None
    city: str
    state: str
    zip_code: str


class AddressCreateRequest(AddressFields):
    pass


class AddressUpdateRequest(BaseModel):
    label: str | None = None
    addr_line1: str | None = None
    addr_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


class AddressDefaultRequest(BaseModel):
    is_default: bool


class AddressDetailResponse(AddressFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    is_default: bool
    setup_dt: datetime
    updated_dt: datetime | None
