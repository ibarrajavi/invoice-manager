class AppError(Exception):
    """Base class for application specific exceptions."""


class RequiredFieldError(AppError):
    """Raised when a required field is blank or missing."""

    def __init__(self, field: str):
        self.field = field
        super().__init__(f"{field} is a required field.")


# CLIENT EXCEPTIONS


class ClientNotFoundError(AppError):
    """Raised when a client cannot be found by the given identifier."""

    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} not found.")


class ClientHasInvoicesError(AppError):
    """Raised when a client getting deleted has invoices."""

    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} has invoices.")


class ClientDeleteError(AppError):
    """Raised when a client could not be deleted."""

    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} could not be deleted.")


class ClientActiveStateError(AppError):
    """Raised when a client is already in the requested active state."""

    def __init__(self, client_id: int, active: bool):
        self.client_id = client_id
        self.active = active
        state = "active" if active else "inactive"
        super().__init__(f"Client {client_id} is already {state}.")


class ClientNameError(AppError):
    """Raised when a client getting created doesn't have a name."""

    def __init__(self):
        super().__init__("Client requires a first and last name or company name.")


class ClientEmailError(AppError):
    """Raised when a client email is taken."""

    def __init__(self, email: str | None):
        self.email = email
        super().__init__("Email address is already taken.")


class ClientStatusUpdateError(AppError):
    """Raised when a client active status could not be updated."""

    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Active status for client {client_id} could not be updated.")


# ADDRESS EXCEPTIONS


class AddressOperationError(AppError):
    """Base class for address errors. Raise a subclass, not this."""

    def __init__(self, client_id: int, message: str, address_id: int | None = None):
        self.address_id = address_id
        self.client_id = client_id
        super().__init__(message)


class AddressNotFoundError(AddressOperationError):
    """Raised when an address does not exist or belongs to a different client."""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id=address_id,
            client_id=client_id,
            message=f"Address {address_id} not found for client {client_id}.",
        )


class AddressDeleteError(AddressOperationError):
    """Raised when an address could not be deleted."""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id=address_id,
            client_id=client_id,
            message=f"Address {address_id} could not be deleted for client {client_id}.",
        )


class AddressInUseError(AddressOperationError):
    """Raised when an address cannot be deleted because it is still referenced."""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id=address_id,
            client_id=client_id,
            message=f"Address {address_id} is currently in use for client {client_id}.",
        )


class AddressDefaultError(AddressOperationError):
    """Raised when an address could not be set as the default"""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id=address_id,
            client_id=client_id,
            message=f"Address {address_id} could not be set as the default for client {client_id}.",
        )


class AddressConflictError(AddressOperationError):
    """Raised when an address create or update violates a database constraint."""

    def __init__(self, client_id: int, address_id: int | None = None):
        target = f"Address {address_id}" if address_id is not None else "New address"
        super().__init__(
            address_id=address_id,
            client_id=client_id,
            message=f"{target} for client {client_id} conflicts with an existing address.",
        )


# INVOICE EXCEPTIONS


class InvoiceNotFoundError(AppError):
    """Raised when an invoice cannot be found by the given identifier."""

    def __init__(self, invoice_id: int):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice {invoice_id} not found.")


class InvoiceNotDraftError(AppError):
    """Raised when a draft-only operation targets a non-draft invoice."""

    def __init__(self, invoice_id: int, status: str):
        self.invoice_id = invoice_id
        self.status = status
        super().__init__(f"Invoice {invoice_id} is {status}, not draft.")


class InvalidStatusTransitionError(AppError):
    """Raised when an invoice cannot move from its current status to the target."""

    def __init__(self, invoice_id: int, current: str, target: str):
        self.invoice_id = invoice_id
        self.current = current
        self.target = target
        super().__init__(
            f"Invoice {invoice_id} cannot change from {current} to {target}."
        )


class InvoiceAddressMismatchError(AppError):
    """Raised when an invoice's address does not belong to its client."""

    def __init__(self, address_id: int, client_id: int):
        self.address_id = address_id
        self.client_id = client_id
        super().__init__(f"Address {address_id} does not belong to client {client_id}.")


class InvoiceIssueError(AppError):
    """Raised when an invoice could not be issued."""

    def __init__(self, invoice_id: int):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice {invoice_id} could not be issued.")


# SETTINGS EXCEPTIONS


class InvalidNextInvoiceNumberError(AppError):
    """Raised when next_invoice_number would go below its current value after issuing."""

    def __init__(self, value: int, minimum: int):
        self.value = value
        self.minimum = minimum
        super().__init__(
            f"Next invoice number {value} is below the current value {minimum}. "
            "Lowering it after invoices are issued could reuse a number."
        )


class PdfStorageDirError(AppError):
    """Raised when the PDF storage folder is missing or not writable."""

    def __init__(self, path: str, reason: str):
        self.path = path
        super().__init__(f"PDF storage folder '{path}' {reason}.")


class SettingsUpdateError(AppError):
    """Raised when settings could not be saved."""

    def __init__(self):
        super().__init__("Settings could not be updated.")
