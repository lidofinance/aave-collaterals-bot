"""Configurable constants here"""

import logging
import os
from typing import Any, Type, TypeAlias

logging.basicConfig(level=logging.INFO, handlers=(logging.StreamHandler(),))
log = logging.getLogger(__name__)

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

INFURA_ENDPOINT = getenv("INFURA_ENDPOINT", required=True)
if "wss://" in INFURA_ENDPOINT:
    # WSS provider seems to be broken in python 3.10 and
    # doesn't work in the current flow. Magic asyncio fails happen.
    raise RuntimeError("Only http[s] Web3 provider endpoint supported")

# === Optional ===

FLIPSIDE_ENDPOINT = getenv(
    "FLIPSIDE_ENDPOINT",
    default="https://api.flipsidecrypto.com/api/v2/" "queries/efc8d01b-60c1-4051-9548-2a6daff256a8/data/latest",
)
EXPORTER_PORT = getenv("EXPORTER_PORT", int, default=8080)
