class AppError(Exception):
    """Base class for application specific exceptions."""


class RequiredFieldError(AppError):
    """Raised when a required field is blank or missing."""

    def __init__(self, field: str):
        self.field = field
        super().__init__(f"{field} is a required field.")


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


class AddressOperationError(AppError):
    """Base class for address errors. Raise a subclass, not this."""

    def __init__(self, address_id: int, client_id: int, message: str):
        self.address_id = address_id
        self.client_id = client_id
        super().__init__(message)


class AddressNotFoundError(AddressOperationError):
    """Raised when an address does not exist or belongs to a different client."""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id, client_id,
            f"Address {address_id} not found for client {client_id}.",
        )


class AddressDeleteError(AddressOperationError):
    """Raised when an address could not be deleted."""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id, client_id,
            f"Address {address_id} could not be deleted for client {client_id}.",
        )


class AddressInUseError(AddressOperationError):
    """Raised when an address cannot be deleted because it is still referenced."""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id, client_id,
            f"Address {address_id} is currently in use for client {client_id}.",
        )


class AddressDefaultError(AddressOperationError):
    """Raised when an address could not be set as the default"""

    def __init__(self, address_id: int, client_id: int):
        super().__init__(
            address_id, client_id,
            f"Address {address_id} could not be set as the default for client {client_id}."
        )
