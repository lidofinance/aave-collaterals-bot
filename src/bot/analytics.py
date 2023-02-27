"""Analytics methods"""

import logging
from contextlib import suppress
from typing import Callable, TypeAlias

import pandas as pd

log = logging.getLogger(__name__)


Thresholds: TypeAlias = tuple[
    float,
    float,
    float,
    float,
    float,
    float,
]

Filter: TypeAlias = Callable[[pd.DataFrame], pd.DataFrame] | str
Bin: TypeAlias = tuple[Thresholds, Filter]


RISK_LABELS = ["A", "B+", "B", "B-", "C", "D", "liquidation"]


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw data received"""

    df = df.copy()
    df = pd.DataFrame(data=df.query("collateral > 0 and debt > 0"))
    df.sort_values(by=(["amount"]), ascending=False, inplace=True)
    df.rename(columns={"healthfactor": "healthf"}, inplace=True)
    df.fillna(0, inplace=True)
    df["diff_collateral"] = abs(df["collateral"] - df["amount"] * df["supply_price"]) / df["collateral"]
    df["diff_debt"] = abs(df["borrowed"] * df["debt_price"] - df["debt"]) / df["debt"]

    return df


def get_risks(df: pd.DataFrame, ratio_list: Thresholds) -> pd.DataFrame:
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


def get_distr(df: pd.DataFrame) -> pd.DataFrame:
    """This function calculates and returns a pivot table by risk levels"""

    risk_distr = df.pivot_table(index="risk_rating", values="amount", aggfunc=["sum", "count"])
    risk_distr.columns = pd.Index(("asset", "cnt"))
    risk_distr["percent"] = (risk_distr["asset"] / risk_distr["asset"].sum()) * 100

    return risk_distr


def _apply_df_query_filter(df: pd.DataFrame, filter_: Filter) -> pd.DataFrame:
    """Apply filter to dataframe"""

    if callable(filter_):
        return filter_(df)

    df = df.copy()
    df.query(filter_, inplace=True)

    return df


def get_zones_values(df: pd.DataFrame, bin_: Bin) -> dict[str, float]:
    """Calculate risk distribution.
    Almost as is from related jupyter notebook."""

    thresholds, filter_ = bin_

    df = prepare_data(df)
    df = _apply_df_query_filter(df, filter_)

    if df.empty:
        return {label: 0.0 for label in RISK_LABELS}

    risks = get_risks(df, thresholds)
    risk_distr = get_distr(risks)

    result = {}
    for label in RISK_LABELS:
        value: float = 0
        with suppress(KeyError):
            value = risk_distr.at[label, "asset"]
        result[label] = value

    return result
