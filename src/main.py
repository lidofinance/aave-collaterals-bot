"""Prometheus exporter of metrics collected from aggregated Anchor protocol data"""

import logging

from prometheus_client import start_http_server

from bot import AAVEBot
from bot.config import EXPORTER_PORT
from bot.metrics import report_build_info

log = logging.getLogger(__name__)


if __name__ == "__main__":
    log.info("Starting prometheus exporter server on port %s", EXPORTER_PORT)
    start_http_server(EXPORTER_PORT)
    report_build_info()
    bot = AAVEBot()
    bot.run()
