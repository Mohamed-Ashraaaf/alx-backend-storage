#!/usr/bin/env python3
""" Web page retrieval and caching """

import redis
import requests
from typing import Callable
from functools import wraps

# Initialize a Redis client
redis_client = redis.Redis()


def get_page(url: str) -> str:
    """ Retrieve HTML content from a URL and cache the result in Redis """
    # Check if the URL is cached
    cached_content = redis_client.get(url)

    if cached_content is not None:
        # If cached content exists, return it
        return cached_content.decode('utf-8')

    try:
        # Use the requests module to make an HTTP GET request
        response = requests.get(f"https://{url}")

        if response.status_code == 200:
            # If the request was successful
            content = response.text
            redis_client.setex(url, 10, content)
            return content
        else:
            # Handle non-200 status codes or request errors
            return f"Failed to fetch from {url} (Status: {response.status_code})"
    except Exception as e:
        return f"Error while fetching content from {url}: {str(e)}"


def count_calls(fn: Callable) -> Callable:
    """ Decorator to count the number of calls to a function """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        call_key = f"count:{fn.__qualname__}"
        redis_client.incr(call_key)
        return fn(*args, **kwargs)

    return wrapper


# Example usage
if __name__ == "__main__":
    url = "slowwly.robertomurray.co.uk"
    content = get_page(url)
    print(content)
