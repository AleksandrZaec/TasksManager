from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login schema"""
    email: EmailStr
    password: str

    # class Config:
    #     extra = "forbid"