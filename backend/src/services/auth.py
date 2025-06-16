from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from backend.src.config.settings import settings
from fastapi import Depends, HTTPException, status

from backend.src.models import TeamRole
from backend.src.schemas.user import UserPayload, UserTeamInfo

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> UserPayload:
    print("\n--- get_current_user ---")
    print("RAW TOKEN:", token)
    """Decode JWT token and return current user's ID, role and team roles."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("\n--- JWT PAYLOAD START ---")
        print(token.credentials)
        print("--- JWT PAYLOAD END ---\n")
        token_str = token.credentials
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("PAYLOAD:", payload)
        if payload.get("token_type") == "refresh":
            print("Token is a refresh token, denying access")
            raise credentials_exception

        user_id = int(payload.get("sub"))
        role = payload.get("role")
        teams_data = payload.get("teams", [])

        if user_id is None or role is None:
            print("Missing user_id or role in token payload")
            raise credentials_exception

        teams = [UserTeamInfo(
            team_id=team["team_id"],
            role=TeamRole(team["role"])
        )
            for team in teams_data
        ]

        return UserPayload(id=user_id, role=role, teams=teams)

    except (JWTError, ValueError, TypeError, KeyError) as e:
        print(f"Unexpected error in get_current_user: {e}")
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

        return {
            "user_id": user_id,
            "role": user_role,
            "jti": token_jti,
            "teams": teams
        }

    except (JWTError, ValueError, TypeError) as e:
        raise credentials_exception
