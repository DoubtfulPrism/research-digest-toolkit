#!/usr/bin/env python3
"""Unit tests for http_client.py."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from diskcache import Cache


@pytest.mark.unit
class TestGetSyncClient:
    """Tests for get_sync_client()."""

    def test_returns_httpx_client(self):
        from rdt.shared.http_client import get_sync_client

        client = get_sync_client(use_cache=False)
        assert isinstance(client, httpx.Client)
        client.close()

    def test_with_cache_uses_cache_transport(self):
        from rdt.shared.http_client import CacheControlTransport, get_sync_client

        client = get_sync_client(use_cache=True)
        assert isinstance(client._transport, CacheControlTransport)
        client.close()

    def test_without_cache_uses_default_transport(self):
        from rdt.shared.http_client import CacheControlTransport, get_sync_client

        client = get_sync_client(use_cache=False)
        assert not isinstance(client._transport, CacheControlTransport)
        client.close()

    def test_with_auth(self):
        from rdt.shared.http_client import get_sync_client

        auth = httpx.BasicAuth("user", "pass")
        client = get_sync_client(use_cache=False, auth=auth)
        assert client._auth is auth
        client.close()


@pytest.mark.unit
class TestGetAsyncClient:
    """Tests for get_async_client()."""

    def test_returns_httpx_async_client(self):
        from rdt.shared.http_client import get_async_client

        client = get_async_client(use_cache=False)
        assert isinstance(client, httpx.AsyncClient)

    def test_with_cache_uses_async_cache_transport(self):
        from rdt.shared.http_client import AsyncCacheControlTransport, get_async_client

        client = get_async_client(use_cache=True)
        assert isinstance(client._transport, AsyncCacheControlTransport)

    def test_without_cache_uses_default_transport(self):
        from rdt.shared.http_client import AsyncCacheControlTransport, get_async_client

        client = get_async_client(use_cache=False)
        assert not isinstance(client._transport, AsyncCacheControlTransport)


@pytest.mark.unit
class TestMakeBearerAuth:
    """Tests for make_bearer_auth()."""

    def test_returns_httpx_auth(self):
        from rdt.shared.http_client import make_bearer_auth

        auth = make_bearer_auth("mytoken")
        assert isinstance(auth, httpx.Auth)

    def test_bearer_auth_adds_authorization_header(self):
        from rdt.shared.http_client import make_bearer_auth

        auth = make_bearer_auth("mytoken123")
        request = httpx.Request("GET", "https://example.com")
        # Consume the auth flow generator
        list(auth.auth_flow(request))
        assert request.headers["Authorization"] == "Bearer mytoken123"


@pytest.mark.unit
class TestCacheControlTransport:
    """Tests for CacheControlTransport."""

    def setup_method(self):
        self.cache = MagicMock(spec=Cache)
        self.inner_transport = MagicMock(spec=httpx.BaseTransport)

    def test_cache_miss_calls_inner_transport(self):
        from rdt.shared.http_client import CacheControlTransport

        self.cache.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.inner_transport.handle_request.return_value = mock_response

        transport = CacheControlTransport(
            cache=self.cache,
            cache_ttl=3600,
            transport=self.inner_transport,
        )
        request = httpx.Request("GET", "https://example.com/data")
        transport.handle_request(request)

        self.inner_transport.handle_request.assert_called_once_with(request)
        self.cache.set.assert_called_once()

    def test_cache_hit_returns_cached_response(self):
        from rdt.shared.http_client import CacheControlTransport

        cached_resp = MagicMock()
        self.cache.get.return_value = cached_resp

        transport = CacheControlTransport(
            cache=self.cache,
            cache_ttl=3600,
            transport=self.inner_transport,
        )
        request = httpx.Request("GET", "https://example.com/cached")
        result = transport.handle_request(request)

        assert result == cached_resp
        self.inner_transport.handle_request.assert_not_called()

    def test_non_get_request_not_cached(self):
        from rdt.shared.http_client import CacheControlTransport

        mock_response = MagicMock()
        self.inner_transport.handle_request.return_value = mock_response

        transport = CacheControlTransport(
            cache=self.cache,
            cache_ttl=3600,
            transport=self.inner_transport,
        )
        request = httpx.Request("POST", "https://example.com/data")
        transport.handle_request(request)

        self.cache.get.assert_not_called()
        self.cache.set.assert_not_called()

    def test_non_200_response_not_cached(self):
        from rdt.shared.http_client import CacheControlTransport

        self.cache.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 404
        self.inner_transport.handle_request.return_value = mock_response

        transport = CacheControlTransport(
            cache=self.cache,
            cache_ttl=3600,
            transport=self.inner_transport,
        )
        request = httpx.Request("GET", "https://example.com/missing")
        transport.handle_request(request)

        self.cache.set.assert_not_called()


@pytest.mark.unit
class TestAsyncCacheControlTransport:
    """Tests for AsyncCacheControlTransport (instantiation only — async calls need pytest-asyncio)."""

    def test_instantiation_with_defaults(self):
        from rdt.shared.http_client import AsyncCacheControlTransport

        cache = MagicMock(spec=Cache)
        transport = AsyncCacheControlTransport(cache=cache, cache_ttl=7200)
        assert transport.cache is cache
        assert transport.cache_ttl == 7200
        assert transport.transport is not None  # default AsyncHTTPTransport created

    def test_instantiation_with_custom_transport(self):
        from rdt.shared.http_client import AsyncCacheControlTransport

        cache = MagicMock(spec=Cache)
        inner = MagicMock(spec=httpx.AsyncBaseTransport)
        transport = AsyncCacheControlTransport(
            cache=cache, cache_ttl=60, transport=inner
        )
        assert transport.transport is inner

    async def test_cache_hit_returns_cached_response(self):
        from rdt.shared.http_client import AsyncCacheControlTransport

        cache = MagicMock(spec=Cache)
        cached_response = MagicMock()
        cached_response.aread = AsyncMock()
        cache.get.return_value = cached_response

        inner = MagicMock(spec=httpx.AsyncBaseTransport)
        transport = AsyncCacheControlTransport(
            cache=cache, cache_ttl=3600, transport=inner
        )
        request = httpx.Request("GET", "https://example.com/cached")
        result = await transport.handle_async_request(request)

        assert result is cached_response
        cached_response.aread.assert_called_once()
        inner.handle_async_request.assert_not_called()

    async def test_cache_miss_fetches_and_caches(self):
        from rdt.shared.http_client import AsyncCacheControlTransport

        cache = MagicMock(spec=Cache)
        cache.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.aread = AsyncMock()

        inner = MagicMock(spec=httpx.AsyncBaseTransport)
        inner.handle_async_request = AsyncMock(return_value=mock_response)

        transport = AsyncCacheControlTransport(
            cache=cache, cache_ttl=3600, transport=inner
        )
        request = httpx.Request("GET", "https://example.com/data")
        result = await transport.handle_async_request(request)

        assert result is mock_response
        mock_response.aread.assert_called_once()
        cache.set.assert_called_once()

    async def test_non_200_response_not_cached(self):
        from rdt.shared.http_client import AsyncCacheControlTransport

        cache = MagicMock(spec=Cache)
        cache.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.aread = AsyncMock()

        inner = MagicMock(spec=httpx.AsyncBaseTransport)
        inner.handle_async_request = AsyncMock(return_value=mock_response)

        transport = AsyncCacheControlTransport(
            cache=cache, cache_ttl=3600, transport=inner
        )
        request = httpx.Request("GET", "https://example.com/missing")
        await transport.handle_async_request(request)

        cache.set.assert_not_called()

    async def test_non_get_request_not_cached(self):
        from rdt.shared.http_client import AsyncCacheControlTransport

        cache = MagicMock(spec=Cache)
        mock_response = MagicMock()
        inner = MagicMock(spec=httpx.AsyncBaseTransport)
        inner.handle_async_request = AsyncMock(return_value=mock_response)

        transport = AsyncCacheControlTransport(
            cache=cache, cache_ttl=3600, transport=inner
        )
        request = httpx.Request("POST", "https://example.com/data")
        result = await transport.handle_async_request(request)

        assert result is mock_response
        cache.get.assert_not_called()
        cache.set.assert_not_called()
