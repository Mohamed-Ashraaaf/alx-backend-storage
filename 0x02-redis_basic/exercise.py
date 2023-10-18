#!/usr/bin/env python3
"""
Redis Cache implementation
"""
import redis
import uuid
from typing import Union, Callable
import functools


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

    @staticmethod
    def count_calls(method: Callable) -> Callable:
        """
        Decorator to count the number of times a method is called.

        Args:
            method (Callable): The method to be counted.

        Returns:
            Callable: A wrapped method that increments the call count.
        """
        attribute = "_cache:count:" + method.__qualname__

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            """
            Wrapper function that increments the call count

            Args:
                self: The instance itself.
                *args: Arguments passed to the method.
                **kwargs: Keyword arguments passed to the method.

            Returns:
                Any: The result of the original method.
            """
            self._redis.incr(attribute)
            return method(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def call_history(method: Callable) -> Callable:
        """
        Decorator to store the history of inputs and outputs for a function.

        Args:
            method (Callable): The method to be decorated.

        Returns:
            Callable: A wrapped method that stores input and output history.
        """
        input_key = "{}:inputs".format(method.__qualname__)
        output_key = "{}:outputs".format(method.__qualname__)

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            """
            Wrapper function that appends input arguments and stores output.

            Args:
                self: The instance itself.
                *args: Arguments passed to the method.
                **kwargs: Keyword arguments passed to the method.

            Returns:
                Any: The result of the original method.
            """
            input_data = str(args)
            self._redis.rpush(input_key, input_data)
            result = method(self, *args, **kwargs)
            self._redis.rpush(output_key, str(result))
            return result

        return wrapper

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

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int]:
        """
        Retrieve data from Redis based on the key

        Args:
            key (str): Key to retrieve data from Redis.
            fn (Callable, optional): Callable to convert data back

        Returns:
            Union[str, bytes, int]: Retrieved data, possibly converted
        """
        data = self._redis.get(key)
        if data and fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, bytes, int]:
        """
        Retrieve data from Redis and automatically convert it to a string.

        Args:
            key (str): Key to retrieve data from Redis.

        Returns:
            Union[str, bytes, int]: Retrieved data, converted to a string.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[str, bytes, int]:
        """
        Retrieve data from Redis and automatically convert it to an integer.

        Args:
            key (str): Key to retrieve data from Redis.

        Returns:
            Union[str, bytes, int]: Retrieved data, converted to an integer.
        """
        return self.get(key, fn=int)

    def replay(self, method: Callable):
        """
        Display the history of calls for a particular function.
        Args:
        method (Callable): The method to replay
        Returns:
        None
        """
        qualified_name = method.__qualname__
        input_key = "{}:inputs".format(qualified_name)
        output_key = "{}:outputs".format(qualified_name)

        inputs = self._redis.lrange(input_key, 0, -1)
        outputs = self._redis.lrange(output_key, 0, -1)

        print("{} was called {} times:".format(qualified_name, len(inputs)))

        for input_data, output_data in zip(inputs, outputs):
            input_args = eval(input_data)
            print("{}{} -> {}".format(
                qualified_name,
                input_args,
                output_data.decode("utf-8")
                ))
