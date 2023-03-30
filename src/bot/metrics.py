"""Exporter metrics definitions"""
import json
import logging
import os
import platform as pf

from prometheus_client import Counter, Gauge, Histogram

log = logging.getLogger(__name__)

BUILD_INFO_PATH = "build-info.json"

PREFIX = "aave_bot"

COLLATERALS = Gauge(
    f"{PREFIX}_collaterals",
    "AAVE collaterals distribution",
    ("pair", "zone", "bin"),
)
PROCESSING_COMPLETED = Gauge(
    f"{PREFIX}_processing_finished_seconds",
    "Last one successful parsing cycle completion timestamp",
    ("pair",),
)
FETCH_DURATION = Gauge(
    f"{PREFIX}_fetch_duration",
    "Protocol fetching duration",
    ("pair",),
)
ETH_RPC_REQUESTS = Counter(
    f"{PREFIX}_eth_rpc_requests",
    "Total count of requests to ETH1 RPC",
    ("provider", "method", "code"),
)
ETH_RPC_REQUESTS_DURATION = Histogram(
    f"{PREFIX}_eth_rpc_requests_duration",
    "Duration of requests to ETH1 RPC",
    ("provider",),
)
APP_ERRORS = Counter(
    f"{PREFIX}_app_errors",
    "Errors count raised during app lifecycle",
    ("module",),
)

BUILD_INFO = Gauge(
    f"{PREFIX}_build_info",
    "Bot build info",
    ("pyversion", "version", "branch", "commit"),
)

NETWORK = Gauge(
    f"{PREFIX}_network",
    "Blockchain network info",
    ("name", "chain_id"),
)


def report_build_info() -> None:
    """Report _build_info metric"""

    labels = {
        "pyversion": ".".join(pf.python_version_tuple()),
        "version": "unknown",
        "branch": "unknown",
        "commit": "unknown",
    }

    if os.path.exists(BUILD_INFO_PATH):
        try:
            with open(BUILD_INFO_PATH, mode="r", encoding="utf-8") as f:
                info = json.load(f)
        except Exception as ex:  # pylint: disable=broad-except
            log.error("Unable to read build info file", exc_info=ex)
        else:
            if isinstance(info, dict):
                labels["version"] = info.get("version", labels["version"])
                labels["branch"] = info.get("branch", labels["branch"])
                labels["commit"] = info.get("commit", labels["commit"])

    BUILD_INFO.labels(**labels).set(1)
