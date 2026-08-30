import os
from typing import Final

from dotenv import load_dotenv


load_dotenv()


class _NoArg:
    pass


NO_ARG: Final = _NoArg()


def get_env_var(key: str, default: str | _NoArg = NO_ARG) -> str:
    try:
        return os.environ[key]
    except KeyError as exception:
        if isinstance(default, _NoArg):
            raise ValueError(f"Environment variable {key} is missing") from exception
        return default


DATABASE_URL: Final[str] = get_env_var("DATABASE_URL")
