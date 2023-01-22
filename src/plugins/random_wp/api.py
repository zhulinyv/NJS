import requests
from faker import Faker
import requests
import parsel
import json
import re



random_acg = [
    # 随机壁纸(全部图)
    "https://iw233.cn/api.php?sort=random&type=json",
    "http://api.iw233.cn/api.php?sort=random&type=json",
    "http://ap1.iw233.cn/api.php?sort=random&type=json",
    "https://dev.iw233.cn/api.php?sort=random&type=json",
    # 随机壁纸(无色图)
    "https://iw233.cn/api.php?sort=iw233&type=json",
    "http://api.iw233.cn/api.php?sort=iw233&type=json",
    "http://ap1.iw233.cn/api.php?sort=iw233&type=json",
    "https://dev.iw233.cn/api.php?sort=iw233&type=json",
    # img1/2
    "https://img.moehu.org/pic.php?return=json&id=img1&num=1",
    "https://img.moehu.org/pic.php?return=json&id=img2&num=1",
    # www.eee.dog
    # "https://api.yimian.xyz/img?type=moe",
    ]

wp_top = [
    # 壁纸推荐
    "https://iw233.cn/api.php?sort=top&type=json",
    "http://api.iw233.cn/api.php?sort=top&type=json",
    "http://ap1.iw233.cn/api.php?sort=top&type=json",
    "https://dev.iw233.cn/api.php?sort=top&type=json",
    ]

white = [
    # 白毛
    "https://iw233.cn/api.php?sort=yin&type=json",
    "http://api.iw233.cn/api.php?sort=yin&type=json",
    "http://ap1.iw233.cn/api.php?sort=yin&type=json",
    "https://dev.iw233.cn/api.php?sort=yin&type=json",
    # 萌虎
    "https://img.moehu.org/pic.php?return=json&id=yin&num=1",
    ]

cat = [
    # 兽耳
    "https://iw233.cn/api.php?sort=cat&type=json",
    "http://api.iw233.cn/api.php?sort=cat&type=json",
    "http://ap1.iw233.cn/api.php?sort=cat&type=json",
    "https://dev.iw233.cn/api.php?sort=cat&type=json",
    # 萌虎
    "https://img.moehu.org/pic.php?return=json&id=kemonomimi&num=1",
    ]

star = [
    # 星空
    "https://iw233.cn/api.php?sort=xing&type=json",
    "http://api.iw233.cn/api.php?sort=xing&type=json",
    "http://ap1.iw233.cn/api.php?sort=xing&type=json",
    "https://dev.iw233.cn/api.php?sort=xing&type=json",
    # 萌虎
    "https://img.moehu.org/pic.php?return=json&id=xingk&num=1",
    ]

phone = [
    # 竖屏壁纸
    "https://iw233.cn/api.php?sort=mp&type=json",
    "http://api.iw233.cn/api.php?sort=mp&type=json",
    "http://ap1.iw233.cn/api.php?sort=mp&type=json",
    "https://dev.iw233.cn/api.php?sort=mp&type=json",
    # 萌虎
    "https://img.moehu.org/pic.php?return=json&id=sjpic&num=1",
    ]

pc = [
    # 横屏壁纸
    "https://iw233.cn/api.php?sort=pc&type=json",
    "http://api.iw233.cn/api.php?sort=pc&type=json",
    "http://ap1.iw233.cn/api.php?sort=pc&type=json",
    "https://dev.iw233.cn/api.php?sort=pc&type=json",
    # 萌虎
    "https://img.moehu.org/pic.php?return=json&id=pc&num=1",
    ]


loli = [
    # 萝莉
    "https://img.moehu.org/pic.php?return=json&id=loli&num=1",
]

bing = [
    # 必应
    "https://api.yimian.xyz/img?type=wallpaper",
]






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