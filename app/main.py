from fastapi import FastAPI
from app.db import setup_db, close_db
from app.users.routers import router as users_router

app = FastAPI()


# Подключение к базе при запуске
@app.on_event("startup")
async def startup():
    await setup_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Project QUARTZLINE backend is running!"}

app.include_router(users_router)