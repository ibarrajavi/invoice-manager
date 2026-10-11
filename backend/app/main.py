from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.v1.clients import router as clients_router
from app.api.v1.settings import router as settings_router
from app.utils.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables on startup (safe for existing tables)
    init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="invoice-manager API",
    version="1.0.0",
)

register_exception_handlers(app)
app.include_router(clients_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")

@app.get("/")
def app_health():
    return {"title": "invoice-manager", "status": "OK"}
