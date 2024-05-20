from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore',
    )
    DISCORD_TOKEN: str

    DISCORD_ACTIVITY: str = 'with SQLModel'
    DISCORD_ACTIVITY_TYPE: Literal['playing', 'watching', 'listening', 'streaming'] = 'playing'
    DISCORD_STATUS: Literal['online', 'idle', 'dnd', 'invisible'] = 'online'

    ENVIRONMENT: Literal['local', 'production'] = 'local'

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = ''

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()  # type: ignore
