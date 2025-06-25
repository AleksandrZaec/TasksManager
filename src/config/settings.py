from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    MODE: str

    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @property
    def DB_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
