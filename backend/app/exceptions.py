class AppError(Exception):
    """Base class for application specific exceptions."""

class ClientNotFoundError(AppError):
    """Raised when a client cannot be found by the given identifier."""
    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} not found")

class ClientHasInvoicesError(AppError):
    """Raised when a client getting deleted has invoices."""
    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} has invoices")

class ClientDeleteError(AppError):
    """Raised when a client could not be deleted."""
    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} could not be deleted")

class ClientActiveStateError(AppError):
    """Raised when a client is already in the requested active state."""
    def __init__(self, client_id: int, active: bool):
        self.client_id = client_id
        self.active = active
        super().__init__(f"Client {client_id} is already {'active' if active else 'inactive'}.")

class ClientNameError(AppError):
    """Raised when a client getting created doesn't have a name."""
    def __init__(self):
        super().__init__("Client requires a name or company name")

class ClientEmailError(AppError):
    """Raised when a client email is taken."""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email address is already taken.")

class ClientStatusUpdateError(AppError):
    """Raised when a client active status could not be updated."""
    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Active status for client {client_id} could not be updated")
