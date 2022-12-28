"""Configurable constants here"""

import logging
import os
from typing import Any, Type, TypeAlias

logging_handler = logging.StreamHandler()

if os.getenv("LOG_FORMAT", "simple") == "json":
    from pythonjsonlogger import jsonlogger

    formatter = jsonlogger.JsonFormatter("%(asctime)%(levelname)%(name)%(message)")
    logging_handler.setFormatter(formatter)

LOG_LEVEL_DEFAULT = logging.INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.getLevelName(LOG_LEVEL_DEFAULT))
LOG_LEVEL_IS_VALID = getattr(logging, LOG_LEVEL, None) is not None

logging.basicConfig(
    level=LOG_LEVEL if LOG_LEVEL_IS_VALID else LOG_LEVEL_DEFAULT,
    handlers=(logging_handler,),
)
log = logging.getLogger(__name__)

if not LOG_LEVEL_IS_VALID:
    log.warning(
        "%s was not recognized, defaults to %s",
        f"{LOG_LEVEL=}",
        logging.getLevelName(LOG_LEVEL_DEFAULT),
    )

T: TypeAlias = Any
D = object()  # sentinel


def getenv(name: str, astype: Type[T] = str, default: T = D, required: bool = False) -> T:
    """Get environment variable in failsafe manner"""

    if required and default is not D:
        raise ValueError("Unable to parse environment variable with both required and default")

    if required and name not in os.environ:
        raise RuntimeError(f"{name} environment variable is required")

    if name in os.environ:
        try:
            return astype(os.getenv(name))
        except (TypeError, ValueError) as ex:
            log.warning(
                "Failed to parse %s environment variable, fallback to %s",
                name,
                f"{default=}",
                exc_info=ex,
            )

    return default


# === Required ===

NODE_ENDPOINT = getenv("NODE_ENDPOINT", required=True)
if "wss://" in NODE_ENDPOINT:
    # WSS provider seems to be broken in python 3.10 and
    # doesn't work in the current flow. Magic asyncio fails happen.
    raise RuntimeError("Only http[s] Web3 provider endpoint supported")

# === Optional ===

FALLBACK_NODE_ENDPOINT = getenv("FALLBACK_NODE_ENDPOINT", str, default="")
MAIN_ERROR_COOLDOWN = getenv("MAIN_ERROR_COOLDOWN", int, default=15)
PARSE_INTERVAL = getenv("PARSE_INTERVAL", int, default=2700)
EXPORTER_PORT = getenv("EXPORTER_PORT", int, default=8080)
