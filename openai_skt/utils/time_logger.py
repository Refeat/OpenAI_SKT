import time
import asyncio
import logging
import functools

def async_time_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        result = await func(*args, **kwargs)
        end_time = asyncio.get_event_loop().time()
        logging.info(f"{func.__name__} took {end_time - start_time:.5f} seconds to run.")
        return result
    return wrapper

def time_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.5f} seconds to run.")
        return result
    return wrapper