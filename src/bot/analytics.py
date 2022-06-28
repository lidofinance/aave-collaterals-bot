"""Analytics methods"""

from contextlib import suppress
from typing import Iterable, List

import pandas as pd
from web3.types import BlockIdentifier

from .aaveparser import get_steth_eth_price
from .consts import DECIMALS_AWETH, DECIMALS_HEALTHF, DECIMALS_STETH

RISK_LABELS = ["A", "B+", "B", "B-", "C", "D", "liquidation"]

RISK_VALUES_BIN1 = [1.42, 1.21, 1.14, 1.07, 1.03, 1.00]
RISK_VALUES_BIN2 = [2.50, 1.75, 1.50, 1.25, 1.10, 1.00]
RISK_VALUES_BIN3 = [2.50, 1.75, 1.50, 1.25, 1.10, 1.00]


def prepare_data(df: pd.DataFrame, block: BlockIdentifier) -> pd.DataFrame:
    """Transform raw data received"""

    df = df.copy()

    df["amount"] = df["amount"] / pow(10, DECIMALS_STETH)
    df["collateral"] = df["collateral"] / pow(10, DECIMALS_STETH)
    df["debt"] = df["debt"] / pow(10, DECIMALS_STETH)
    df["ethdebt"] = df["ethdebt"] / pow(10, DECIMALS_AWETH)
    df["healthf"] = df["healthf"] / pow(10, DECIMALS_HEALTHF)

    df.fillna(0, inplace=True)
    df = pd.DataFrame(data=df.query("collateral > 0 and debt > 0"))
    steth_price = get_steth_eth_price(block) / pow(10, DECIMALS_STETH)
    df["diff_collateral"] = abs(df["collateral"] - df["amount"] * steth_price) / df["collateral"]
    df["diff_debt"] = abs(df["ethdebt"] - df["debt"]) / df["debt"]

    return df


def get_risks(df: pd.DataFrame, ratio_list: List[float]) -> pd.DataFrame:
    """
    This function calculates the risk level for each position
    and returns the positions sorted by risk
    """

    df = df.copy()

    df["risk_rating"] = [
        (x > ratio_list[0] and "A")
        or (ratio_list[1] < x <= ratio_list[0] and "B+")
        or (ratio_list[2] < x <= ratio_list[1] and "B")
        or (ratio_list[3] < x <= ratio_list[2] and "B-")
        or (ratio_list[4] < x <= ratio_list[3] and "C")
        or (ratio_list[5] < x <= ratio_list[4] and "D")
        or (ratio_list[5] <= x and "liquidation")
        for x in df["healthf"]
    ]

    df.query("amount > 0", inplace=True)
    df.sort_values(by="healthf", ascending=False, inplace=True)

    return df


def get_distr(data) -> pd.DataFrame:
    """This function calculates and returns a pivot table by risk levels"""

    risk_distr = data.pivot_table(index="risk_rating", values=["amount"], aggfunc=["sum", "count"])
    risk_distr.columns = ["stETH", "cnt"]
    risk_distr["percent"] = (risk_distr["stETH"] / risk_distr["stETH"].sum()) * 100

    return risk_distr


def bin1(df: pd.DataFrame) -> pd.DataFrame:
    """AAVE users with >=80% collaterals - stETH and  >=80% debt - ETH"""

    df = df.copy()

    df.query("diff_collateral <= 0.2 and diff_debt <= 0.2 and ethdebt > 0", inplace=True)

    return df


def bin2(df: pd.DataFrame) -> pd.DataFrame:
    """AAVE users with stETH collateral and >=80% debt - not ETH"""

    df = df.copy()

    df.query("diff_debt > 0.8", inplace=True)
    df.sort_values(by=(["amount"]), ascending=False, inplace=True)

    return df


def bin3(df: pd.DataFrame) -> pd.DataFrame:
    """All the others AAVE users with stETH collateral"""

    bin1_df = bin1(df)
    bin2_df = bin2(df)

    return pd.DataFrame(pd.concat([df, bin1_df, bin2_df]).drop_duplicates(keep=False))


def calculate_values(data: pd.DataFrame, block: BlockIdentifier) -> Iterable[dict[str, float]]:
    """Calculate risk distribution.
    Almost as is from related jupyter notebook."""

    data = prepare_data(data, block)

    bins = (
        (bin1, RISK_VALUES_BIN1),
        (bin2, RISK_VALUES_BIN2),
        (bin3, RISK_VALUES_BIN3),
    )

    result = []
    for transform, risks_values in bins:
        df = transform(data)
        df = get_risks(df, risks_values)
        risk_distr = get_distr(df)

        values = {}
        for label in RISK_LABELS:
            value: float = 0
            with suppress(KeyError):
                value = risk_distr.at[label, "percent"]
            values[label] = value

        result.append(values)

    return result
