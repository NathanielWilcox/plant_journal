from functools import wraps
from typing import Callable
import requests, time
from django.db import connection, OperationalError, InterfaceError
from .token_validator import token_validator


def with_auth_retry(max_retries: int = 3, retry_delay: int = 1):
    """
    Decorator for API calls requiring authentication.
    Injects auth headers and retries on 401 Unauthorized.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    # Merge headers safely: prefer headers supplied by caller (e.g. user token)
                    supplied_headers = kwargs.get("headers", {})
                    auth_headers = token_validator.get_headers() or {}
                    # Ensure supplied_headers is a dict
                    if not isinstance(supplied_headers, dict):
                        supplied_headers = {}
                    # Keep auth_headers as defaults, allow supplied_headers to override
                    auth_headers.update(supplied_headers)
                    kwargs["headers"] = auth_headers

                    return func(*args, **kwargs)

                except requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code == 401:
                        # Refresh token and retry
                        token_validator._refresh_token()
                        retries += 1
                        time.sleep(retry_delay)
                        continue
                    raise
            # If all retries fail
            return {"error": f"Authentication failed after {max_retries} retries"}
        return wrapper
    return decorator


def with_db_retry(max_retries: int = 3, retry_delay: int = 1):
    """
    Decorator to handle database connection errors and implement retry logic.
    Ensures connection is valid before executing the function.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_error = None

            while retries < max_retries:
                try:
                    connection.ensure_connection()
                    result = func(*args, **kwargs)
                    return result
                except (OperationalError, InterfaceError) as e:
                    last_error = str(e)
                    retries += 1
                    if retries < max_retries:
                        connection.close()
                        time.sleep(retry_delay)
                        continue
                except Exception as e:
                    return {"error": f"Database operation failed: {str(e)}"}

            return {
                "error": f"Database connection failed after {max_retries} retries. Last error: {last_error}"
            }
        return wrapper
    return decorator
