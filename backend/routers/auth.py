from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.auth.auth import decode_refresh_token
from backend.auth.security import verify_password, create_access_token, create_refresh_token
from backend.config.db import get_db
from backend.crud.user import UserCRUD
from fastapi import Body
from backend.schemas.auth import LoginRequest

router = APIRouter()


@router.post("/login")
async def login(
        data: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Authenticate user and return a JWT access token."""
    user_data = await UserCRUD.get_for_login(db, data.email)
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

    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    return response_data


@router.post("/refresh")
async def refresh_token(
        refresh_token: str = Body(..., embed=True),
) -> dict[str, str]:
    """Issue new access token using refresh token."""
    try:
        token_data = await decode_refresh_token(refresh_token)
        new_access_token = create_access_token(
            data={
                "sub": token_data["user_id"],
                "role": token_data["role"],
                "teams": token_data["teams"]
            }
        )

        response_data = {"access_token": new_access_token, "token_type": "bearer"}
        return response_data

    except HTTPException:
        raise
