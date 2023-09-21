"""ETH Web3 connection"""

import logging
from functools import cache

from web3 import HTTPProvider, Web3
from web3.contract import Contract
from web3.middleware import simple_cache_middleware  # type: ignore

from .config import FALLBACK_NODE_ENDPOINT, NODE_ENDPOINT
from .middleware import construct_fallback_provider_middleware, metrics_collector, retryable

log = logging.getLogger(__name__)


w3 = Web3(HTTPProvider(NODE_ENDPOINT, request_kwargs={"timeout": 90}))
w3.middleware_onion.add(metrics_collector)
w3.middleware_onion.add(retryable)
if FALLBACK_NODE_ENDPOINT:
    w3.middleware_onion.add(construct_fallback_provider_middleware(w3, FALLBACK_NODE_ENDPOINT))
    log.info("fallback provider is configured")
w3.middleware_onion.add(simple_cache_middleware)


@cache
def get_contract(address: str, abi: str) -> Contract:
    """Get Contract instance by the given address"""

    address = Web3.toChecksumAddress(address)
    return w3.eth.contract(address=address, abi=abi)
