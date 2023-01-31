"""Workaround to reduce calls count to ETH node"""

# pylint: disable=unused-argument,invalid-name,unused-import

import logging
from typing import Any, Callable

from eth_typing import URI  # type: ignore
from requests import HTTPError, Response
from retry.api import retry_call
from web3 import Web3
from web3.types import RPCEndpoint, RPCResponse

from .consts import HTTP_REQUESTS_DELAY, HTTP_REQUESTS_RETRY
from .metrics import ETH_RPC_REQUESTS, ETH_RPC_REQUESTS_DURATION

log = logging.getLogger(__name__)


def chain_id_mock(
    make_request: Callable[[RPCEndpoint, Any], RPCResponse], _: Web3
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
        rpc_domain = _get_provider_domain_from_w3(w3)

        try:
            with ETH_RPC_REQUESTS_DURATION.labels(provider=rpc_domain).time():
                response = make_request(method, params)
        except HTTPError as ex:
            failed: Response = ex.response
            ETH_RPC_REQUESTS.labels(
                provider=rpc_domain,
                method=method,
                code=failed.status_code,
            ).inc()
            raise
        else:
            # https://www.jsonrpc.org/specification#error_object
            # https://eth.wiki/json-rpc/json-rpc-error-codes-improvement-proposal
            error = response.get("error")
            code: int = 0
            if isinstance(error, dict):
                code = error.get("code") or code
            ETH_RPC_REQUESTS.labels(
                provider=rpc_domain,
                method=method,
                code=code,
            ).inc()

            return response

    return middleware


def construct_fallback_provider_middleware(w3: Web3, fallback: URI) -> Callable:
    """Constructs a middleware which mimics fallback provider"""

    main_endpoint = getattr(w3.provider, "endpoint_uri")
    if not main_endpoint:
        raise ValueError("Web3 provider endpoint is not set")

    def fallback_provider(
        make_request: Callable[[RPCEndpoint, Any], RPCResponse], _: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        """Constructs a middleware which measure requests parameters"""

        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            switch_to_main()
            try:
                return make_request(method, params)
            except Exception as e:  # pylint: disable=W0703
                log.warning("Request to provider has been failed: %s", e)
                switch_to_fallback()
                return make_request(method, params)

        return middleware

    def switch_to_main() -> None:
        w3.provider.endpoint_uri = main_endpoint  # type: ignore
        log.debug("Switched to main provider")

    def switch_to_fallback() -> None:
        w3.provider.endpoint_uri = fallback  # type: ignore
        log.debug("Switched to fallback provider")

    return fallback_provider


def retryable(
    make_request: Callable[[RPCEndpoint, Any], RPCResponse], _: Web3
) -> Callable[[RPCEndpoint, Any], RPCResponse]:
    """Constructs a middleware which retries requests to the endpoint"""

    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:

        return retry_call(
            make_request,
            (method, params),
            tries=HTTP_REQUESTS_RETRY,
            delay=HTTP_REQUESTS_DELAY,
        )

    return middleware


def _get_provider_domain_from_w3(w3: Web3) -> str:
    """Get provider domain from Web3 object"""

    uri = getattr(w3.provider, "endpoint_uri", "unknown")
    return uri.split("://")[-1].split("/")[0].split(":")[0]
