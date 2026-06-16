import time
from functools import wraps
import openai

# Worth retrying: transient issues that might succeed on a second
# attempt. A rate limit clears, a connection blip passes, a server
# hiccup resolves on its own.
RETRYABLE_EXCEPTIONS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
)

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2


def with_retry(func):
    """
    Retries the wrapped function on transient API errors using
    exponential backoff (2s, 4s, 8s).

    Errors NOT in RETRYABLE_EXCEPTIONS are raised immediately, no
    retry. openai.PermissionDeniedError is a good example, that's the
    exact error type we hit earlier when the xAI account ran out of
    billing credits. Retrying that would just waste time, it was never
    going to succeed without fixing the billing account manually.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except RETRYABLE_EXCEPTIONS as e:
                if attempt == MAX_RETRIES:
                    raise
                print(
                    f"Attempt {attempt} failed ({type(e).__name__}), "
                    f"retrying in {backoff}s..."
                )
                time.sleep(backoff)
                backoff *= 2

    return wrapper