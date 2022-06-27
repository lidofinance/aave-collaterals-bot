"""Module for parsing data from Anchor protocol contracts"""

import logging
import time
from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd
from unsync import unsync
from web3.types import BlockData, BlockIdentifier

from .config import FLIPSIDE_ENDPOINT
from .eth import AAVE_LPOOL, AAVE_ORACLE, AAVE_WETH_STABLE_DEBT, AAVE_WETH_VAR_DEBT, ASTETH, w3
from .http import requests_get

log = logging.getLogger(__name__)

LIDO_STETH = w3.toChecksumAddress("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")
MS_3_MIN = 3 * 60 * 1000


def get_steth_eth_price() -> int:
    """Get the price of stETH in ETH from AAVE protocol"""

    return AAVE_ORACLE.functions.getAssetPrice(LIDO_STETH).call()


@dataclass
class CoinGeckoPriceRequestParams:
    """Payload for request to /simple/price
    @see https://www.coingecko.com/en/api/documentation for details."""

    ids: str
    vs_currencies: str = "usd"
    include_market_cap: str = "false"
    include_24hr_vol: str = "false"
    include_24hr_change: str = "false"
    include_last_updated_at: str = "false"


@dataclass
class CoinGeckoChartRequestParams:
    """Payload for request to /coins/{id}/market_chart
    @see https://www.coingecko.com/en/api/documentation for details."""

    vs_currency: str = "usd"
    days: int = 1


def _crypto_to_usd(currency: str, timestamp_ns: int) -> float:

    unix_ts = timestamp_ns // pow(10, 6)  # will be block.timestamp soon
    payload = CoinGeckoChartRequestParams()
    response = requests_get(
        url=f"https://api.coingecko.com/api/v3/coins/{currency}/market_chart",
        params=asdict(payload),
        timeout=5,
    )
    response.raise_for_status()
    prices = [(ts, price) for ts, price in response.json()["prices"] if ts <= unix_ts]
    if not prices:
        raise Exception("No price information within the given timestamp")
    prices.sort(key=lambda x: x[0])  # sort by ts
    ts, price = prices[-1]
    if unix_ts - ts > MS_3_MIN:
        raise Exception(f"Stale price data, last available {ts=}")
    return price


def eth_last_price() -> float:
    """Current price of ETH"""

    return _crypto_to_usd("ethereum", time.time_ns())


def steth_last_price() -> float:
    """Current price of stETH"""

    return _crypto_to_usd("staked-ether", time.time_ns())


@dataclass
class LendingPoolResponse:
    """Response from AAVE Lending Pool contract getUserAccountData endpoint"""

    collateral_eth: int
    debt_eth: int
    available_borrows_eth: int
    current_liquidation_threshold: int
    ltv: int
    healthfactor: int


@unsync
def get_user_stats(user: str, block: BlockIdentifier = "latest") -> LendingPoolResponse:
    """Parse user stat from AAVE Lending Pool"""

    address = w3.toChecksumAddress(user)
    result = AAVE_LPOOL.functions.getUserAccountData(address).call(block_identifier=block)
    return LendingPoolResponse(*result)


@unsync
def get_asteth_balance(user: str, block: BlockIdentifier = "latest") -> float:
    """Get user's astETH balance"""

    address = w3.toChecksumAddress(user)
    return ASTETH.functions.balanceOf(address).call(block_identifier=block)


@unsync
def get_eth_debt(user: str, block: BlockIdentifier) -> float:
    """Get balance of user from AAVE tokens contracts"""

    address = w3.toChecksumAddress(user)
    return sum(
        (
            AAVE_WETH_STABLE_DEBT.functions.balanceOf(address).call(block_identifier=block),
            AAVE_WETH_VAR_DEBT.functions.balanceOf(address).call(block_identifier=block),
        )
    )


def get_userlist() -> Iterable:
    """Get the list of borrowers.
    NB! It's subject to change!"""

    response = requests_get(url=FLIPSIDE_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()


def get_latest_block() -> BlockData:
    """Get the latest ETH block"""

    return w3.eth.get_block("latest")


def parse() -> pd.DataFrame:
    """Parse required data"""

    latest_block = get_latest_block()
    block_number = latest_block["number"]  # type: ignore
    log.info("Parse started at block %d", block_number)

    # will be changed to parsing from the blockchain
    df = pd.DataFrame(get_userlist())
    df = df[["user"]]
    df.set_index("user")

    @unsync
    def _parse_stats():

        buf = []
        tasks = [(user, get_user_stats(user, block_number)) for user in df["user"]]
        for user, task in tasks:
            stat: LendingPoolResponse = task.result()  # type: ignore
            buf.append(
                {
                    "user": user,
                    "collateral": stat.collateral_eth,
                    "debt": stat.debt_eth,
                    "available_borrow": stat.available_borrows_eth,
                    "threshold": stat.current_liquidation_threshold,
                    "ltv": stat.ltv,
                    "healthf": stat.healthfactor,
                }
            )
        return buf

    @unsync
    def _parse_balance():

        buf = []
        tasks = [(user, get_asteth_balance(user, block_number)) for user in df["user"]]
        for user, task in tasks:
            balance: float = task.result()  # type: ignore
            buf.append({"user": user, "amount": balance})
        return buf

    @unsync
    def _parse_eth_debth():

        buf = []
        tasks = [(user, get_eth_debt(user, block_number)) for user in df["user"]]
        for user, task in tasks:
            balance: float = task.result()  # type: ignore
            buf.append({"user": user, "ethdebt": balance})
        return buf

    tasks = [_parse_stats(), _parse_balance(), _parse_eth_debth()]
    parts = [pd.DataFrame(task.result()) for task in tasks]  # type: ignore # pylint: disable=no-member

    for part in parts:
        df = df.merge(part, on="user", how="left")

    return df
