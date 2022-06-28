"""Anchor protocol collaterals monitoring bot"""

import logging
import time
from pprint import PrettyPrinter

import pandas as pd
from web3.types import BlockIdentifier

from .aaveparser import parse
from .analytics import calculate_values
from .config import PARSE_INTERVAL
from .metrics import APP_ERRORS, COLLATERALS_ZONES_PERCENT, FETCH_DURATION


class AAVEBot:  # pylint: disable=too-few-public-methods
    """The main class of the Aave bot"""

    def __init__(self) -> None:
        self.block: int | None = None
        self.log = logging.getLogger(__name__)
        self.pprint = PrettyPrinter(indent=4)

    def _compute_metrics(self, data: pd.DataFrame, block: BlockIdentifier) -> None:
        with APP_ERRORS.labels("calculations").count_exceptions():
            values = calculate_values(data, block)
        for bin, stat in enumerate(values):  # pylint: disable=redefined-builtin
            for zone, percent in stat.items():
                COLLATERALS_ZONES_PERCENT.labels(zone, bin + 1).set(percent)
        self.log.debug("Metrics has been updated\n%s", self.pprint.pformat(values))
        self.log.info("Fetching complete")

    def _settle(self) -> None:
        self.log.info("Wait for %d seconds for the next fetch", PARSE_INTERVAL)
        time.sleep(PARSE_INTERVAL)

    def run(self) -> None:
        """Main loop of bot"""

        while True:

            try:
                with FETCH_DURATION.time():
                    with APP_ERRORS.labels("fetching").count_exceptions():
                        self.block, ledger = parse(self.block)
                self._compute_metrics(ledger, self.block)
            except Exception as ex:  # pylint: disable=broad-except
                self.log.error("An error occurred", exc_info=ex)

            self._settle()
