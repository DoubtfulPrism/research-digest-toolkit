## HTTP Caching Pattern

**HTTPX + DiskCache integration for caching GET requests with custom transports.**

### When to Apply

- Repeated HTTP requests to the same URLs (RSS feeds, API endpoints)
- Development/testing to avoid hammering external services
- Rate-limited APIs where cache reduces request count
- Long-running scrapers that might restart (preserve progress)

### The Pattern

**1. Use helper functions from http_client.py:**

```python
from http_client import get_sync_client, get_async_client

# Synchronous client with caching (default TTL: 1 hour)
client = get_sync_client(use_cache=True, cache_ttl=3600)
response = client.get("https://api.example.com/data")

# Asynchronous client with caching
async_client = get_async_client(use_cache=True, cache_ttl=3600)
response = await async_client.get("https://api.example.com/data")
```

**2. Cache directory:** `http_cache/` (automatically created via DiskCache)

**3. Cache behavior:**
- Only GET requests are cached
- Cache key: Full URL (including query params)
- TTL: Configurable per client (default 3600s = 1 hour)
- Cache hit: Logged to Rich console as `[cyan]Cache hit for {url}[/cyan]`

### Custom Transport Implementation

```python
import httpx
from diskcache import Cache

class CacheControlTransport(httpx.BaseTransport):
    def __init__(self, cache: Cache, cache_ttl: int, transport=None):
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.transport = transport or httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            cache_key = str(request.url)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                console.log(f"[cyan]Cache hit for {request.url}[/cyan]")
                cached_response.read()  # Ensure response body is available
                return cached_response

            response = self.transport.handle_request(request)
            response.read()  # Read response before caching
            if response.status_code == 200:
                self.cache.set(cache_key, response, expire=self.cache_ttl)
            return response
        return self.transport.handle_request(request)
```

### Why

- **Performance** - Eliminates redundant network requests
- **Reliability** - Continue working if external service becomes unavailable
- **Rate limit friendly** - Reduces API calls, avoids 429 errors
- **Development speed** - Fast iteration without waiting for slow APIs
- **Disk-based** - Cache persists across process restarts

### Common Mistakes

- Caching non-GET requests (POST, PUT, DELETE) - these should never be cached
- Not reading response body before caching - leads to empty cached responses
- Forgetting to specify TTL for time-sensitive data - stale cache
- Caching error responses (4xx/5xx) - only 200 OK is cached

### Examples

**Good:**

```python
from http_client import get_sync_client

# Cache RSS feed for 1 hour (3600s)
client = get_sync_client(use_cache=True, cache_ttl=3600)
response = client.get("https://example.com/feed.xml")

# Disable caching for real-time data
client_no_cache = get_sync_client(use_cache=False)
response = client_no_cache.get("https://api.example.com/live")
```

**Bad:**

```python
# Manual caching - reinventing the wheel
import pickle
cache_file = "my_cache.pkl"
if os.path.exists(cache_file):
    with open(cache_file, "rb") as f:
        response = pickle.load(f)
else:
    response = httpx.get(url)
    with open(cache_file, "wb") as f:
        pickle.dump(response, f)
```

### Cache Management

```python
from diskcache import Cache

# Access cache directly for management
cache = Cache("http_cache")

# Clear all cache
cache.clear()

# Get cache stats
print(f"Cache size: {cache.volume()}")
print(f"Cache entries: {len(cache)}")

# Delete specific entry
cache.delete("https://example.com/api/data")
```

### TTL Guidelines

| Data Type | Recommended TTL |
|-----------|-----------------|
| RSS feeds | 3600s (1 hour) |
| Rate-limited APIs | 7200s (2 hours) |
| Static documentation | 86400s (24 hours) |
| Real-time data | 300s (5 min) or no cache |
| Development/testing | 3600s (1 hour) |

### Async Pattern

```python
from http_client import get_async_client

async def fetch_multiple():
    async_client = get_async_client(use_cache=True, cache_ttl=3600)

    # First call hits the network
    response1 = await async_client.get("https://api.example.com/data")

    # Second call (same URL) hits the cache
    response2 = await async_client.get("https://api.example.com/data")

    await async_client.aclose()
```
