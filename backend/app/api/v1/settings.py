from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.app_settings import (
    AppSettingsDetailResponse,
    AppSettingsUpdateRequest,
)
from app.services import app_settings as settings_service
from app.utils.database import get_db

router = APIRouter(prefix="/settings", tags=["settings"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=AppSettingsDetailResponse)
def get_settings(db: DbSession):
    return settings_service.get_settings(db)


@router.patch("", response_model=AppSettingsDetailResponse)
def update_settings(body: AppSettingsUpdateRequest, db: DbSession):
    return settings_service.update_settings(
        db, **body.model_dump(exclude_unset=True)
    )