import tempfile
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import (
    InvalidNextInvoiceNumberError,
    PdfStorageDirError,
    RequiredFieldError,
    SettingsUpdateError,
)
from app.models import AppSettings, Invoice
from app.utils.sentinel import UNSET, Unset
from app.utils.text import clean, clean_email

# Settings is a single row
SETTINGS_ID = 1


# HELPER FUNCTIONS


def _validate_pdf_storage_dir(value: str) -> str:
    """
    Return the absolute path if the folder exists and is writable.

    - Raises PdfStorageDirError if the folder is missing or not writable.
    """
    path = Path(value).expanduser()
    if not path.is_dir():
        raise PdfStorageDirError(value, "does not exist or is not a folder")

    # Writing a temp file is more reliable than os.access on Windows
    try:
        with tempfile.TemporaryFile(dir=path):
            pass
    except OSError as e:
        raise PdfStorageDirError(value, "is not writable") from e

    return str(path.resolve())


def _validate_next_invoice_number(
    db: Session,
    settings: AppSettings,
    value: int,
) -> None:
    """
    Allow any value until an invoice is issued, then only increases.

    - Raises InvalidNextInvoiceNumberError if lowering after issuing.
    """
    has_issued = db.scalar(
        select(Invoice.id).where(Invoice.invoice_no.is_not(None)).limit(1)
    )
    if has_issued and value < settings.next_invoice_number:
        raise InvalidNextInvoiceNumberError(value, settings.next_invoice_number)


# CORE SETTINGS FUNCTIONS


def get_settings(db: Session) -> AppSettings:
    """Return the app settings, creating the row with defaults if missing."""
    settings = db.get(AppSettings, SETTINGS_ID)
    if settings is None:
        settings = AppSettings(id=SETTINGS_ID)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(
    db: Session,
    *,
    invoice_prefix: str | None | Unset = UNSET,
    next_invoice_number: int | Unset = UNSET,
    pdf_storage_dir: str | None | Unset = UNSET,
    fname: str | None | Unset = UNSET,
    lname: str | None | Unset = UNSET,
    addr_line1: str | None | Unset = UNSET,
    addr_line2: str | None | Unset = UNSET,
    city: str | None | Unset = UNSET,
    state: str | None | Unset = UNSET,
    zip_code: str | None | Unset = UNSET,
    phone_num: str | None | Unset = UNSET,
    email: str | None | Unset = UNSET,
) -> AppSettings:
    """
    Update the app settings and commit.

    - Raises RequiredFieldError if next_invoice_number is null.
    - Raises InvalidNextInvoiceNumberError if lowering it after invoices are issued.
    - Raises PdfStorageDirError if the PDF folder is missing or not writable.
    - Raises SettingsUpdateError if the commit fails.
    """
    settings = get_settings(db)

    text_updates = {
        "invoice_prefix": invoice_prefix,
        "fname": fname,
        "lname": lname,
        "addr_line1": addr_line1,
        "addr_line2": addr_line2,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "phone_num": phone_num,
    }

    # Validate everything first so a failure leaves the object untouched
    changes = {
        field: clean(value)
        for field, value in text_updates.items()
        if value is not UNSET
    }

    if email is not UNSET:
        changes["email"] = clean_email(email)

    if pdf_storage_dir is not UNSET:
        cleaned = clean(pdf_storage_dir)
        changes["pdf_storage_dir"] = (
            _validate_pdf_storage_dir(cleaned) if cleaned else None
        )

    if next_invoice_number is not UNSET:
        # The schema allows an explicit null, which can't clear a NOT NULL column
        if next_invoice_number is None:
            raise RequiredFieldError("next_invoice_number")
        _validate_next_invoice_number(db, settings, next_invoice_number)
        changes["next_invoice_number"] = next_invoice_number

    for field, value in changes.items():
        setattr(settings, field, value)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise SettingsUpdateError() from e
    db.refresh(settings)
    return settings