from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator


class ClientFields(BaseModel):
    fname: str | None = None
    lname: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None


class ClientCreateRequest(ClientFields):
    # Validation to confirm that an identifier
    # for the client is in the request
    @model_validator(mode="after")
    def require_identifying_info(self):
        if not self.company_name and not (self.fname or self.lname):
            raise ValueError("Provide a company name or first/last name")
        return self


class ClientUpdateRequest(ClientFields):
    active: bool | None = None


class ClientDetailResponse(ClientFields):
    id: int
    display_name: str
    active: bool
    setup_dt: datetime
    updated_dt: datetime | None

    model_config = {"from_attributes": True}


class AddressCreateRequest(BaseModel):
    client_id: int
    is_default: bool
    label: str
    addr_line1: str
    addr_line2: str | None = None
    city: str
    state: str
    zip_code: str


class AddressUpdateRequest(BaseModel):
    is_default: bool | None = None
    label: str | None = None
    addr_line1: str | None = None
    addr_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


# Using inheritance for now. If the create request
# grows, this may have to change
class AddressDetailResponse(AddressCreateRequest):
    id: int
    setup_dt: datetime
    updated_dt: datetime | None

    model_config = {"from_attributes": True}
