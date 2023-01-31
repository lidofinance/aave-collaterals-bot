"""ETH Web3 connection"""

import json
import logging
import os
from functools import cache
from pathlib import Path

from web3 import HTTPProvider, Web3
from web3.contract import Contract

from .config import FALLBACK_NODE_ENDPOINT, NODE_ENDPOINT
from .consts import (
    AAVE_LPOOL_ADDRESS,
    AAVE_ORACLE_ADDRESS,
    AAVE_WETH_STABLE_DEBT_ADDRESS,
    AAVE_WETH_VAR_DEBT_ADDRESS,
    ASTETH_ADDRESS,
)
from .middleware import chain_id_mock, construct_fallback_provider_middleware, metrics_collector, retryable

log = logging.getLogger(__name__)

ABI_HOME = Path(os.path.dirname(__file__), "abi")


w3 = Web3(HTTPProvider(NODE_ENDPOINT))
w3.middleware_onion.add(metrics_collector)
w3.middleware_onion.add(retryable)
if FALLBACK_NODE_ENDPOINT:
    w3.middleware_onion.add(construct_fallback_provider_middleware(w3, FALLBACK_NODE_ENDPOINT))
w3.middleware_onion.add(chain_id_mock)


@cache
def _contract(address: str, abi_file: os.PathLike) -> Contract:
    """Get Contract instance by the given address"""

    address = Web3.toChecksumAddress(address)
    with open(abi_file, mode="r", encoding="utf-8") as file:
        abi = json.load(file)
        return w3.eth.contract(address=address, abi=abi)


AAVE_LPOOL = _contract(AAVE_LPOOL_ADDRESS, ABI_HOME / "aave-lpool-abi.json")
AAVE_ORACLE = _contract(AAVE_ORACLE_ADDRESS, ABI_HOME / "aave-oracle-abi.json")
AAVE_WETH_STABLE_DEBT = _contract(AAVE_WETH_STABLE_DEBT_ADDRESS, ABI_HOME / "aave-weth-stable-debt-abi.json")
AAVE_WETH_VAR_DEBT = _contract(AAVE_WETH_VAR_DEBT_ADDRESS, ABI_HOME / "aave-weth-var-debt-abi.json")
ASTETH = _contract(ASTETH_ADDRESS, ABI_HOME / "asteth-abi.json")
