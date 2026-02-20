"""
Unit tests for src.utils.retry (retry utilities with exponential backoff).
Run from repo root: pytest tests/test_retry.py -v
"""
import asyncio
from unittest.mock import MagicMock, patch
import pytest

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.retry import (
    is_rate_limit_error,
    is_network_error,
    is_transient_error,
    calculate_backoff,
    async_retry,
    sync_retry,
    retry_decorator
)


class RateLimitError(Exception):
    """Simulated rate limit error."""
    pass


class NetworkError(Exception):
    """Simulated network error."""
    pass


class PermanentError(Exception):
    """Simulated permanent error."""
    pass


def test_is_rate_limit_error():
    """Test rate limit error detection."""
    assert is_rate_limit_error(Exception("429 rate limit exceeded"))
    assert is_rate_limit_error(Exception("HTTP 429 Too Many Requests"))
    assert is_rate_limit_error(Exception("503 Service Unavailable"))
    assert is_rate_limit_error(Exception("quota exceeded"))
    assert not is_rate_limit_error(Exception("400 Bad Request"))
    assert not is_rate_limit_error(Exception("normal error"))


def test_is_network_error():
    """Test network error detection."""
    assert is_network_error(Exception("connection timeout"))
    assert is_network_error(Exception("network unreachable"))
    assert is_network_error(Exception("DNS resolution failed"))
    assert is_network_error(Exception("socket error"))
    assert not is_network_error(Exception("validation error"))


def test_is_transient_error():
    """Test transient error detection."""
    assert is_transient_error(Exception("429 rate limit"))
    assert is_transient_error(Exception("connection timeout"))
    assert is_transient_error(Exception("500 Internal Server Error"))
    assert not is_transient_error(Exception("400 Bad Request"))
    assert not is_transient_error(Exception("validation error"))


def test_calculate_backoff():
    """Test backoff calculation."""
    # First attempt should use base delay
    delay = calculate_backoff(attempt=0, base_delay=1.0, max_delay=60.0)
    assert 1.0 <= delay <= 1.25  # Base delay + jitter
    
    # Second attempt should be exponential
    delay = calculate_backoff(attempt=1, base_delay=1.0, max_delay=60.0)
    assert 2.0 <= delay <= 2.5  # 2x base + jitter
    
    # Should respect max delay
    delay = calculate_backoff(attempt=10, base_delay=1.0, max_delay=60.0)
    assert delay <= 60.0
    
    # Without jitter
    delay = calculate_backoff(attempt=1, base_delay=1.0, jitter=False)
    assert delay == 2.0


def test_sync_retry_success():
    """Test sync retry succeeds on first attempt."""
    def success_func():
        return "success"
    
    result = sync_retry(success_func, max_retries=3)
    assert result == "success"


def test_sync_retry_succeeds_after_failures():
    """Test sync retry succeeds after transient failures."""
    call_count = [0]
    
    def flaky_func():
        call_count[0] += 1
        if call_count[0] < 3:
            raise NetworkError("transient")
        return "success"
    
    result = sync_retry(flaky_func, max_retries=3, base_delay=0.01)
    assert result == "success"
    assert call_count[0] == 3


def test_sync_retry_fails_after_max_retries():
    """Test sync retry fails after max retries."""
    def failing_func():
        raise NetworkError("always fails")
    
    with pytest.raises(NetworkError):
        sync_retry(failing_func, max_retries=2, base_delay=0.01)


def test_sync_retry_no_retry_on_permanent_error():
    """Test sync retry doesn't retry on permanent errors."""
    call_count = [0]
    
    def permanent_error_func():
        call_count[0] += 1
        raise PermanentError("permanent")
    
    def is_permanent(e):
        return isinstance(e, PermanentError)
    
    with pytest.raises(PermanentError):
        sync_retry(permanent_error_func, max_retries=3, retry_on=lambda e: not is_permanent(e), base_delay=0.01)
    
    # Should only be called once (no retries)
    assert call_count[0] == 1


@pytest.mark.asyncio
async def test_async_retry_success():
    """Test async retry succeeds on first attempt."""
    async def success_func():
        return "success"
    
    result = await async_retry(success_func, max_retries=3)
    assert result == "success"


@pytest.mark.asyncio
async def test_async_retry_succeeds_after_failures():
    """Test async retry succeeds after transient failures."""
    call_count = [0]
    
    async def flaky_func():
        call_count[0] += 1
        if call_count[0] < 2:
            raise NetworkError("transient")
        return "success"
    
    result = await async_retry(flaky_func, max_retries=3, base_delay=0.01)
    assert result == "success"
    assert call_count[0] == 2


@pytest.mark.asyncio
async def test_async_retry_fails_after_max_retries():
    """Test async retry fails after max retries."""
    async def failing_func():
        raise NetworkError("always fails")
    
    with pytest.raises(NetworkError):
        await async_retry(failing_func, max_retries=2, base_delay=0.01)


def test_retry_decorator_sync():
    """Test retry decorator on sync function."""
    call_count = [0]
    
    @retry_decorator(max_retries=3, base_delay=0.01)
    def flaky_func():
        call_count[0] += 1
        if call_count[0] < 2:
            raise NetworkError("transient")
        return "success"
    
    result = flaky_func()
    assert result == "success"
    assert call_count[0] == 2


@pytest.mark.asyncio
async def test_retry_decorator_async():
    """Test retry decorator on async function."""
    call_count = [0]
    
    @retry_decorator(max_retries=3, base_delay=0.01)
    async def flaky_func():
        call_count[0] += 1
        if call_count[0] < 2:
            raise NetworkError("transient")
        return "success"
    
    result = await flaky_func()
    assert result == "success"
    assert call_count[0] == 2
