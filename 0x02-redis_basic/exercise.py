#!/usr/bin/env python3
"""
Redis Cache implementation
"""
import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class to store and retrieve data in Redis
    """
    def __init__(self):
        """
        Initialize the Cache instance and flush the Redis database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()


    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis and return the generated key.

        Args:
            data (Union[str, bytes, int, float]): Data to store in Redis.

        Returns:
            str: A unique key for the stored data.
        """
        key = str(uuid.uuid4())
        if isinstance(data, (str, bytes, int, float)):
            self._redis.set(key, data)
        return key
