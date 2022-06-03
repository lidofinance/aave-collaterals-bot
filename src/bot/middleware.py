"""Workaround to reduce calls count to ETH node"""

# pylint: disable=unused-argument,invalid-name,unused-import

import logging
from typing import Any, Callable

from web3 import Web3
from web3.types import RPCEndpoint, RPCResponse

from .metrics import ETH_RPC_REQUESTS, ETH_RPC_REQUESTS_DURATION

log = logging.getLogger(__name__)


def chain_id_mock(
    make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: "Web3"
) -> Callable[[RPCEndpoint, Any], RPCResponse]:
    """Constructs a middleware which mock eth_chainId method call response"""

    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:

        # simple_cache_middleware supports eth_chainId method caching but
        # since we are using threading based concurrency, the middleware
        # is not applicable (at least as I can se at the moment)
        if method == "eth_chainId":
            return {
                "id": 0,
                "jsonrpc": "2.0",
                "result": 1,
            }

        return make_request(method, params)

    return middleware


def metrics_collector(
    make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: "Web3"
) -> Callable[[RPCEndpoint, Any], RPCResponse]:
    """Constructs a middleware which measure requests parameters"""

    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:

        with ETH_RPC_REQUESTS_DURATION.time():
            response = make_request(method, params)

        # https://www.jsonrpc.org/specification#error_object
        # https://eth.wiki/json-rpc/json-rpc-error-codes-improvement-proposal
        error = response.get("error")
        code: int = 0
        if isinstance(error, dict):
            code = error.get("code") or code
        ETH_RPC_REQUESTS.labels(
            method=method,
            code=code,
        ).inc()

        return response

    return middleware
