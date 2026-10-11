from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    AddressConflictError,
    AddressDefaultError,
    AddressDeleteError,
    AddressInUseError,
    AddressNotFoundError,
    AppError,
    ClientActiveStateError,
    ClientDeleteError,
    ClientEmailError,
    ClientHasInvoicesError,
    ClientNameError,
    ClientNotFoundError,
    ClientStatusUpdateError,
    InvalidStatusTransitionError,
    InvoiceAddressMismatchError,
    InvoiceIssueError,
    InvoiceNotDraftError,
    InvoiceNotFoundError,
    RequiredFieldError,
)

STATUS_CODES: dict[type[AppError], int] = {
    # NOT FOUND
    ClientNotFoundError: 404,
    AddressNotFoundError: 404,
    InvoiceNotFoundError: 404,
    # CONFLICT
    ClientEmailError: 409,
    ClientHasInvoicesError: 409,
    ClientActiveStateError: 409,
    AddressInUseError: 409,
    AddressDefaultError: 409,
    AddressConflictError: 409,
    InvoiceNotDraftError: 409,
    InvalidStatusTransitionError: 409,
    # UNPROCESSABLE CONTENT
    ClientNameError: 422,
    RequiredFieldError: 422,
    InvoiceAddressMismatchError: 422,
    # INTERNAL SERVER ERROR
    ClientDeleteError: 500,
    ClientStatusUpdateError: 500,
    AddressDeleteError: 500,
    InvoiceIssueError: 500,
}


def _status_for(exc: AppError) -> int:
    for cls in type(exc).__mro__:
        if cls in STATUS_CODES:
            return STATUS_CODES[cls]
    return 500


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=_status_for(exc), content={"detail": str(exc)})
