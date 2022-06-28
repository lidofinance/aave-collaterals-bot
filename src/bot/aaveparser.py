"""Module for parsing data from Anchor protocol contracts"""

import logging
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from eth_typing.encoding import HexStr
from unsync import unsync
from web3.types import BlockData, BlockIdentifier

from .config import FLIPSIDE_ENDPOINT
from .consts import AAVE_FIRST_BLOCK, DECIMALS_ASTETH, LIDO_STETH
from .eth import AAVE_LPOOL, AAVE_ORACLE, AAVE_WETH_STABLE_DEBT, AAVE_WETH_VAR_DEBT, ASTETH, w3
from .http import requests_get

log = logging.getLogger(__name__)


class AddressSet(set):
    """Set for ETH addresses"""

    def add(self, __element: HexStr) -> None:
        if w3.toInt(hexstr=__element) == 0:
            return  # skip NULL address
        super().add(__element)


ASTETH_HOLDERS = AddressSet()  # cache for hodlers


def get_steth_eth_price(block: BlockIdentifier) -> int:
    """Get the price of stETH in ETH from AAVE protocol"""

    return AAVE_ORACLE.functions.getAssetPrice(LIDO_STETH).call(block_identifier=block)


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
        args = {
            "fromBlock": block,
            "toBlock": block + batch_size,
        }
        events = ASTETH.events.Transfer.getLogs(**args)
        for event in events:
            ASTETH_HOLDERS.add(event["args"]["from"])
            ASTETH_HOLDERS.add(event["args"]["to"])
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
