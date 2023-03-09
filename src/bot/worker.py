"""Workers module"""

from dataclasses import dataclass, field
from typing import Iterable

from . import bins
from .analytics import Bin
from .structs import ChainId, Context, DebtToken, ERC20Like, LendingPool, Market, Oracle, PoolPosition, SupplyToken


@dataclass
class Worker:
    """Worker class"""

    chain_id: int
    ctx: Context
    pair: PoolPosition
    bins: Iterable[Bin] = field(default_factory=list)


# https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
astETH = Worker(
    chain_id=ChainId.MAINNET,
    pair=PoolPosition(
        amm=Market(
            lending_pool=LendingPool(address="0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"),
            oracle=Oracle(address="0xA50ba011c48153De246E5192C8f9258A2ba79Ca9"),
        ),
        supply_token=SupplyToken(
            a_token=ERC20Like(address="0x1982b2F5814301d4e9a8b0201555376e62F82428"),
            address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
        ),
        debt_token=DebtToken(
            address="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            stable=ERC20Like(address="0x4e977830ba4bd783C0BB7F15d3e243f73FF57121"),
            var=ERC20Like(address="0xF63B34710400CAd3e044cFfDcAb00a0f32E33eCf"),
        ),
        balance_threshold=0.1,
    ),
    ctx=Context(init_block=14289297),
    bins=bins.STETH,
)

# https://docs.aave.com/developers/deployed-contracts/v3-mainnet/ethereum-mainnet
awstETH = Worker(
    chain_id=ChainId.MAINNET,
    pair=PoolPosition(
        amm=Market(
            lending_pool=LendingPool(address="0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"),
            oracle=Oracle(address="0x54586bE62E3c3580375aE3723C145253060Ca0C2"),
        ),
        supply_token=SupplyToken(
            a_token=ERC20Like(address="0x0B925eD163218f6662a35e0f0371Ac234f9E9371"),
            address="0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
        ),
        debt_token=DebtToken(
            address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            stable=ERC20Like(address="0x102633152313C81cD80419b6EcF66d14Ad68949A"),
            var=ERC20Like(address="0xeA51d7853EEFb32b6ee06b1C12E6dcCA88Be0fFE"),
        ),
        balance_threshold=0,
    ),
    ctx=Context(init_block=16496795),
    bins=bins.WSTETH,
)
