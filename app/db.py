from fastapi import FastAPI
import asyncpg
from typing import Optional

DATABASE_URL = "postgresql://postgres:2806@localhost/project_quartzline"

pool: Optional[asyncpg.Pool] = None

database = pool

async def setup_db():
    global pool
    pool = await asyncpg.create_pool(dsn=DATABASE_URL)

async def close_db():
    global pool
    await pool.close()


async def connect_to_db():
    return await asyncpg.connect(DATABASE_URL)

async def disconnect_from_db(conn):
    await conn.close()
