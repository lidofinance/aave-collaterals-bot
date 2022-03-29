"""Module for parsing data from Anchor protocol contracts"""

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd
import requests
from unsync import unsync

from config import FLIPSIDE_ENDPOINT
from eth import AAVE_LPOOL, AAVE_ORACLE, ASTETH, w3

LIDO_STETH = w3.toChecksumAddress("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")


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


def _crypto_to_usd(currency: str) -> float:

    payload = CoinGeckoPriceRequestParams(ids=currency)
    r = requests.get("https://api.coingecko.com/api/v3/simple/price", params=asdict(payload), timeout=5)
    r.raise_for_status()
    return r.json()[currency]["usd"]


def eth_last_price() -> float:
    """Current price of ETH"""

    return _crypto_to_usd("ethereum")


def steth_last_price() -> float:
    """Current price of stETH"""

    return _crypto_to_usd("staked-ether")


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
def get_user_stats(user: str) -> LendingPoolResponse:
    """Parse user stat from AAVE Lending Pool"""

    address = w3.toChecksumAddress(user)
    result = AAVE_LPOOL.functions.getUserAccountData(address).call()
    return LendingPoolResponse(*result)


@unsync
def get_asteth_balance(user: str) -> float:
    """Get user's astETH balance"""

    address = w3.toChecksumAddress(user)
    return ASTETH.functions.balanceOf(address).call()


def get_userlist() -> Iterable:
    """Get the list of borrowers.
    NB! It's subject to change!"""

    r = requests.get(FLIPSIDE_ENDPOINT, timeout=15)
    r.raise_for_status()
    return r.json()


def parse() -> pd.DataFrame:
    """Parse required data"""

    df = pd.DataFrame(get_userlist())
    df.set_index("user")
    del df["amount"]  # will be parsed separately

    @unsync
    def _parse_stats():

        buf = []
        tasks = [(user, get_user_stats(user)) for user in df["user"]]
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
        tasks = [(user, get_asteth_balance(user)) for user in df["user"]]
        for user, task in tasks:
            balance: float = task.result()  # type: ignore
            buf.append({"user": user, "amount": balance})
        return buf

    tasks = [_parse_stats(), _parse_balance()]
    parts = [pd.DataFrame(task.result()) for task in tasks]  # type: ignore

    for part in parts:
        df = df.merge(part, on="user", how="left")

    return df
