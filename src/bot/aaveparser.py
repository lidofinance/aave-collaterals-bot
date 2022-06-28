"""Module for parsing data from Anchor protocol contracts"""

import logging
from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd
from retry import retry
from unsync import unsync
from web3.types import BlockData, BlockIdentifier

from .config import FLIPSIDE_ENDPOINT
from .consts import AAVE_FIRST_BLOCK, DECIMALS_ASTETH, HTTP_REQUESTS_DELAY, HTTP_REQUESTS_RETRY, LIDO_STETH, MS_3_MIN
from .eth import AAVE_LPOOL, AAVE_ORACLE, AAVE_WETH_STABLE_DEBT, AAVE_WETH_VAR_DEBT, ASTETH, w3
from .http import requests_get

log = logging.getLogger(__name__)

ASTETH_HOLDERS = set()  # cache for hodlers


def get_steth_eth_price(block: BlockIdentifier) -> int:
    """Get the price of stETH in ETH from AAVE protocol"""

    return AAVE_ORACLE.functions.getAssetPrice(LIDO_STETH).call(block_identifier=block)


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


def _crypto_to_usd(currency: str, block: BlockIdentifier) -> float:

    block_ts = get_block_info(block)["timestamp"] * 1000  # type: ignore
    payload = CoinGeckoChartRequestParams()
    response = requests_get(
        url=f"https://api.coingecko.com/api/v3/coins/{currency}/market_chart",
        params=asdict(payload),
        timeout=5,
    )
    response.raise_for_status()
    prices = [(ts, price) for ts, price in response.json()["prices"] if ts <= block_ts]
    if not prices:
        raise Exception("No price information within the given timestamp")
    prices.sort(key=lambda x: x[0])  # sort by ts
    ts, price = prices[-1]
    if block_ts - ts > MS_3_MIN:
        raise Exception(f"Stale price data, last available {ts=}")
    return price


@retry(tries=HTTP_REQUESTS_RETRY, delay=HTTP_REQUESTS_DELAY)
def eth_price(block: BlockIdentifier = "latest") -> float:
    """Current price of ETH"""

    return _crypto_to_usd("ethereum", block)


@retry(tries=HTTP_REQUESTS_RETRY, delay=HTTP_REQUESTS_DELAY)
def steth_price(block: BlockIdentifier = "latest") -> float:
    """Current price of stETH"""

    return _crypto_to_usd("staked-ether", block)


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


def get_block_info(block: BlockIdentifier) -> BlockData:
    """Get the given block information"""

    return w3.eth.get_block(block)


def get_latest_block() -> int:
    """Get the latest ETH block number"""

    return w3.eth.block_number


def fetch_asteth_holders(start_block: int, last_block: int) -> list[dict]:
    """Fetch astETH holders from ETH"""

    res = []

    log.info("Fetching astETH holders within the blocks range %d,%d", start_block, last_block)
    batch_size = 100000
    block = start_block
    while block <= last_block:
        events = ASTETH.events.Mint.getLogs(fromBlock=block, toBlock=block + batch_size)
        for event in events:  # store new minters
            holder = event["args"]["from"]
            ASTETH_HOLDERS.add(holder)
        block += batch_size

    tasks = [(holder, get_asteth_balance(holder, last_block)) for holder in ASTETH_HOLDERS]
    threshold = pow(10, DECIMALS_ASTETH) // 10  # 0.1
    for holder, task in tasks:
        balance = task.result()  # type: ignore
        if balance <= threshold:
            ASTETH_HOLDERS.remove(holder)
            continue
        res.append({"user": holder, "amount": balance})

    log.info("Found %d holders with non-zero balance", len(res))
    return res


def parse(start_block: int | None = None) -> tuple[int, pd.DataFrame]:
    """Parse required data"""

    latest_block = get_latest_block()
    if latest_block == start_block:
        raise Exception(f"Block {start_block} has been already read")

    log.info("Fetching data at the block %d", latest_block)
    start_block = start_block or AAVE_FIRST_BLOCK
    users = fetch_asteth_holders(start_block, latest_block)

    df = pd.DataFrame(users)
    df.set_index("user")

    @unsync
    def _parse_stats():

        buf = []
        tasks = [(user, get_user_stats(user, latest_block)) for user in df["user"]]
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
    def _parse_eth_debth():

        buf = []
        tasks = [(user, get_eth_debt(user, latest_block)) for user in df["user"]]
        for user, task in tasks:
            debt: float = task.result()  # type: ignore
            buf.append({"user": user, "ethdebt": debt})
        return buf

    tasks = [_parse_stats(), _parse_eth_debth()]
    parts = [pd.DataFrame(task.result()) for task in tasks]  # type: ignore # pylint: disable=no-member

    for part in parts:
        df = df.merge(part, on="user", how="left")

    return latest_block, df
