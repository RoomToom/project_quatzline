from fastapi import APIRouter, HTTPException
from app import db
from app.utils.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from datetime import timedelta
from app.utils.security import get_current_user_id
from fastapi import Depends
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from app.utils.security import decode_token

router = APIRouter()


# ----- Схемы запросов -----

# Модель для запроса регистрации
class RegisterRequest(BaseModel):
    login: str
    password: str
    riot_id_name: str
    riot_id_tag: str


# Модель для запроса логина
class LoginRequest(BaseModel):
    login: str
    password: str


# Модель ответа с JWT токеном
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ----- Эндпоинт: Регистрация -----
@router.post("/register")
async def register_user(data: RegisterRequest):
    existing_user = await db.pool.fetchrow("SELECT id FROM users WHERE login = $1", data.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

    hashed_password = hash_password(data.password)

    await db.pool.execute(
        """
        INSERT INTO users (login, password_hash, riot_id_name, riot_id_tag, created_at)
        VALUES ($1, $2, $3, $4, NOW())
        """,
        data.login, hashed_password, data.riot_id_name, data.riot_id_tag
    )

    return {"message": "Регистрация успешна"}


# ----- Эндпоинт: Логин -----
@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginRequest):
    if not db.pool:
        raise HTTPException(status_code=500, detail="POOL IS NONE!")

    user = await db.pool.fetchrow("SELECT id, password_hash FROM users WHERE login = $1", data.login)

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}


# ----- Эндпоинт: get token ----- (получение данных текущего пользователя по токену)
@router.get("/me")
async def get_my_profile(user_id: int = Depends(get_current_user_id)):
    user = await db.pool.fetchrow("SELECT id, login, riot_id_name, riot_id_tag FROM users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователя не найдено")

    return dict(user)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user = await db.pool.fetchrow(
        "SELECT id, login, riot_id_name, riot_id_tag FROM users WHERE id = $1",
        int(user_id)
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователя не найдено")

    return user