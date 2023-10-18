#!/usr/bin/env python3
""" Web page retrieval and caching """

import requests
import redis
from typing import Callable

redis_client = redis.Redis()


def get_page(url: str) -> str:
    """ Retrieve HTML content from a URL and cache the result in Redis """
    cached_content = redis_client.get(url)

    if cached_content is not None:
        return cached_content.decode('utf-8')

    response = requests.get(url)

    if response.status_code == 200:
        content = response.text
        redis_client.setex(url, 10, content)
        return content
    else:
        return f"Failed to fetch content from {url}"


def count_calls(fn: Callable) -> Callable:
    """ Decorator to count the number of calls to a function """

    def wrapper(*args, **kwargs):
        call_key = f"count:{fn.__qualname__}"
        redis_client.incr(call_key)
        return fn(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/10000/url/text"
    content = get_page(url)
    print(content)
