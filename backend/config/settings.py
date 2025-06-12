from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    MODE: str

    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
