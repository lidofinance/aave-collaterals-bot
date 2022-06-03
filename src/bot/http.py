"""Module for customizing HTTP requests provider"""

from functools import partial
from urllib.parse import urlparse

import requests

from .metrics import HTTP_REQUESTS, HTTP_REQUESTS_DURATION


def _middleware(method: str, **kwargs):
    if "url" not in kwargs:
        raise ValueError("Expected url keyword argument")

    args = urlparse(kwargs["url"])
    with HTTP_REQUESTS_DURATION.labels(
        domain=args.hostname,
        path=args.path,
        method=method,
    ).time():
        resp = getattr(requests, method)(**kwargs)
    HTTP_REQUESTS.labels(
        domain=args.hostname,
        path=args.path,
        method=method,
        http_code=resp.status_code,
    ).inc()

    return resp


requests_get = partial(_middleware, "get")
