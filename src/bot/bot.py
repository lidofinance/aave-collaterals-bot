"""Anchor protocol collaterals monitoring bot"""

import logging
import time
from pprint import PrettyPrinter

import pandas as pd

from .aaveparser import parse
from .analytics import calculate_values
from .metrics import COLLATERALS_ZONES_PERCENT

S15MIN = 15 * 60


class AAVEBot:  # pylint: disable=too-few-public-methods
    """The main class of the Aave bot"""

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.pprint = PrettyPrinter(indent=4)

    def _fetch_block(self) -> None:
        self.log.info("Fetching has been started")

    def _compute_metrics(self, data: pd.DataFrame) -> None:
        values = calculate_values(data)
        for bin, stat in enumerate(values):  # pylint: disable=redefined-builtin
            for zone, percent in stat.items():
                COLLATERALS_ZONES_PERCENT.labels(zone, bin + 1).set(percent)
        self.log.debug("Metrics has been updated\n%s", self.pprint.pformat(values))

    @staticmethod
    def _settle() -> None:
        time.sleep(S15MIN)

    def run(self) -> None:
        """Main loop of bot"""

        while True:

            try:
                ledger = parse()
                self._compute_metrics(ledger)
            except Exception as ex:  # pylint: disable=broad-except
                self.log.error("An error occurred", exc_info=ex)

            self._settle()
