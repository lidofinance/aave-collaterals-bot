"""Anchor protocol collaterals monitoring bot"""

import logging
import time
from pprint import PrettyPrinter

import pandas as pd

from aaveparser import parse
from analytics import calculate_values
from metrics import COLLATERALS_ZONES_PERCENT

S15MIN = 15 * 60


class AAVEBot:
    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.pp = PrettyPrinter(indent=4)

    def _fetch_block(self) -> None:
        self.log.info("Fetching has been started")

    def _compute_metrics(self, data: pd.DataFrame) -> None:
        values = calculate_values(data)
        for bin, stat in enumerate(values):
            for zone, percent in stat.items():
                COLLATERALS_ZONES_PERCENT.labels(zone, bin + 1).set(percent)
        self.log.debug(f"Metrics has been updated\n{self.pp.pformat(values)}")

    def _settle(self) -> None:
        time.sleep(S15MIN)

    def run(self) -> None:
        """Main loop of bot"""

        while True:

            try:
                ledger = parse()
                self._compute_metrics(ledger)
            except Exception as ex:
                self.log.error("An error occured", exc_info=ex)

            self._settle()
