"""Environment-backed backend configuration."""

import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class _NoArg:
    pass


NO_ARG: Final = _NoArg()


def get_env_var(key: str, default: str | _NoArg = NO_ARG) -> str:
    """Return an environment value or raise when a required value is absent."""
    value = os.getenv(key)
    if value is not None:
        return value
    if isinstance(default, _NoArg):
        raise KeyError(f"Environment variable {key} is missing")
    return default


DATABASE_URL: Final[str] = get_env_var("DATABASE_URL")
ENV: Final[str] = get_env_var("ENV", "dev")
JWT_ACCESS_SECRET: Final[str] = get_env_var("JWT_ACCESS_SECRET")
JWT_REFRESH_SECRET: Final[str] = get_env_var("JWT_REFRESH_SECRET")
JWT_ALGORITHM: Final[str] = get_env_var("JWT_ALGORITHM", "HS256")
