from fastapi import FastAPI
import asyncpg
from typing import Optional

DATABASE_URL = "postgresql://postgres:2806@localhost/project_quartzline"

# Глобальная переменная для пула подключений к базе данных (инициализируется при запуске приложения)
pool: Optional[asyncpg.Pool] = None

# Псевдоним для доступа к пулу — используется для совместимости с импортами (костыль, скорее всего пизды получу)
database = pool

async def setup_db():
    global pool
    if not pool:
        pool = await asyncpg.create_pool(dsn=DATABASE_URL)

async def close_db():
    global pool
    if pool:
        await pool.close()
async def connect_to_db():
    return await asyncpg.connect(DATABASE_URL)

async def disconnect_from_db(conn):
    await conn.close()
