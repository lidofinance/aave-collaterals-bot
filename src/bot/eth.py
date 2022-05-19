"""ETH Web3 connection"""

import json
import logging
import os
from functools import cache
from pathlib import Path

from web3 import HTTPProvider, Web3
from web3.contract import Contract

from .config import NODE_ENDPOINT
from .middleware import requests_cache

log = logging.getLogger(__name__)

ABI_HOME = Path(os.path.dirname(__file__), "abi")

# https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
AAVE_LPOOL_ADDRESS = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"  # Aave v2 Lending Pool Contract)
AAVE_ORACLE_ADDRESS = "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9"  # Aave Chain
ASTETH_ADDRESS = "0x1982b2F5814301d4e9a8b0201555376e62F82428"  # aSTETH token

w3 = Web3(HTTPProvider(NODE_ENDPOINT))
w3.middleware_onion.add(requests_cache, "requests_cache")


@cache
def _contract(address: str, abi_file: os.PathLike) -> Contract:
    """Get Contract instance by the given address"""

    address = w3.toChecksumAddress(address)
    with open(abi_file, mode="r", encoding="utf-8") as file:
        abi = json.load(file)
        return w3.eth.contract(address=address, abi=abi)


AAVE_LPOOL = _contract(AAVE_LPOOL_ADDRESS, ABI_HOME / "aave-lpool-abi.json")
AAVE_ORACLE = _contract(AAVE_ORACLE_ADDRESS, ABI_HOME / "aave-oracle-abi.json")
ASTETH = _contract(ASTETH_ADDRESS, ABI_HOME / "asteth-abi.json")
