"""Module for parsing data from AAVE protocol contracts"""

import logging
from collections.abc import Iterable
from typing import TypeAlias

import pandas as pd
from unsync import unsync
from web3.types import BlockData, BlockIdentifier

from .config import TRANSFER_EVENTS_BATCH
from .eth import w3
from .structs import Context, ERC20Like, PoolPosition, UserInfo

log = logging.getLogger(__name__)


UserAndBalance: TypeAlias = tuple[str, float]


@unsync
def get_user_stats(ctx: Context, pair: PoolPosition, user: str) -> UserInfo:
    """Parse user stat from AAVE Lending Pool"""
    return pair.amm.get_user_info(user, ctx.curr_block)


@unsync
def get_atoken_balance(ctx: Context, a_token: ERC20Like, user: str) -> float:
    """Get user's aToken balance"""
    return a_token.balance(user, ctx.curr_block)


@unsync
def get_debt(ctx: Context, pair: PoolPosition, user: str) -> float:
    """Get balance of user from AAVE tokens contracts"""
    return pair.get_total_debt(user, ctx.curr_block)


def get_block_info(block: BlockIdentifier = "latest") -> BlockData:
    """Get the given block information"""
    return w3.eth.get_block(block)


def get_latest_block_number() -> int:
    """Get the latest ETH block number"""
    return w3.eth.block_number


def find_new_atoken_holders(ctx: Context, pair: PoolPosition) -> None:
    """Fetch AToken holders onchain"""

    log.info(
        "Fetching %s holders within the blocks range %d,%d",
        pair.supply_token.a_token.symbol,
        ctx.init_block,
        ctx.curr_block,
    )
    block = ctx.init_block
    while block <= ctx.curr_block:
        args = {
            "fromBlock": block,
            "toBlock": block + TRANSFER_EVENTS_BATCH,
        }
        events = pair.supply_token.a_token.events.Transfer.getLogs(**args)
        for event in events:
            ctx.holders.add(event["args"]["from"])
            ctx.holders.add(event["args"]["to"])
        block += TRANSFER_EVENTS_BATCH


def get_holders_balances(ctx: Context, pair: PoolPosition) -> Iterable[tuple[str, float]]:
    """Get balances of AToken holders"""
    tasks = [(h, get_atoken_balance(ctx, pair.supply_token.a_token, h)) for h in ctx.holders]
    for holder, task in tasks:
        balance = task.result()  # type: ignore
        yield (holder, balance)


def drop_users_below_threshold(
    ctx: Context, threshold: float, users_and_balances: Iterable[UserAndBalance]
) -> Iterable[UserAndBalance]:
    """Drop users with balance below the threshold"""
    for user, balance in users_and_balances:
        if balance < threshold:
            ctx.holders.remove(user)
            continue
        yield (user, balance)


def fetch(ctx: Context, pair: PoolPosition) -> pd.DataFrame | None:
    """Fetch required blockchain data"""

    latest_block = get_latest_block_number()
    if latest_block == ctx.init_block:
        log.info("Block %d has been already read", latest_block)
        return None

    ctx.curr_block = latest_block

    find_new_atoken_holders(ctx, pair)
    buf = get_holders_balances(ctx, pair)
    buf = drop_users_below_threshold(ctx, pair.balance_threshold, buf)  # NOTE: is there a better place for threshold?

    df = pd.DataFrame(buf, columns=["user", "amount"])

    if df.empty:
        ctx.init_block = ctx.curr_block
        log.info("No holders found")
        return None

    log.info("%d holders found", len(df))
    df.set_index("user")

    @unsync
    def _get_stats():

        buf = []
        tasks = [(user, get_user_stats(ctx, pair, user)) for user in df["user"]]
        for user, task in tasks:
            stat: UserInfo = task.result()  # type: ignore
            buf.append({"user": user, **stat})
        return buf

    @unsync
    def _get_debt():

        buf = []
        tasks = [(user, get_debt(ctx, pair, user)) for user in df["user"]]
        for user, task in tasks:
            debt: float = task.result()  # type: ignore
            buf.append({"user": user, "borrowed": debt})
        return buf

    @unsync
    def _get_extra_amount():

        prices = tuple(pair.get_token_price(t.address, ctx.curr_block) for t in pair.extra_tokens)

        @unsync
        def balances(user: str) -> tuple[float, ...]:
            return tuple(t.a_token.balance(user, ctx.curr_block) for t in pair.extra_tokens)

        buf = []
        tasks = [(user, balances(user)) for user in df["user"]]
        for user, task in tasks:
            user_balances: tuple[float, ...] = task.result()  # type: ignore
            extra_amount = sum(b * p for b, p in zip(user_balances, prices))
            buf.append({"user": user, "extra_amount": extra_amount})
        return buf

    tasks = [_get_stats(), _get_debt(), _get_extra_amount()]
    parts = [pd.DataFrame(task.result()) for task in tasks]  # type: ignore # pylint: disable=no-member

    df["supply_price"] = pair.get_supply_token_price(ctx.curr_block)
    df["debt_price"] = pair.get_debt_token_price(ctx.curr_block)

    for part in parts:
        df = df.merge(part, on="user", how="left")

    # move context's blocks forward
    ctx.init_block = ctx.curr_block

    return df
