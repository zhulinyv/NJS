import json
import httpx
from pathlib import Path
import os
from bs4 import BeautifulSoup
from .config import config_dev

async def get_user_info(user_name:str) -> dict:
    '''通过 user_name 获取信息详情,
    return:
    result["status"],
    result["user_name"],
    result["screen_name"],
    result["bio"]
    '''
    async with httpx.AsyncClient(proxies=config_dev.twitter_proxy) as client:
        res = await client.get(url=f"{config_dev.twitter_url}/{user_name}")
        result ={}
        if res.status_code ==200:
            result["status"] = True
            result["user_name"] = user_name
            soup = BeautifulSoup(res.text,"html.parser")
            result["screen_name"] = match[0].text if (match := soup.find_all('a', class_='profile-card-fullname')) else ""
            result["bio"] = match[0].text if (match := soup.find_all('p')) else ""
        else:
            result["status"] = False

    return result

async def get_user_newtimeline(user_name:str,since_id: str = "0") -> str:
    ''' 通过 user_name 获取推文id列表,
    有 since_id return 最近的新的推文id,
    无 since_id return 最新的推文id'''
    async with httpx.AsyncClient(proxies=config_dev.twitter_proxy) as client:
        res = await client.get(url=f"{config_dev.twitter_url}/{user_name}")
        if res.status_code ==200:
            soup = BeautifulSoup(res.text,"html.parser")
            timeline_list = soup.find_all('a', class_='tweet-link')
            new_line =[]
            for x in timeline_list:
                if user_name in x.attrs["href"]:
                    tweet_id = x.attrs["href"].split("/").pop().replace("#m","")
                    if since_id != "0":
                        if int(tweet_id) > int(since_id):
                            new_line.append(tweet_id)
                    else:
                        new_line.append(tweet_id)
                        
            if since_id == "0":
                if new_line == []:
                    new_line.append("1")
                else:
                    new_line = [str(max(map(int,new_line)))]
            if new_line == []:
                new_line = ["not found"]
        else:
            new_line = ["not found"]
    return new_line[-1]

async def get_tweet(user_name:str,tweet_id: str = "0") -> dict:
    '''通过 user_name 和 tweet_id 获取推文详情,
    return:
    result["status"],
    result["text"],
    result["pic_url_list"],
    result["video_url"],
    result["r18"]
    '''
    async with httpx.AsyncClient(proxies=config_dev.twitter_proxy) as client:
        res = await client.get(url=f"{config_dev.twitter_url}/{user_name}/status/{tweet_id}",cookies={"hlsPlayback": "on"})
        result = {}
        if res.status_code ==200:
            result["status"] = True
            soup = BeautifulSoup(res.text,"html.parser")
            # text
            result["text"] = match[0].text if (match := soup.find_all('div', class_='tweet-content media-body')) else ""
            # pic
            if pic_list := soup.find_all('a', class_='still-image'):
                result["pic_url_list"] = [x.attrs["href"] for x in pic_list]
            else:
                result["pic_url_list"] = []
            # video
            if video_list := soup.find_all('video'):
                # result["video_url"] = video_list[0].attrs["data-url"]
                result["video_url"] = f"https://twitter.com/{user_name}/status/{tweet_id}"
            else:
                result["video_url"] = ""
            # r18
            result["r18"] = bool(r18 := soup.find_all('div', class_='unavailable-box'))
        else:
            result["status"] = False
    return result

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'}

async def get_video(url: str) -> str:
    path = Path() / "data" / "twitter" / "cache" /  f"{url.split('/').pop()}.mp4"
    path = f"{os.getcwd()}/{str(path)}"

    async with httpx.AsyncClient(proxies=config_dev.twitter_proxy) as client:
        res = await client.get(f"https://twitterxz.com/?url={url}",headers=header)
        if res.status_code != 200:
            raise ValueError("视频下载失败")
        soup = BeautifulSoup(res.text,"html.parser")
        video_url = json.loads(soup.find_all('script')[0].text)['props']['pageProps']['twitterInfo']['videoInfos'][-1]['url']
        async with client.stream("get",video_url) as s:
            if res.status_code != 200:
                raise ValueError("视频下载失败")
        
            with open(path,'wb') as file:
                async for chunk in s.aiter_bytes():
                    file.write(chunk)

    return path