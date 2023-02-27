"""Data structs"""

import math
from contextlib import suppress
from dataclasses import dataclass, field
from enum import IntEnum
from functools import cached_property
from typing import ClassVar, NamedTuple, TypedDict

from eth_typing.encoding import HexStr
from web3.exceptions import ContractLogicError
from web3.types import BlockIdentifier

from . import abi
from .consts import DECIMALS_HEALTHF
from .eth import get_contract, w3


class ChainId(IntEnum):
    """Chain IDs"""

    MAINNET = 1
    POLYGON = 137


class AddressSet(set):
    """Set for ETH addresses"""

    def add(self, __element: HexStr) -> None:
        if w3.toInt(hexstr=__element) == 0:
            return  # skip NULL address
        super().add(__element)


@dataclass
class IsContract:
    """Simple code generator for contracts declarations.
    `contract` field is initialized via object construction and attributes are proxied to it."""

    address: str
    abi: ClassVar[str]

    def __post_init__(self):
        self.contract = get_contract(address=self.address, abi=self.abi)

    def __getattr__(self, item):
        return getattr(self.contract, item)


@dataclass
class ERC20Like(IsContract):
    """Basic ERC20 contract wrapper"""

    abi = abi.ERC20

    @cached_property
    def decimals(self) -> int:
        """Proxy to ERC20 decimals() method"""
        return self.contract.functions.decimals().call()

    @cached_property
    def precision(self) -> int:
        """Precision of the token"""
        return 10**self.decimals

    @cached_property
    def symbol(self) -> str:
        """Proxy to ERC20 symbol() method"""
        return self.contract.functions.symbol().call()


@dataclass
class SupplyToken(ERC20Like):
    """The token the user deposits to the pool"""

    a_token: ERC20Like  # AToken counter-part


@dataclass
class DebtToken(ERC20Like):
    """The token the user receives when borrowing from the pool"""

    # NOTE: maybe it's possible to get stable/variable debt tokens from contract
    stable: ERC20Like
    var: ERC20Like


@dataclass
class Oracle(IsContract):
    """AAVE Oracle"""

    abi = abi.Oracle

    @cached_property
    def decimals(self) -> int:
        """Precision of returned values"""
        try:
            base_unit_precision = self.contract.functions.BASE_CURRENCY_UNIT().call()
            return int(math.log(base_unit_precision, 10))
        except ContractLogicError:
            return 18  # defaults to ETH-based

    @cached_property
    def precision(self) -> int:
        """Precision of returned values"""
        return 10**self.decimals


@dataclass
class LendingPool(IsContract):
    """AAVE Pool"""

    abi = abi.LendingPool


class LPUserAccountDataResponse(NamedTuple):
    """Response from AAVE Lending Pool contract getUserAccountData endpoint"""

    # NOTE: preserve order of fields

    collateral: int
    debt: int
    available_borrow: int
    liquidation_threshold: int
    ltv: int
    healthfactor: int


class UserInfo(TypedDict):
    """User info"""

    collateral: float
    debt: float
    liquidation_threshold: int
    ltv: int
    healthfactor: float
    emode: bool | None


@dataclass
class Market:
    """Market on AAVE"""

    lending_pool: LendingPool
    oracle: Oracle  # NOTE: get onchain via call to addresses provider

    @cached_property
    def base_precision(self) -> int:
        """Precision of the base token"""
        return self.oracle.precision

    def get_asset_price(self, asset: str, block: BlockIdentifier) -> int:
        """Get asset price in base units"""
        asset = w3.toChecksumAddress(asset)
        return self.oracle.contract.functions.getAssetPrice(asset).call(block_identifier=block) / self.oracle.precision

    def get_user_info(self, user: str, block: BlockIdentifier) -> UserInfo:
        """Get user account data from AAVE Lending Pool"""
        user = w3.toChecksumAddress(user)
        r = self.lending_pool.contract.functions.getUserAccountData(user).call(block_identifier=block)
        r = LPUserAccountDataResponse(*r)

        return UserInfo(
            collateral=r.collateral / self.base_precision,
            debt=r.debt / self.base_precision,
            liquidation_threshold=r.liquidation_threshold,
            healthfactor=r.healthfactor / 10**DECIMALS_HEALTHF,
            ltv=r.ltv,
            emode=self.get_user_emode(user, block),
        )

    def get_user_emode(self, user: str, block: BlockIdentifier) -> bool | None:
        """Get user e-mode flag"""
        with suppress(ContractLogicError):
            return bool(self.lending_pool.functions.getUserEMode(user).call(block_identifier=block))

        return None


@dataclass
class PoolPosition:
    """Pair of supply and debt tokens on the given market"""

    amm: Market

    supply_token: SupplyToken
    debt_token: DebtToken

    balance_threshold: float = 0

    @cached_property
    def name(self) -> str:
        """Get position name"""
        return f"{self.supply_token.symbol}-{self.debt_token.symbol}"

    def get_total_supply(self, user: str, block: BlockIdentifier) -> int:
        """Get user total supplied amount of the collateral token"""
        a_token = self.supply_token.a_token
        user = w3.toChecksumAddress(user)
        return a_token.contract.functions.balanceOf(user).call(block_identifier=block) / a_token.precision

    def get_total_debt(self, user: str, block: BlockIdentifier) -> float:
        """Get user total borrowed amount of the debt token"""
        address = w3.toChecksumAddress(user)
        return sum(
            (
                self.debt_token.stable.functions.balanceOf(address).call(block_identifier=block)
                / self.debt_token.stable.precision,
                self.debt_token.var.functions.balanceOf(address).call(block_identifier=block)
                / self.debt_token.var.precision,
            )
        )

    def get_supply_token_price(self, block: BlockIdentifier) -> int:
        """Get supply token price in base units"""
        return self.amm.get_asset_price(self.supply_token.address, block)

    def get_debt_token_price(self, block: BlockIdentifier) -> int:
        """Get debt token price in base units"""
        return self.amm.get_asset_price(self.debt_token.address, block)


@dataclass
class Context:
    """Context for a worker"""

    init_block: int = 0
    curr_block: int = 0

    holders: AddressSet = field(default_factory=AddressSet)
