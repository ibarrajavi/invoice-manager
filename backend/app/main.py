from fastapi import FastAPI
from contextlib import asynccontextmanager

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

@app.get("/")
def app_health():
    return {
        "title": "invoice-manager",
        "status": "OK"
    }

