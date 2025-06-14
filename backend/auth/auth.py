from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from backend.config.settings import settings
from fastapi import Depends, HTTPException, status

from backend.models import TeamRole
from backend.schemas.user import UserPayload, UserTeamInfo

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> UserPayload:
    """Decode JWT token and return current user's ID, role and team roles."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_str = token.credentials
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("token_type") == "refresh":
            raise credentials_exception

        user_id = int(payload.get("sub"))
        role = payload.get("role")
        teams_data = payload.get("teams", [])

        if user_id is None or role is None:
            raise credentials_exception

        teams = [UserTeamInfo(
            team_id=team["team_id"],
            role=TeamRole(team["role"])
        )
            for team in teams_data
        ]

        user_payload = UserPayload(id=user_id, role=role, teams=teams)
        return user_payload

    except (JWTError, ValueError, TypeError, KeyError) as e:
        raise credentials_exception


async def decode_refresh_token(refresh_token: str) -> dict:
    """Decode and validate refresh token, return full payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if not all(key in payload for key in ["sub", "role", "jti", "teams"]):
            raise credentials_exception

        user_id = int(payload["sub"])
        user_role = payload["role"]
        token_jti = payload["jti"]
        teams = payload["teams"]

        token_data = {
            "user_id": user_id,
            "role": user_role,
            "jti": token_jti,
            "teams": teams
        }
        return token_data

    except (JWTError, ValueError, TypeError) as e:
        raise credentials_exception
