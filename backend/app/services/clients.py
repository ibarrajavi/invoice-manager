from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from enum import Enum
from typing import Literal

from app.models import Client, Invoice, Address
from app.exceptions import (
    ClientNotFoundError, 
    ClientHasInvoicesError, 
    ClientDeleteError, 
    ClientActiveStateError, 
    ClientNameError,
    ClientEmailError,
    ClientStatusUpdateError,
    AddressNotFoundError,
)

# Sentinel marking a field that was omitted
# Different from None which clears the field
class Sentinel(Enum):
    UNSET = "UNSET"

UNSET = Sentinel.UNSET
type Unset = Literal[Sentinel.UNSET]

# HELPER FUNCTIONS

def _clean(value):
    """Strips whitespace from string values."""
    if isinstance(value, str):
        return value.strip() or None
    return value

def _require(value: str, name: str) -> str:
    """Wrapper for clean, which is used for required fields."""
    cleaned = _clean(value)
    if cleaned is None:
        raise ValueError(f"{name} is required")
    return cleaned

def _set_active(
        db: Session,
        client_id: int,
        active: bool,
) -> Client:
    """
    Updates a Client's active status.
    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientActiveStateError if the client is already active.
    - Raises ClientStatusUpdateError if the commit fails.
    """
    client = get_client(db, client_id)

    if client.active == active:
        raise ClientActiveStateError(client_id, active)

    client.active = active
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ClientStatusUpdateError(client_id) from e
    return client

# CORE CLIENT FUNCTIONS

def create_client(
        db: Session,
        *,
        fname: str | None = None,
        lname: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_name: str | None = None,
) -> Client:
    """
    Create a new client row and commit.
    - Raises IntegrityError if a unique constraint is violated.
    - Raises ClientNameError if a client name is not entered.
    - Raises ClientEmailError if email is taken.
    """
    fname = _clean(fname)
    lname = _clean(lname)
    email = _clean(email)
    phone = _clean(phone)
    company_name = _clean(company_name)

    # Must at least have a full name or company name
    if not company_name and not (fname or lname):
        raise ClientNameError()

    # Email must be unique, if not raise custom exception
    if email and db.scalar(select(Client.id).where(Client.email == email).limit(1)):
        raise ClientEmailError(email)

    client = Client(
        fname=fname,
        lname=lname,
        email=email,
        phone=phone,
        company_name=company_name,
    )

    db.add(client)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Raising the error so the router can
        # return an HTTP error
        raise
    # Refreshing to load the setup_dt column
    db.refresh(client)
    return client

def update_client(
        db: Session,
        client_id: int,
        *,
        fname: str | None | Unset = UNSET,
        lname: str | None | Unset = UNSET,
        email: str | None | Unset = UNSET,
        phone: str | None | Unset = UNSET,
        company_name: str | None | Unset = UNSET,
) -> Client:
    """
    Update an existing client row and commit.
    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientNameError if a client name is not entered.
    - Raises ClientEmailError if email is taken.
    - Raises IntegrityError if a unique constraint is violated.
    """
    # Check if a client is in the database
    client = get_client(db, client_id)

    # Check if email is not taken
    if email is not UNSET:
        email = _clean(email)
        if email and db.scalar(
            select(Client.id)
            .where(Client.email == email, Client.id != client_id)
            .limit(1)
        ):
            raise ClientEmailError(email)
    
    updates = {
        "fname": fname,
        "lname": lname,
        "email": email,
        "phone": phone,
        "company_name": company_name,
    }

    for field, value in updates.items():
        if value is not UNSET:
            # setattr handles the assignment of the value (e.g., client.field = value)
            setattr(client, field, _clean(value))

    if not client.company_name and not (client.fname or client.lname):
        db.rollback()
        raise ClientNameError()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Raising the error so the router can
        # return an HTTP error
        raise
    # Refreshing to load the updated_dt column
    db.refresh(client)
    return client

def delete_client(
        db: Session,
        client_id: int,
) -> None:
    """
    Delete an existing client.
    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientHasInvoicesError if the client has any invoices.
    - Raises ClientDeleteError if the delete fails for another reason.
    """
    # Check if a client is in the database
    client = get_client(db, client_id)

    # Check if a client has invoices
    if db.scalar(select(Invoice.id).where(Invoice.client_id == client_id).limit(1)):
        raise ClientHasInvoicesError(client_id)

    try:
        db.delete(client)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ClientDeleteError(client_id) from e

def deactivate_client(
        db: Session, 
        client_id: int
    ) -> Client:
    """
    Deactivates an existing client.
    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientActiveStateError if the client is already inactive.
    - Raises ClientStatusUpdateError if the commit fails.
    """
    return _set_active(db, client_id, False)

def activate_client(
        db: Session, 
        client_id: int
    ) -> Client:
    """
    Activates an existing client.
    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientActiveStateError if the client is already active.
    - Raises ClientStatusUpdateError if the commit fails.
    """
    return _set_active(db, client_id, True)

def get_client(
        db: Session,
        client_id: int,
) -> Client:
    """
    Returns a specified client.
    - Raises ClientNotFoundError if client doesn't exist.
    """
    client = db.get(Client, client_id)
    if client is None:
        raise ClientNotFoundError(client_id)
    return client

def get_all_clients(
        db: Session,
) -> list[Client]:
    """Returns a list of all clients, ordered by id."""
    return list(db.scalars(select(Client).order_by(Client.id)).all())

# ADDRESS FUNCTIONS

def create_address(
        db: Session,
        client_id: int,
        *,
        label: str,
        addr_line1: str,
        # Address line 2 is the only optional field
        addr_line2: str | None = None,
        city: str,
        state: str,
        zip_code: str
) -> Address:
    """
    Create a new address row and commit.
    """
    # First check if client exists
    get_client(db, client_id)

    label = _require(label, "label")
    addr_line1 = _require(addr_line1, "addr_line1")
    addr_line2 = _clean(addr_line2)
    city = _require(city, "city")
    state = _require(state, "state")
    zip_code = _require(zip_code, "zip_code")

    address = Address(
        client_id=client_id,
        label=label,
        addr_line1=addr_line1,
        addr_line2=addr_line2,
        city=city,
        state=state,
        zip_code=zip_code,
    )

    db.add(address)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Raising the error so the router can
        # return an HTTP error
        raise
    # Refreshing to load the setup_dt column
    db.refresh(address)
    return address
    
def update_address(
    db: Session,
    client_id: int,
    address_id: int,
    *,
    label: str | Unset = UNSET,
    addr_line1: str | Unset = UNSET,
    addr_line2: str | None | Unset = UNSET,
    city: str | Unset = UNSET,
    state: str | Unset = UNSET,
    zip_code: str | Unset = UNSET,
) -> Address:
    """
    Update an existing address row and commit.
    - Raises ClientNotFoundError if the client doesn't exist.
    - Raises AddressNotFoundError if the address doesn't exist or
      belongs to a different client.
    - Raises ValueError if a required field is blank.
    - Raises IntegrityError if a database constraint is violated.
    """
    address = get_address(db, client_id, address_id)

    updates = {
        "label": label,
        "addr_line1": addr_line1,
        "addr_line2": addr_line2,
        "city": city,
        "state": state,
        "zip_code": zip_code,
    }
    required = {"label", "addr_line1", "city", "state", "zip_code"}

    # Validate everything first so a failure leaves the object untouched
    changes = {}
    for field, value in updates.items():
        if value is UNSET:
            continue
        changes[field] = _require(value, field) if field in required else _clean(value)

    for field, value in changes.items():
        setattr(address, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Raising the error so the router can
        # return an HTTP error
        raise
    # Refreshing to load the updated_dt column
    db.refresh(address)
    return address

def delete_address():
    pass

def get_address(
        db: Session,
        client_id: int,
        address_id: int
) -> Address:
    """
    Return the address with the given ID for the given client.

    - Raises ClientNotFoundError if client doesn't exist.
    - Raises AddressNotFoundError if the address doesn't exist or belongs
    to a different client.
    """
    get_client(db, client_id)

    address = db.get(Address, address_id)
    if address is None or address.client_id != client_id:
        raise AddressNotFoundError(address_id, client_id)
    return address

def get_all_addresses():
    pass

def set_default_address(
        db: Session,
        client_id: int,
        address_id: int,
        is_default: bool,
) -> Address:
    address = get_address(db, client_id, address_id)
    # Check if the address is already the default
    if address.is_default == is_default:
        return address

    if is_default:
        db.execute(
            update(Address)
            .where(Address.client_id == client_id, Address.is_default.is_(True))
            .values(is_default=False)
        )
    address.is_default = is_default

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(address)
    return address

