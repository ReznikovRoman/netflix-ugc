from functools import lru_cache
from typing import Union

from pydantic import AnyHttpUrl, Field, validator
from pydantic.env_settings import BaseSettings


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class Settings(BaseSettings):
    """Настройки проекта."""

    # Project
    PROJECT_BASE_URL: str
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str | None = Field(None, env="NAA_SERVER_NAME")
    SERVER_HOSTS: Union[str, list[AnyHttpUrl]]
    PROJECT_NAME: str
    DEBUG: bool = Field(False)

    # Logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "loggers": {
            "asyncio": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "ugc": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    class Config(EnvConfig):
        env_prefix = "NUGC_"
        case_sensitive = True

    @validator("SERVER_HOSTS", pre=True)
    def _assemble_server_hosts(cls, server_hosts):
        if isinstance(server_hosts, str):
            return [item.strip() for item in server_hosts.split(",")]
        return server_hosts


@lru_cache()
def get_settings() -> "Settings":
    return Settings()