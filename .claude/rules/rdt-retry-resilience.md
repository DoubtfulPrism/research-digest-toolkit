## Retry & Resilience Pattern

**Automatic retry with exponential backoff for transient network failures.**

### When to Apply

- Any HTTP request to external APIs or web pages
- Network operations that can fail temporarily (5xx errors, timeouts)
- Rate-limited APIs (429 Too Many Requests)

### The Pattern

**1. Use pre-configured decorators from retry_utils.py:**

```python
from retry_utils import retry_with_logging, retry_api_call

@retry_with_logging(verbose=True)
def fetch_content(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    return response.text

@retry_api_call(verbose=True)
def call_api(endpoint):
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()
```

**2. Or use helper functions for one-off requests:**

```python
from retry_utils import make_resilient_request, make_resilient_api_call

# Standard retry (3 attempts)
response = make_resilient_request(url, session=session, verbose=True)

# API retry with rate limit handling (5 attempts)
response = make_resilient_api_call(api_url, session=session, verbose=True)
```

### Retry Configurations

| Decorator | Attempts | Backoff | Use When |
|-----------|----------|---------|----------|
| `@retry_with_logging` | 3 | 1s, 2s, 4s | General HTTP requests |
| `@retry_api_call` | 5 | 2s, 4s, 8s, 16s, 32s | Rate-limited APIs |

### What Gets Retried

- ✅ **Network errors:** `Timeout`, `ConnectionError`
- ✅ **Server errors:** 5xx status codes
- ✅ **Rate limits:** 429 Too Many Requests
- ❌ **Client errors:** 4xx (except 429) - these are not retried

### Why

- **Resilience** - Handles transient network failures automatically
- **Exponential backoff** - Reduces load on struggling servers
- **Visibility** - Rich console logging shows retry attempts and wait times
- **Rate limit friendly** - Longer backoff for 429 errors

### Common Mistakes

- Not calling `response.raise_for_status()` - retries won't trigger on HTTP errors
- Using retry on 4xx client errors - these are permanent failures
- Retrying indefinitely - always have a stop condition
- Not using `verbose=False` for batch operations - floods console

### Examples

**Good:**

```python
from retry_utils import retry_api_call

@retry_api_call(verbose=True)
def fetch_hackernews_item(item_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Triggers retry on 5xx/429
    return response.json()
```

**Bad:**

```python
# Manual retry logic - error-prone, no backoff
for attempt in range(3):
    try:
        response = requests.get(url)
        break  # Success
    except Exception:
        if attempt == 2:
            raise
        time.sleep(1)  # Fixed delay, not exponential
```

### Error Handling in Retry Logic

The `should_retry_http_error()` function determines retry eligibility:

```python
# From retry_utils.py
def should_retry_http_error(exception):
    if isinstance(exception, requests.exceptions.HTTPError):
        status_code = exception.response.status_code
        # Don't retry 4xx (except 429 rate limit)
        if 400 <= status_code < 500 and status_code != 429:
            return False
        # Retry 5xx and 429
        return status_code >= 500 or status_code == 429
    # Retry network errors
    return isinstance(exception, (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ))
```

### Rich Logging Output

When `verbose=True`, retries are logged with color-coded Rich console output:

```
⚠️  Attempt 2 failed: HTTPError: 503 Server Error. Retrying in 2.0s...
⚠️  Rate limited (attempt 3). Waiting 4.0s before retry...
```
