import aiohttp
from .config import githubcard_config


token = githubcard_config.github_token

Headers1 = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}
Headers2 = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}

if token is None:
    headers=Headers1
else:
    headers=Headers2

async def get_github_reposity_information(url: str) -> str:
    try:
        UserName, RepoName = url.replace("https://github.com/", "").split("/")
    except:
        UserName, RepoName = url.replace("github.com/", "").split("/")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/users/{UserName}", headers=headers, timeout=5) as response:
            RawData = await response.json()  
            AvatarUrl = RawData["avatar_url"]
            ImageUrl = f"https://image.thum.io/get/width/1280/crop/640/viewportWidth/1280/png/noanimate/https://socialify.git.ci/{UserName}/{RepoName}/image?description=1&font=Rokkitt&language=1&name=1&owner=1&pattern=Circuit%20Board&theme=Light&logo={AvatarUrl}"
            return ImageUrl