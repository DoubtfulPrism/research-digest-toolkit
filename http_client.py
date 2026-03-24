#!/usr/bin/env python3
"""
HTTP client with caching for the Research Digest Toolkit.
"""

import httpx
from diskcache import Cache
from rich.console import Console

console = Console()

cache = Cache("http_cache")


def get_sync_client(
    use_cache: bool = True,
    cache_ttl: int = 3600,
    auth: httpx.Auth | None = None,
) -> httpx.Client:
    """
    Returns a synchronous HTTPX client with optional caching and auth.
    """
    if use_cache:
        return httpx.Client(
            auth=auth,
            transport=CacheControlTransport(cache=cache, cache_ttl=cache_ttl),
        )
    return httpx.Client(auth=auth)


def get_async_client(
    use_cache: bool = True, cache_ttl: int = 3600
) -> httpx.AsyncClient:
    """
    Returns an asynchronous HTTPX client with optional caching.
    """
    if use_cache:
        return httpx.AsyncClient(
            transport=AsyncCacheControlTransport(cache=cache, cache_ttl=cache_ttl)
        )
    return httpx.AsyncClient()


class _BearerAuth(httpx.Auth):
    """Auth flow that adds a Bearer token to the Authorization header."""

    def __init__(self, token: str) -> None:
        super().__init__()
        self._token = token

    def auth_flow(self, request: httpx.Request):  # type: ignore[override]
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


def make_bearer_auth(token: str) -> httpx.Auth:
    """Return an httpx.Auth that adds a Bearer token header."""
    return _BearerAuth(token)


class CacheControlTransport(httpx.BaseTransport):
    """
    A custom HTTPX transport that uses DiskCache for caching GET requests.
    """

    def __init__(
        self, cache: Cache, cache_ttl: int, transport: httpx.BaseTransport | None = None
    ):
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.transport = transport or httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            cache_key = str(request.url)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                console.log(f"[cyan]Cache hit for {request.url}[/cyan]")
                cached_response.read()
                return cached_response

            response = self.transport.handle_request(request)
            response.read()
            if response.status_code == 200:
                self.cache.set(cache_key, response, expire=self.cache_ttl)
            return response
        return self.transport.handle_request(request)


class AsyncCacheControlTransport(httpx.AsyncBaseTransport):
    """
    An asynchronous custom HTTPX transport that uses DiskCache for caching GET requests.
    """

    def __init__(
        self,
        cache: Cache,
        cache_ttl: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.transport = transport or httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            cache_key = str(request.url)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                console.log(f"[cyan]Cache hit for {request.url}[/cyan]")
                await cached_response.aread()
                return cached_response

            response = await self.transport.handle_async_request(request)
            await response.aread()
            if response.status_code == 200:
                self.cache.set(cache_key, response, expire=self.cache_ttl)
            return response
        return await self.transport.handle_async_request(request)
