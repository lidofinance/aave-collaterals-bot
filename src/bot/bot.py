"""Anchor protocol collaterals monitoring bot"""

import logging
import time
from pprint import PrettyPrinter

import pandas as pd

from .aaveparser import fetch
from .analytics import get_zones_values
from .config import MAIN_ERROR_COOLDOWN, PARSE_INTERVAL
from .eth import w3
from .metrics import APP_ERRORS, COLLATERALS, FETCH_DURATION, PROCESSING_COMPLETED
from .worker import Worker, arbwstETH, astETH, awstETH, polStMATIC


class AAVEBot:  # pylint: disable=too-few-public-methods
    """The main class of the Aave bot"""

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.pprint = PrettyPrinter(indent=4)
        self.chain_id = w3.eth.chain_id

        # List all workers to process
        # NB! less holders first to decrease of the number of requests of error
        self.workers = (
            arbwstETH,
            awstETH,
            polStMATIC,
            astETH,
        )

    def run(self) -> None:
        """Main loop of bot"""

        self.log.info("Running on chain ID %s", self.chain_id)
        while True:
            try:
                for w in self.workers:
                    if w.pair.chain_id == self.chain_id:
                        self._run_worker(w)
            except Exception as ex:  # pylint: disable=broad-except
                self._on_error(ex)
            else:
                self._on_success()

    def _run_worker(self, w: Worker) -> None:
        df = self._fetch(w)
        if df is not None:
            self._compute_metrics(df, w)
        PROCESSING_COMPLETED.labels(w.pair.name).set_to_current_time()

    @staticmethod
    def _fetch(w: Worker) -> pd.DataFrame | None:
        with FETCH_DURATION.labels(w.pair.name).time():
            with APP_ERRORS.labels("aaveparser").count_exceptions():
                return fetch(w.ctx, w.pair)

    def _compute_metrics(self, df: pd.DataFrame, w: Worker) -> None:
        for idx, bin_ in enumerate(w.bins):
            with APP_ERRORS.labels("analytics").count_exceptions():
                values = get_zones_values(df, bin_)
            for zone, v in values.items():
                COLLATERALS.labels(w.pair.name, zone, idx + 1).set(v)

            bin_alias = f"{w.pair.name}-{idx + 1}"
            self.log.info("Bin %s distribution:\n%s", bin_alias, self.pprint.pformat(values))
            self.log.info("Total amount locked in bin %s: %d", bin_alias, sum(values.values()))

    def _on_error(self, ex: Exception) -> None:
        self.log.error("An error occurred", exc_info=ex)
        self.log.warning("Wait for %d seconds before the next try", MAIN_ERROR_COOLDOWN)
        time.sleep(MAIN_ERROR_COOLDOWN)

    def _on_success(self) -> None:
        self.log.info("Wait for %d seconds for the next fetch", PARSE_INTERVAL)
        time.sleep(PARSE_INTERVAL)
