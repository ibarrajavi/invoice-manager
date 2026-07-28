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

class ClientDeactivateError(AppError):
    """Raised when a client is already inactive."""
    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client {client_id} is already inactive")

class ClientNameError(AppError):
    """Raised when a client getting created doesn't have a name."""
    def __init__(self):
        super().__init__("Client requires a name or company name")

class ClientEmailError(AppError):
    """Raised when a client email is taken."""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email address is already taken.")

