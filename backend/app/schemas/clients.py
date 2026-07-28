from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional
from datetime import datetime

class ClientFields(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None

class ClientCreateRequest(ClientFields):
    # Validation to confirm that an identifier
    # for the client is in the request
    @model_validator(mode="after")
    def require_identifying_info(self):
        if not self.company_name and not (self.fname or self.lname):
            raise ValueError("Provide a company name or first/last name")
        return self

class ClientUpdateRequest(ClientFields):
    active: Optional[bool] = None

class ClientDetailResponse(ClientFields):
    id: int
    display_name: str
    active: bool
    setup_dt: datetime
    updated_dt: datetime | None

    model_config = {
        "from_attributes": True
    }

class AddressCreateRequest(BaseModel):
    client_id: int
    is_default: bool
    label: str
    addr_line1: str
    addr_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str

class AddressUpdateRequest(BaseModel):
    is_default: Optional[bool] = None
    label: Optional[str] = None
    addr_line1: Optional[str] = None
    addr_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

# Using inheritance for now. If the create request
# grows, this may have to change
class AddressDetailResponse(AddressCreateRequest):
    id: int
    setup_dt: datetime
    updated_dt: datetime | None

    model_config = {
        "from_attributes": True
    }
