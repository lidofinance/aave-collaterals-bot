"""Workaround to reduce calls count to ETH node"""
# pylint: disable=unused-argument,invalid-name,unused-import

import logging
from typing import Any, Callable

from web3 import Web3
from web3.types import Middleware, RPCEndpoint, RPCResponse

log = logging.getLogger(__name__)


def construct_mock_chain_id_middleware() -> Middleware:
    """Constructs a middleware which mock eth_chainId method call response"""

    def wrapper(
        make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: "Web3"
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:

            if method == "eth_chainId":
                return {
                    "id": 0,
                    "jsonrpc": "2.0",
                    "result": 1,
                }
            return make_request(method, params)

        return middleware

    return wrapper


requests_cache = construct_mock_chain_id_middleware()

# The following code should be used, by I cannot make it works at the moment :(

# from web3.middleware.cache import construct_simple_cache_middleware
#
# requests_cache = construct_simple_cache_middleware(
#     cache_class=dict,
#     rpc_whitelist=[  # type: ignore
#         "eth_chainId",
#     ],
# )
