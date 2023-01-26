from faker import Faker
import requests
import parsel
import json
import re


# get 图片
def get_pic(url):
    res = requests.get(url).json()
    pic_url = res["pic"][0]
    return pic_url

# bing 壁纸
TYPES=["PHONE","DESKTOP","RANDOM"]
url = 'https://cn.bing.com'

def getFakerHeaders(TYPE):
    fake = Faker()
    if str(TYPE).upper()=="PHONE":
        return 'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_1 like Mac OS X; hsb-DE) AppleWebKit/531.21.4 (KHTML, like Gecko) Version/3.0.5 Mobile/8B116 Safari/6531.21.4'
    if str(TYPE).upper() == "DESKTOP":
        return 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_5 rv:5.0; the-NP) AppleWebKit/534.2.5 (KHTML, like Gecko) Version/5.0.5 Safari/534.2.5'
    if str(TYPE).upper() == "RANDOM":
        return fake.user_agent()

def getBingImageURL():
    headers= {"user-agent": getFakerHeaders("DESKTOP")}
    respond=requests.get(url=url,headers=headers)
    respond.encoding = respond.apparent_encoding
    selector = parsel.Selector(respond.text, base_url=url)
    url1=str(selector.css('#preloadBg::attr(href)').extract_first())
    url1=confirmURL(url1)
    return url1

def getBingVerticalImageURL():
    headers= {"user-agent": getFakerHeaders("PHONE")}
    respond=requests.get(url=url,headers=headers)
    respond.encoding = respond.apparent_encoding
    selector = parsel.Selector(respond.text, base_url=url)
    url1=str(selector.css('#preloadBg::attr(href)').extract_first())
    url1=confirmURL(url1)
    return url1

def getBingDescription():
    headers = {
        'user-agent':getFakerHeaders('DESKTOP')
    }
    res = requests.get(url, headers=headers)
    res.encoding = res.apparent_encoding
    ret = re.search("var _model =(\{.*?\});", res.text)
    if not ret:
        return
    data = json.loads(ret.group(1))
    image_content = data['MediaContents'][0]['ImageContent']
    return {
        'headline': image_content['Headline'],
        'title': image_content['Title'],
        'description': image_content['Description'],
        'main_text': image_content['QuickFact']['MainText'],
    }

def confirmURL(url):
    url_head=str(url)
    result=""
    if(url_head[0:6]=="/th?id"):
        result="https://s.cn.bing.net"+url_head
        return result
    else:
        return str(url)

async def getImage(url):
    try:
        r=requests.get(url)
        img=r.text.strip()
        return img
    except Exception:
        return "ERROR"