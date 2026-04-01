import time
import logging
from openai import RateLimitError, APITimeoutError, APIConnectionError

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # seconds


def retry_openai_call(func, *args, **kwargs):
    """Retry an OpenAI API call with exponential backoff on rate limits and transient errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                logger.warning("OpenAI rate limit hit, retrying in %ds (attempt %d/%d)", delay, attempt + 1, MAX_RETRIES)
                time.sleep(delay)
            else:
                logger.error("OpenAI rate limit exceeded after %d retries: %s", MAX_RETRIES, e)
                raise
        except (APITimeoutError, APIConnectionError) as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                logger.warning("OpenAI transient error, retrying in %ds (attempt %d/%d): %s", delay, attempt + 1, MAX_RETRIES, e)
                time.sleep(delay)
            else:
                logger.error("OpenAI API failed after %d retries: %s", MAX_RETRIES, e)
                raise
