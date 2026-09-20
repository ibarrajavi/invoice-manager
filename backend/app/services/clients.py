from enum import Enum
from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import (
    AddressDefaultError,
    AddressDeleteError,
    AddressInUseError,
    AddressNotFoundError,
    ClientActiveStateError,
    ClientDeleteError,
    ClientEmailError,
    ClientHasInvoicesError,
    ClientNameError,
    ClientNotFoundError,
    ClientStatusUpdateError,
    RequiredFieldError,
)
from app.models import Address, Client, Invoice


# Sentinel marking a field that was omitted
# Different from None which clears the field
class Sentinel(Enum):
    UNSET = "UNSET"


UNSET = Sentinel.UNSET
type Unset = Literal[Sentinel.UNSET]

# HELPER FUNCTIONS


def _clean(value: str | None) -> str | None:
    """Strip whitespace, returning None if the result is empty."""
    if value is None:
        return None
    return value.strip() or None


def _require(value: str, field: str) -> str:
    """
    Return the cleaned value, or raise if it is blank.

    - Raises RequiredFieldError if the value is empty or whitespace only.
    """
    cleaned = _clean(value)
    if cleaned is None:
        raise RequiredFieldError(field)
    return cleaned


def _clean_email(value: str | None) -> str | None:
    """Strip and lowercase an email, returning None if it is blank."""
    cleaned = _clean(value)
    return cleaned.lower() if cleaned else None


def _has_name(
    fname: str | None,
    lname: str | None,
    company_name: str | None,
) -> bool:
    """Return True if a client has a full name or a company name."""
    return bool(company_name or (fname and lname))


def _set_active(
    db: Session,
    client_id: int,
    active: bool,
) -> Client:
    """
    Update a Client's active status.

    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientActiveStateError if the client is already in the requested state.
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

    - Raises ClientNameError if the client's full name 
      or company name is not entered.
    - Raises ClientEmailError if email is taken.
    """
    fname = _clean(fname)
    lname = _clean(lname)
    email = _clean_email(email)
    phone = _clean(phone)
    company_name = _clean(company_name)

    # Must at least have a full name or company name
    if not _has_name(fname, lname, company_name):
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
    except IntegrityError as e:
        db.rollback()
        # Email is the only unique column, so this is a lost
        # race against the pre-check above
        raise ClientEmailError(email) from e
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
    - Raises ClientNameError if the update would leave the client
      without a full name or company name.
    - Raises ClientEmailError if email is taken.
    """
    # Check if a client is in the database
    client = get_client(db, client_id)

    if email is not UNSET:
        email = _clean_email(email)

    updates = {
        "fname": fname,
        "lname": lname,
        "email": email,
        "phone": phone,
        "company_name": company_name,
    }

    # Clean the provided fields. Omitted fields are ignored.
    changes = {
        field: _clean(value) for field, value in updates.items() if value is not UNSET
    }

    # Check the names the client will have after the update
    if not _has_name(
        changes.get("fname", client.fname),
        changes.get("lname", client.lname),
        changes.get("company_name", client.company_name),
    ):
        raise ClientNameError()

    # Check if the email is not taken by another client
    new_email = changes.get("email")
    if new_email and db.scalar(
        select(Client.id)
        .where(Client.email == new_email, Client.id != client_id)
        .limit(1)
    ):
        raise ClientEmailError(new_email)

    for field, value in changes.items():
        # setattr handles the assignment of the value (e.g., client.field = value)
        setattr(client, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ClientEmailError(new_email) from e
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
    client_id: int,
) -> Client:
    """
    Deactivate an existing client.

    - Raises ClientNotFoundError if client doesn't exist.
    - Raises ClientActiveStateError if the client is already inactive.
    - Raises ClientStatusUpdateError if the commit fails.
    """
    return _set_active(db, client_id, False)


def activate_client(
    db: Session,
    client_id: int,
) -> Client:
    """
    Activate an existing client.

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
    Return a specified client.

    - Raises ClientNotFoundError if client doesn't exist.
    """
    client = db.get(Client, client_id)
    if client is None:
        raise ClientNotFoundError(client_id)
    return client


def get_all_clients(
    db: Session,
) -> list[Client]:
    """Return a list of all clients, ordered by id."""
    return list(db.scalars(select(Client).order_by(Client.id)).all())


# ADDRESS FUNCTIONS


def create_address(
    db: Session,
    client_id: int,
    *,
    label: str,
    addr_line1: str,
    addr_line2: str | None = None,
    city: str,
    state: str,
    zip_code: str,
) -> Address:
    """
    Create a new address row and commit.

    Address line 2 is the only optional field.

    - Raises ClientNotFoundError if client doesn't exist.
    - Raises RequiredFieldError if a required field is blank.
    - Raises IntegrityError if a database constraint is violated.
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
    - Raises RequiredFieldError if a required field is blank.
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


def delete_address(
    db: Session,
    client_id: int,
    address_id: int,
) -> None:
    """
    Delete a specified address for a client.

    - Raises ClientNotFoundError if client doesn't exist.
    - Raises AddressNotFoundError if the address doesn't exist or belongs
      to a different client.
    - Raises AddressInUseError if the address is referenced elsewhere.
    - Raises AddressDeleteError if the delete fails for another reason.
    """
    address = get_address(db, client_id, address_id)

    try:
        db.delete(address)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise AddressInUseError(address_id, client_id) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise AddressDeleteError(address_id, client_id) from e


def get_address(
    db: Session,
    client_id: int,
    address_id: int,
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


def get_all_addresses(
    db: Session,
    client_id: int,
) -> list[Address]:
    """
    Return a list of all addresses for a client, ordered by id.

    - Raises ClientNotFoundError if client doesn't exist.
    """
    # First check if the client exists
    get_client(db, client_id)

    stmt = select(Address).where(Address.client_id == client_id).order_by(Address.id)
    return list(db.scalars(stmt).all())


def set_address_default(
    db: Session,
    client_id: int,
    address_id: int,
    is_default: bool,
) -> Address:
    """
    Set or clear the default address for a client.

    Any existing default address is cleared before setting a new one.

    - Raises ClientNotFoundError if client doesn't exist.
    - Raises AddressNotFoundError if the address doesn't exist or belongs
      to a different client.
    - Raises AddressDefaultError if another default was set at the same time.
    """
    address = get_address(db, client_id, address_id)
    # Nothing to do if already in the requested state
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
    except IntegrityError as e:
        db.rollback()
        raise AddressDefaultError(address_id, client_id) from e
    db.refresh(address)
    return address
