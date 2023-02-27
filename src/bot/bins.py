"""Bins for collaterals"""

import pandas as pd

from .analytics import Bin


def steth_bin1(df: pd.DataFrame) -> pd.DataFrame:
    """AAVE users with >=80% collaterals - stETH and  >=80% debt - ETH"""

    df = df.copy()

    df.query("diff_collateral <= 0.2 and diff_debt <= 0.2 and borrowed > 0", inplace=True)

    return df


def steth_bin2(df: pd.DataFrame) -> pd.DataFrame:
    """AAVE users with stETH collateral and >=80% debt - not ETH"""

    df = df.copy()

    df.query("diff_debt > 0.8", inplace=True)

    return df


def steth_bin3(df: pd.DataFrame) -> pd.DataFrame:
    """All the others AAVE users with stETH collateral"""

    bin1_df = steth_bin1(df)
    bin2_df = steth_bin2(df)

    return pd.DataFrame(pd.concat([df, bin1_df, bin2_df]).drop_duplicates(keep=False))


STETH: list[Bin] = [
    (
        (1.42, 1.21, 1.14, 1.07, 1.03, 1.00),
        steth_bin1,
    ),
    (
        (2.50, 1.75, 1.50, 1.25, 1.10, 1.00),
        steth_bin2,
    ),
    (
        (2.50, 1.75, 1.50, 1.25, 1.10, 1.00),
        steth_bin3,
    ),
]


def wsteth_bin1_1(df: pd.DataFrame) -> pd.DataFrame:
    """Users with e-mode (collateral - wstETH, debt - ETH)"""

    df = df.copy()

    df = df.query("diff_collateral <= 0.2 and diff_debt <= 0.2 and borrowed > 0 and emode == True")

    return df


def wsteth_bin1_2(df: pd.DataFrame) -> pd.DataFrame:
    """Users without e-mode and with >=80% of collateral - wstETH, and >= 80% of debt - ETH"""

    df = df.copy()

    df = df.query("diff_collateral <= 0.2 and diff_debt <= 0.2 and borrowed > 0 and emode == False")

    return df


def wsteth_bin2(df: pd.DataFrame) -> pd.DataFrame:
    """AAVE users with wstETH collateral and >=80% debt - not ETH"""

    df = df.copy()

    df.query("diff_debt > 0.8", inplace=True)

    return df


def wsteth_bin3(df: pd.DataFrame) -> pd.DataFrame:
    """All the others AAVE users with stETH collateral"""

    others = (
        wsteth_bin1_1(df),
        wsteth_bin1_2(df),
        wsteth_bin2(df),
    )

    return pd.DataFrame(pd.concat([df, *others]).drop_duplicates(keep=False))


WSTETH: list[Bin] = [
    (
        (1.42, 1.21, 1.14, 1.07, 1.03, 1.00),
        wsteth_bin1_1,
    ),
    (
        (1.42, 1.21, 1.14, 1.07, 1.03, 1.00),
        wsteth_bin1_2,
    ),
    (
        (2.50, 1.75, 1.50, 1.25, 1.10, 1.00),
        wsteth_bin2,
    ),
    (
        (2.50, 1.75, 1.50, 1.25, 1.10, 1.00),
        wsteth_bin3,
    ),
]
