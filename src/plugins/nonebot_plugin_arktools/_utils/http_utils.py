import httpx
from nonebot import logger
from .._exceptions import *


async def request_(url, method: str = "GET", *, retry: int = 5, **kwargs):
    if method in {"get", "GET"}:
        return await async_get(url, retry=retry, **kwargs)
    elif method in {"post", "POST"}:
        return await async_post(url, retry=retry, **kwargs)
    else:
        raise NoMethodException


async def async_get(url, *, retry: int = 5, **kwargs):
    async with httpx.AsyncClient() as client:
        for times in range(retry):
            try:
                return await client.get(url, **kwargs)
            except httpx.TimeoutException:
                logger.warning(f"get请求第{times+1}次失败...")
                continue
            except Exception:
                raise
        raise


async def async_post(url, *, retry: int = 5, **kwargs):
    async with httpx.AsyncClient() as client:
        for times in range(retry):
            try:
                return await client.post(url, **kwargs)
            except httpx.TimeoutException:
                logger.warning(f"post请求第{times+1}次失败...")
                continue
            except Exception:
                raise
        raise
