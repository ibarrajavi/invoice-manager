from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from enum import Enum
from typing import Literal

from app.models import Client, Invoice
from app.exceptions import (
    ClientNotFoundError, 
    ClientHasInvoicesError, 
    ClientDeleteError, 
    ClientActiveStateError, 
    ClientNameError,
    ClientEmailError,
    ClientStatusUpdateError,
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

def _set_active(
        db: Session,
        client_id: int,
        active: bool,
) -> Client:
    """
    Updates a Client's active status.
    Raises ClientNotFoundError if client doesn't exist.
    Raises ClientActiveStateError if the client is already active.
    Raises ClientStatusUpdateError if the commit fails.
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

# CLIENT FUNCTIONS

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
    Raises IntegrityError if a unique constraint is violated.
    Raises ClientNameError if a client name is not entered.
    Raises ClientEmailError if email is taken.
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
    Raises ClientNotFoundError if client doesn't exist.
    Raises ClientNameError if a client name is not entered.
    Raises ClientEmailError if email is taken.
    Raises IntegrityError if a unique constraint is violated.
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
    Raises ClientNotFoundError if client doesn't exist.
    Raises ClientHasInvoicesError if the client has any invoices.
    Raises ClientDeleteError if the delete fails for another reason.
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
    Raises ClientNotFoundError if client doesn't exist.
    Raises ClientActiveStateError if the client is already inactive.
    Raises ClientStatusUpdateError if the commit fails.
    """
    return _set_active(db, client_id, False)

def activate_client(
        db: Session, 
        client_id: int
    ) -> Client:
    """
    Activates an existing client.
    Raises ClientNotFoundError if client doesn't exist.
    Raises ClientActiveStateError if the client is already active.
    Raises ClientStatusUpdateError if the commit fails.
    """
    return _set_active(db, client_id, True)

def get_client(
        db: Session,
        client_id: int,
) -> Client:
    """
    Returns a specified client.
    Raises ClientNotFoundError if client doesn't exist.
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
    