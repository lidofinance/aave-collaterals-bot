"""Workers module"""

from dataclasses import dataclass, field
from typing import Iterable

from . import bins
from .analytics import Bin
from .structs import (
    ChainId,
    Context,
    DebtToken,
    ERC20Like,
    LendingPoolV2,
    LendingPoolV3,
    Market,
    PoolPosition,
    SupplyToken,
)


@dataclass
class Worker:
    """Worker class"""

    ctx: Context
    pair: PoolPosition
    bins: Iterable[Bin] = field(default_factory=list)


# https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
astETH = Worker(
    pair=PoolPosition(
        chain_id=ChainId.HOMESTEAD,
        amm=Market(lending_pool=LendingPoolV2(address="0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")),
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
    pair=PoolPosition(
        chain_id=ChainId.HOMESTEAD,
        amm=Market(lending_pool=LendingPoolV3(address="0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2")),
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

# https://docs.aave.com/developers/deployed-contracts/v3-mainnet/polygon
polStMATIC = Worker(
    pair=PoolPosition(
        chain_id=ChainId.POLYGON,
        amm=Market(lending_pool=LendingPoolV3(address="0x794a61358D6845594F94dc1DB02A252b5b4814aD")),
        supply_token=SupplyToken(
            a_token=ERC20Like(address="0xEA1132120ddcDDA2F119e99Fa7A27a0d036F7Ac9"),
            address="0x3A58a54C066FdC0f2D55FC9C89F0415C92eBf3C4",
        ),
        debt_token=DebtToken(
            address="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
            stable=ERC20Like(address="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"),
            var=ERC20Like(address="0x4a1c3aD6Ed28a636ee1751C69071f6be75DEb8B8"),
        ),
        balance_threshold=0,
    ),
    ctx=Context(init_block=33101585),
    bins=bins.STMATIC,
)

# https://docs.aave.com/developers/deployed-contracts/v3-mainnet/arbitrum
arbwstETH = Worker(
    pair=PoolPosition(
        chain_id=ChainId.ARBITRUM,
        amm=Market(lending_pool=LendingPoolV3(address="0x794a61358D6845594F94dc1DB02A252b5b4814aD")),
        supply_token=SupplyToken(
            a_token=ERC20Like(address="0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf"),
            address="0x5979D7b546E38E414F7E9822514be443A4800529",
        ),
        debt_token=DebtToken(
            address="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
            stable=ERC20Like(address="0xD8Ad37849950903571df17049516a5CD4cbE55F6"),
            var=ERC20Like(address="0x0c84331e39d6658Cd6e6b9ba04736cC4c4734351"),
        ),
        balance_threshold=0,
    ),
    ctx=Context(init_block=65735133),
    bins=bins.WSTETH,
)


# https://docs.aave.com/developers/deployed-contracts/v3-mainnet/optimism
# NOTE: will be added soon after the investigation of emode availability
# optwstETH = Worker(
#     chain_id=ChainId.OPTIMISM,
#     pair=PoolPosition(
#         amm=Market(lending_pool=LendingPool(address="0x794a61358D6845594F94dc1DB02A252b5b4814aD")),
#         supply_token=SupplyToken(
#             a_token=ERC20Like(address="0xc45A479877e1e9Dfe9FcD4056c699575a1045dAA"),
#             address="0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb",
#         ),
#         debt_token=DebtToken(
#             address="0x4200000000000000000000000000000000000006",
#             stable=ERC20Like(address="0xD8Ad37849950903571df17049516a5CD4cbE55F6"),
#             var=ERC20Like(address="0x0c84331e39d6658Cd6e6b9ba04736cC4c4734351"),
#         ),
#         balance_threshold=0,
#     ),
#     ctx=Context(init_block=76697000),  # first transfer event
#     bins=bins.STETH,
# )
