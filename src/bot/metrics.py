"""Exporter metrics definitions"""

import platform as pf

from prometheus_client import Counter, Gauge, Histogram

PREFIX = "aave_bot"

COLLATERALS_ZONES_PERCENT = Gauge(
    f"{PREFIX}_collateral_percentage",
    "AAVE collaterals percentage distribution",
    ("zone", "bin"),
)
FETCH_DURATION = Gauge(
    f"{PREFIX}_fetch_duration",
    "Protocol fetching duration",
)
ETH_RPC_REQUESTS = Counter(
    f"{PREFIX}_eth_rpc_requests",
    "Total count of requests to ETH1 RPC",
    ("method", "code"),
)
ETH_RPC_REQUESTS_DURATION = Histogram(
    f"{PREFIX}_eth_rpc_requests_duration",
    "Duration of requests to ETH1 RPC",
)
APP_ERRORS = Counter(
    f"{PREFIX}_app_errors",
    "Errors count raised during app lifecycle",
    ("module",),
)
HTTP_REQUESTS_DURATION = Histogram(
    f"{PREFIX}_http_requests_duration",
    "Duration of HTTP requests",
    ("domain", "path", "method"),
)
HTTP_REQUESTS = Counter(
    f"{PREFIX}_http_requests",
    "Total count of HTTP requests",
    ("domain", "path", "method", "http_code"),
)

BUILD_INFO = Gauge(
    f"{PREFIX}_build_info",
    "Bot build info",
    ("pyversion",),
)


def report_build_info() -> None:
    """Report _build_info metric"""

    pyversion = ".".join(pf.python_version_tuple())
    BUILD_INFO.labels(
        pyversion=pyversion,
    ).set(1)
