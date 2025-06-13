from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from backend.config.settings import settings
from uuid import uuid4

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
