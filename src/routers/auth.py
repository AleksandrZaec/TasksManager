from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import decode_refresh_token
from src.services.user import users_crud
from src.utils.security import verify_password, create_access_token, create_refresh_token
from src.config.db import get_db
from fastapi import Body
from src.schemas import LoginRequest

router = APIRouter()


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Authenticate user and return a JWT access token."""
    user_data = await users_crud.get_for_login(db, data.email)
    if not user_data or not verify_password(data.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={
            "sub": str(user_data["id"]),
            "role": user_data["role"],
            "teams": user_data["teams"]
        }
    )

    refresh_token = create_refresh_token(
        data={
            "sub": str(user_data["id"]),
            "role": user_data["role"],
            "teams": user_data["teams"],
        }

    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)) -> dict[str, str]:
    """Issue new access token using refresh token."""
    try:
        token_data = await decode_refresh_token(refresh_token)
        new_access_token = create_access_token(
            data={
                "sub": str(token_data["user_id"]),
                "role": token_data["role"],
                "teams": token_data["teams"]
            }
        )

        return {"access_token": new_access_token, "token_type": "bearer"}

    except HTTPException:
        raise
