"""
Reusable async retry utility with exponential backoff and error classification.

Supports both sync and async functions, with configurable retry strategies
for different error types (rate limits, network errors, transient failures).
"""
import asyncio
import time
from functools import wraps
from typing import Callable, TypeVar, Optional, Union, List, Type
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def is_rate_limit_error(exception: Exception) -> bool:
    """Check if exception indicates a rate limit error (429, 503)."""
    error_str = str(exception).lower()
    error_type = type(exception).__name__.lower()
    
    # HTTP status codes
    if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
        return True
    if "503" in error_str or "service unavailable" in error_str:
        return True
    
    # API-specific rate limit indicators
    if "quota" in error_str and ("exceeded" in error_str or "limit" in error_str):
        return True
    
    # Check for rate limit exception types
    if "ratelimiterror" in error_type or "ratelimit" in error_type:
        return True
    
    return False


def is_network_error(exception: Exception) -> bool:
    """Check if exception indicates a transient network error."""
    error_str = str(exception).lower()
    error_type = type(exception).__name__.lower()
    
    # Network-related errors
    network_keywords = [
        "connection", "timeout", "network", "dns", "socket",
        "refused", "unreachable", "reset", "broken pipe",
        "ssl", "certificate", "tls"
    ]
    
    if any(keyword in error_str for keyword in network_keywords):
        return True
    
    # Exception types
    network_exception_types = [
        "connectionerror", "timeouterror", "httperror",
        "requestexception", "socket", "sslerror"
    ]
    
    if any(etype in error_type for etype in network_exception_types):
        return True
    
    return False


def is_transient_error(exception: Exception) -> bool:
    """Check if exception is likely transient and worth retrying."""
    # Rate limits are transient
    if is_rate_limit_error(exception):
        return True
    
    # Network errors are transient
    if is_network_error(exception):
        return True
    
    # Check exception type name for common transient error types
    error_type = type(exception).__name__.lower()
    transient_types = ["networkerror", "timeouterror", "connectionerror"]
    if any(ttype in error_type for ttype in transient_types):
        return True
    
    # 5xx server errors (except 503 which is handled above)
    error_str = str(exception).lower()
    if any(code in error_str for code in ["500", "502", "504", "508"]):
        return True
    
    return False


def calculate_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> float:
    """Calculate backoff delay with exponential backoff and optional jitter.
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd
    
    Returns:
        Delay in seconds before next retry (never exceeds max_delay)
    """
    delay = min(base_delay * (exponential_base ** attempt), max_delay)
    
    if jitter:
        import random
        # Add up to 25% jitter, but ensure total doesn't exceed max_delay
        jitter_amount = min(delay * 0.25 * random.random(), max_delay - delay)
        delay = delay + jitter_amount
    
    return min(delay, max_delay)


async def async_retry(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: Optional[Callable[[Exception], bool]] = None,
    *args,
    **kwargs
) -> T:
    """Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        retry_on: Optional function to determine if exception should be retried.
                  If None, uses is_transient_error by default.
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
    
    Returns:
        Result from func
    
    Raises:
        Last exception if all retries exhausted
    """
    if retry_on is None:
        retry_on = is_transient_error
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Don't retry if it's not a transient error
            if not retry_on(e):
                logger.debug(f"Non-transient error, not retrying: {e}")
                raise
            
            # Don't retry on last attempt
            if attempt >= max_retries - 1:
                logger.warning(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                break
            
            # Calculate backoff delay
            delay = calculate_backoff(
                attempt=attempt,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base
            )
            
            # Special handling for rate limits - use longer delay
            if is_rate_limit_error(e):
                delay = min(delay * 2, max_delay)
                logger.info(f"Rate limit hit, waiting {delay:.2f}s before retry {attempt + 1}/{max_retries}")
            else:
                logger.debug(f"Transient error, retrying in {delay:.2f}s (attempt {attempt + 1}/{max_retries}): {e}")
            
            await asyncio.sleep(delay)
    
    # All retries exhausted
    raise last_exception


def sync_retry(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: Optional[Callable[[Exception], bool]] = None,
    *args,
    **kwargs
) -> T:
    """Retry a synchronous function with exponential backoff.
    
    Args:
        func: Synchronous function to retry
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        retry_on: Optional function to determine if exception should be retried.
                  If None, uses is_transient_error by default.
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
    
    Returns:
        Result from func
    
    Raises:
        Last exception if all retries exhausted
    """
    if retry_on is None:
        retry_on = is_transient_error
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Don't retry if it's not a transient error
            if not retry_on(e):
                logger.debug(f"Non-transient error, not retrying: {e}")
                raise
            
            # Don't retry on last attempt
            if attempt >= max_retries - 1:
                logger.warning(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                break
            
            # Calculate backoff delay
            delay = calculate_backoff(
                attempt=attempt,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base
            )
            
            # Special handling for rate limits - use longer delay
            if is_rate_limit_error(e):
                delay = min(delay * 2, max_delay)
                logger.info(f"Rate limit hit, waiting {delay:.2f}s before retry {attempt + 1}/{max_retries}")
            else:
                logger.debug(f"Transient error, retrying in {delay:.2f}s (attempt {attempt + 1}/{max_retries}): {e}")
            
            time.sleep(delay)
    
    # All retries exhausted
    raise last_exception


def retry_decorator(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: Optional[Callable[[Exception], bool]] = None
):
    """Decorator for retrying functions (works with both sync and async).
    
    Usage:
        @retry_decorator(max_retries=3)
        async def my_async_function():
            ...
        
        @retry_decorator(max_retries=3)
        def my_sync_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await async_retry(
                    func,
                    max_retries=max_retries,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    retry_on=retry_on,
                    *args,
                    **kwargs
                )
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return sync_retry(
                    func,
                    max_retries=max_retries,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    retry_on=retry_on,
                    *args,
                    **kwargs
                )
            return sync_wrapper
    return decorator
