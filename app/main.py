import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://fsae:fsae2026@timescaledb:5432/daq_data")

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = AsyncConnectionPool(conninfo=DATABASE_URL, min_size=1, max_size=10, open=False)
    await pool.open(wait=True, timeout=30)
    app.state.pool = pool
    yield
    await pool.close()

app = FastAPI(title="LSU FSAE DAQ API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/health")
async def health(request: Request):
    async with request.app.state.pool.connection() as conn:
        await conn.execute("SELECT 1")
    return {"status": "healthy"}
