import asyncio

import aiohttp

from .decorators import retry
from .generate import generate_random

csrf_token = generate_random(32)
session_id = generate_random(32)
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": f"csrftoken={csrf_token}; sessionid={session_id}",
    "Referer": "https://dpaste.org/",
    "Referrer-Policy": "same-origin"
}


async def get_url(content: str, format_: str = "_markdown"):
    @retry(5, "粘贴到pastebin时出错")
    async def get_paste_url(content_: str, format__: str = "_markdown"):
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            payload = {
                "csrfmiddlewaretoken": csrf_token,
                "title": "",
                "expires": "2592000",
                "format": "url",
                "lexer": format__,
                "content": content_,
            }
            async with session.post(
                    "https://dpaste.org", data=payload
            ) as resp:
                resp.raise_for_status()
                url = resp.url
                return str(url)

    try:
        url = await get_paste_url(content, format_)
        return url
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    async def main():
        url = await get_url("1234")
        print(url)


    asyncio.run(main())
