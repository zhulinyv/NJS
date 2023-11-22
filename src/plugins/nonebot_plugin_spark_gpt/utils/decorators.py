import asyncio
from functools import wraps

from nonebot_plugin_web_config import get_config


def config_func(namespace):
    def decorator(cls):
        func_name = cls.__name__.lower() + "_config"

        @wraps(cls)
        def func():
            return get_config(module=__name__, config_name=cls.__config_name__)

        namespace[func_name] = func
        return cls

    return decorator


def retry(tries, error_message):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error = None
            for _ in range(tries):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    error = e
            raise Exception(f"{error_message}: {error}")

        return wrapper

    return decorator
