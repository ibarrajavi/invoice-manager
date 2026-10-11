from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.clients import (
    AddressCreateRequest,
    AddressDefaultRequest,
    AddressDetailResponse,
    AddressUpdateRequest,
    ClientCreateRequest,
    ClientDetailResponse,
    ClientUpdateRequest,
)
from app.services import clients as client_service
from app.utils.database import get_db

router = APIRouter(prefix="/clients", tags=["clients"])

DbSession = Annotated[Session, Depends(get_db)]


# CLIENTS


@router.get("", response_model=list[ClientDetailResponse])
def list_clients(db: DbSession):
    return client_service.get_all_clients(db)


@router.post(
    "", response_model=ClientDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_client(body: ClientCreateRequest, db: DbSession):
    return client_service.create_client(db, **body.model_dump())


@router.get("/{client_id}", response_model=ClientDetailResponse)
def get_client(client_id: int, db: DbSession):
    return client_service.get_client(db, client_id)


@router.patch("/{client_id}", response_model=ClientDetailResponse)
def update_client(client_id: int, body: ClientUpdateRequest, db: DbSession):
    # Only fields the client actually sent, omitted ones stay UNSET in the service
    return client_service.update_client(
        db, client_id, **body.model_dump(exclude_unset=True)
    )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: DbSession) -> None:
    client_service.delete_client(db, client_id)


@router.post("/{client_id}/activate", response_model=ClientDetailResponse)
def activate_client(client_id: int, db: DbSession):
    return client_service.activate_client(db, client_id)


@router.post("/{client_id}/deactivate", response_model=ClientDetailResponse)
def deactivate_client(client_id: int, db: DbSession):
    return client_service.deactivate_client(db, client_id)


# ADDRESSES


@router.get("/{client_id}/addresses", response_model=list[AddressDetailResponse])
def list_addresses(client_id: int, db: DbSession):
    return client_service.get_all_addresses(db, client_id)


@router.post(
    "/{client_id}/addresses",
    response_model=AddressDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(client_id: int, body: AddressCreateRequest, db: DbSession):
    return client_service.create_address(db, client_id, **body.model_dump())


@router.get("/{client_id}/addresses/{address_id}", response_model=AddressDetailResponse)
def get_address(client_id: int, address_id: int, db: DbSession):
    return client_service.get_address(db, client_id, address_id)


@router.patch(
    "/{client_id}/addresses/{address_id}", response_model=AddressDetailResponse
)
def update_address(
    client_id: int, address_id: int, body: AddressUpdateRequest, db: DbSession
):
    return client_service.update_address(
        db, client_id, address_id, **body.model_dump(exclude_unset=True)
    )


@router.delete(
    "/{client_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_address(client_id: int, address_id: int, db: DbSession) -> None:
    client_service.delete_address(db, client_id, address_id)


@router.put(
    "/{client_id}/addresses/{address_id}/default",
    response_model=AddressDetailResponse,
)
def set_address_default(
    client_id: int, address_id: int, body: AddressDefaultRequest, db: DbSession
):
    return client_service.set_address_default(
        db, client_id, address_id, body.is_default
    )
