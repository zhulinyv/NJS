import os
import re
import base64
import random
import nonebot
import openai
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from httpx import AsyncClient
from re import findall
from loguru import logger

try:
    ban_data_path: str = nonebot.get_driver().config.ban_data_path   # 记录 ban 冷却时间的路径
    setu_flag: bool = nonebot.get_driver().config.setu_api           # 这个值为True时, 使用的是 MirlKoi 图片
    api_num: int = nonebot.get_driver().config.api_num               # 这个值为1时, 使用的是小爱同学
    api_cd_time: int = nonebot.get_driver().config.api_cd_time       # api 冷却时间
    ban_cd_time: int = nonebot.get_driver().config.ban_cd_time       # ban 冷却时间
    api_key: str = nonebot.get_driver().config.openai_api_key        # Openai api key
    max_tokens: int = nonebot.get_driver().config.openai_max_tokens  # 返回的最大文本
    Bot_NICKNAME: str = nonebot.get_driver().config.bot_nickname     # bot的nickname,可以换成你自己的
    Bot_MASTER: str = nonebot.get_driver().config.bot_master         # bot的主人名称,也可以换成你自己的
except:
    ban_data_path: str = "./data/ban_CD"
    setu_flag: bool = True
    api_num: int = 1
    api_cd_time: int = 120
    ban_cd_time: int = 21600
    api_key: str = "寄"
    max_tokens: int = 2000
    Bot_NICKNAME: str = "脑积水"
    Bot_MASTER: str = "(๑•小丫头片子•๑)"

"""ban 使用的 json 工具"""
# read_json的工具函数
def read_json_ban() -> dict:
    try:
        with open(ban_data_path + "usercd.json", "r") as f_in:
            data = json.load(f_in)
            f_in.close()
            return data
    except FileNotFoundError:
        try:
            import os
            os.makedirs(ban_data_path)
        except FileExistsError:
            pass
        with open(ban_data_path + "usercd.json", mode="w") as f_out:
            json.dump({}, f_out)
        return {}
# write_json的工具函数
def write_json_ban(qid: str, time: int, mid: int, data: dict):
    data[qid] = [time, mid]
    with open(ban_data_path + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()
# remove_json的工具函数
def remove_json_ban(qid: str):
    with open(ban_data_path + "usercd.json", "r") as f_in:
        data = json.load(f_in)
        f_in.close()
    data.pop(qid)
    with open(ban_data_path + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()

# ban人提示语
attack_sendmessage = [
    "不理你啦，baka",
    "我给你一拳",
    "不理你啦！バーカー",
    "baka！不理你了！",
    "你在说什么呀，咱就不理你了！",
]

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource/json")) / "data.json", "r", encoding="utf8"))

# 获取resource/audio下面的全部文件
aac_file_path = os.path.join(os.path.dirname(__file__), "resource/audio")
aac_file_list = os.listdir(aac_file_path)

# hello之类的回复
hello__reply = [
    "你好！",
    "哦豁？！",
    "你好！Ov<",
    f"库库库，呼唤{Bot_NICKNAME}做什么呢",
    "我在呢！",
    "呼呼，叫俺干嘛",
]

# 从字典里返还消息, 抄(借鉴)的zhenxun-bot
async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)

# 从qinyunke_api拿到消息
async def qinyun_reply(url):
    async with AsyncClient() as client:
        response = await client.get(url)
        # 这个api好像问道主人或者他叫什么名字会返回私活,这里replace掉部分
        res = response.json()["content"].replace("林欣", Bot_MASTER).replace("{br}", "\n").replace("贾彦娟", Bot_MASTER).replace("周超辉", Bot_MASTER).replace("鑫总", Bot_MASTER).replace("张鑫", Bot_MASTER).replace("菲菲", Bot_NICKNAME).replace("dn", Bot_MASTER).replace("1938877131", "2749903559").replace("小燕", Bot_NICKNAME).replace("琪琪", Bot_NICKNAME).replace("无敌小攻", Bot_NICKNAME).replace("廖婕羽", Bot_MASTER).replace("张疯疯", Bot_NICKNAME)
        res = re.sub(u"\\{.*?\\}", "", res)
        if "taobao" in res:
            res = Bot_NICKNAME + "暂时听不懂主人说的话呢"
        return res

# 从小爱同学api拿到消息, 这个api私货比较少
async def xiaoice_reply(url):
    async with AsyncClient() as client:
        res = (await client.get(url)).json()
        if res["code"] == 200:
            return (res["data"]["txt"]).replace("小爱", Bot_NICKNAME), res["data"]["tts"]
        else:
            return "寄"


""" ChatGPT 部分"""
openai_cd_dir = {} # 空字典, 用来存放冷却时间

# 判断传入的字符串中是否有url存在(我他娘的就不信这样还能输出广告?)
def have_url(s: str) -> bool:
    index = s.find('.')     # 找到.的下标
    if index == -1:         # 如果没有.则返回False
        return False
    flag1 = (u'\u0041' <= s[index-1] <= u'\u005a') or (u'\u0061' <= s[index-1] <= u'\u007a')        # 判断.前面的字符是否为字母
    flag2 = (u'\u0041' <= s[index+1] <= u'\u005a') or (u'\u0061' <= s[index+1] <= u'\u007a')        # 判断.后面的字符是否为字母
    if flag1 and flag2:     # 如果.前后都是字母则返回True
        return True
    else:               # 如果.前后不是字母则返回False
        return False

def get_openai_reply(prompt:str)->str:
    openai.api_key = api_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    res = response.choices[0].text
    # 移除所有开头的\n
    while res.startswith("\n"):
        res = res[1:]
    return res


# 获取涩图(P站)
async def get_setu() -> list:
    async with AsyncClient() as client:
        req_url = "https://api.lolicon.app/setu/v2"
        params = {
            "r18": 0,
            "size": "regular",
            "proxy": "i.pixiv.re",
        }
        res = await client.get(req_url, params=params, timeout=120)
        logger.info(res.json())
        setu_title = res.json()["data"][0]["title"]
        setu_url = res.json()["data"][0]["urls"]["regular"]
        content = await down_pic(setu_url)
        setu_pid = res.json()["data"][0]["pid"]
        setu_author = res.json()["data"][0]["author"]
        base64 = convert_b64(content)
        if type(base64) == str:
            pic = "[CQ:image,file=base64://" + base64 + "]"
            data = (
                "标题:"
                + setu_title
                + "\npid:"
                + str(setu_pid)
                + "\n画师:"
                + setu_author
            )
        return [pic, data, setu_url]
async def down_pic(url):
    async with AsyncClient() as client:
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        re = await client.get(url=url, headers=headers, timeout=120)
        if re.status_code == 200:
            logger.success("成功获取图片")
            return re.content
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return re.status_code
def convert_b64(content) -> str:
    ba = str(base64.b64encode(content))
    pic = findall(r"\'([^\"]*)\'", ba)[0].replace("'", "")
    return pic

# 戳一戳消息
poke_reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    f"请不要戳{Bot_NICKNAME} >_<",
    "放手啦，不给戳QAQ",
    f"喂(#`O′) 戳{Bot_NICKNAME}干嘛！",
    "戳坏了，赔钱！",
    "戳坏了",
    "嗯……不可以……啦……不要乱戳",
    "那...那里...那里不能戳...绝对...",
    "(。´・ω・)ん?",
    "有事恁叫我，别天天一个劲戳戳戳！",
    "欸很烦欸！",
    "再戳一下试试？",
    "正在关闭对您的所有服务...关闭成功",
    "啊呜，太舒服刚刚竟然睡着了。什么事？",
    "正在定位您的真实地址...定位成功。轰炸机已起飞",
    "悄悄告诉你，我只允许你一个人戳哦~",
    "唔姆姆，不许再戳咱了！",
    f"呜...不可以戳{Bot_NICKNAME}>_<",
    "别戳了别戳了再戳就坏了555",
    "呜...不要用力戳咱...好疼>_<",
]

# 藏话
curse=[
    "nm",
    "色批",
    "泥马",
    "病",
    "尼玛",
    "傻鸟",
    "傻狗",
    "狗",
    "儿子",
    "爹",
    "爸爸",
    "猪",
    "沙雕",
    "卧槽",
    "二臂",
    "爷爷",
    "有病",
    "MD",
    "啥鼻",
    "沙鼻",
    "鲨笔",
    "戳那吗B",
    "鲵🐴",
    "塞你公",
    "溺🐎",
    "雜種",
    "杀你",
    "他NND",
    "妳奶奶",
    "操死妳妹",
    "on狗",
    "妈B",
    "强奸",
    "操妳妹",
    "甚麼寄八",
    "傻B",
    "驶你母",
    "臭婊",
    "mdzz",
    "奸淫",
    "雞姦",
    "抽你丫的",
    "妈个B",
    "操死你母",
    "跡掰",
    "ㄐ掰",
    "你爺",
    "輪姦",
    "他媽",
    "她妈",
    "🐴🐴",
    "什麼勾巴",
    "shabi",
    "甚麼勾八",
    "妳全家",
    "狗b",
    "狗交",
    "甚麼勾巴",
    "妳爺",
    "妈个b",
    "賤種",
    "睨🐎",
    "你大爺",
    "老味",
    "你它妈",
    "瘪三",
    "幹死你妹",
    "哩娘",
    "妳媽",
    "嫩叠",
    "幹爆妳母",
    "操你母",
    "几把玩意",
    "X妈",
    "表子",
    "怩🐎",
    "龜公",
    "nmsl",
    "賤屄",
    "你马",
    "冚家",
    "狗日",
    "草泥马",
    "乱奸",
    "他ㄇㄉ",
    "乡巴佬",
    "你祖宗",
    "匿🐴",
    "死屄",
    "什么鸡扒",
    "林北",
    "死雞巴",
    "輪奸",
    "草拟妈",
    "吃屎",
    "幹暴你妹",
    "殺你",
    "倪🐴",
    "蠢猪",
    "JB玩意",
    "草妈",
    "你奶奶",
    "草你吗",
    "D区",
    "傻b",
    "东亚病夫",
    "给爷爬",
    "ㄐㄅ",
    "績掰",
    "甚么勾巴",
    "幹你梁",
    "on鳩",
    "瘪犊子",
    "伱妈",
    "smj8",
    "滾那嗎B",
    "猊🐎",
    "呢🐎",
    "幹您老幕",
    "什麼鸡扒",
    "呆比",
    "操死你妹",
    "賣淫",
    "塞你老师",
    "腻🐎",
    "你媽",
    "擬娘",
    "尼🐴",
    "草拟吗",
    "撞死你",
    "smjb",
    "什麼寄八",
    "你老木",
    "下賤",
    "食撚",
    "靠爸",
    "奸她",
    "睨🐴",
    "戇鳩",
    "妮🐎",
    "屠你",
    "烂逼",
    "操死妳母",
    "妓女",
    "b样",
    "创死你",
    "奸你",
    "屌毛",
    "陷家",
    "婊子",
    "鸡巴玩意",
    "呆卵",
    "jiba玩意",
    "強奸",
    "倪🐎",
    "什么鸡八",
    "他妈",
    "您娘",
    "她馬的",
    "賤婊",
    "ㄖ",
    "你吗b",
    "sabi",
    "弱智",
    "什麼勾吧",
    "姦污",
    "甚么寄吧",
    "傻比",
    "我妳老爸",
    "他娘的",
    "老婊",
    "去死",
    "你妈",
    "她马的",
    "那嗎逼",
    "你馬的",
    "吗的",
    "操死妳爸",
    "什么鸡巴",
    "Biaozi",
    "幹死妳爸",
    "插那吗B",
    "什么寄吧",
    "幹爆你妹",
    "甚么鸡八",
    "崽种",
    "雞奸",
    "2b",
    "么有🐎",
    "先奸后杀",
    "妈的",
    "幹林",
    "脑瘫",
    "你全家",
    "鲵🐎",
    "逆🐴",
    "機掰",
    "靠盃",
    "什麼鸡八",
    "煞笔",
    "爛雞",
    "旎🐎",
    "幹死妳母",
    "拟🐎",
    "霓🐎",
    "鸡掰",
    "妳妈",
    "臭屄",
    "甚么勾吧",
    "雞掰",
    "日你老娘",
    "好撚廢",
    "她媽的",
    "shenmejiba",
    "激掰",
    "干妳马",
    "你爹",
    "妳馬",
    "尼🐎",
    "幹你母",
    "干x娘",
    "啞撚",
    "死婊",
    "赛妳阿母",
    "吗逼",
    "妳娘",
    "泥🐴",
    "你爸",
    "甚么勾八",
    "妈逼",
    "瘠薄玩意",
    "砍死你",
    "滚犊子",
    "志葬",
    "操妳爸",
    "诱奸",
    "妈批",
    "爛屄",
    "拟🐴",
    "甚麼雞扒",
    "呢🐴",
    "卖比",
    "什么勾巴",
    "卖批",
    "on九",
    "你二大爺",
    "批样",
    "妳老母",
    "别他吗",
    "龟公",
    "驶你公",
    "你八辈祖宗",
    "你麻痹",
    "強姦",
    "他奶奶",
    "幹暴你母",
    "小比樣",
    "甚么鸡扒",
    "比样",
    "妳马的",
    "什麼雞扒",
    "滥逼",
    "幹妳爸",
    "🐎🐎",
    "nnd",
    "什麼勾八",
    "贱比",
    "jb玩意",
    "你姥",
    "幹暴妳妹",
    "杀b",
    "tmd",
    "煞逼",
    "甚么雞扒",
    "女干",
    "脑残",
    "甚么鸡巴",
    "甚麼鸡扒",
    "塞林木",
    "她NND",
    "幹爆妳妹",
    "贱b",
    "娘西皮",
    "你二大爷",
    "赛林木",
    "CNM",
    "烂臭嗨",
    "戇狗",
    "王巴",
    "野雞",
    "你大爷",
    "含撚",
    "甚麼鸡八",
    "幹你良",
    "虐杀",
    "妳祖宗",
    "戇九",
    "口区",
    "草擬媽",
    "幹死你母",
    "你爷",
    "幹妳母",
    "操你妹",
    "没用东西",
    "狗幹",
    "幹你妹",
    "他嗎的",
    "nmbiss",
    "二逼",
    "腻🐴",
    "塞你母",
    "基掰",
    "你娘",
    "cnm",
    "你🐴",
    "鹹家鏟",
    "操你老妈",
    "轮姦",
    "贱B",
    "賤貨",
    "幹爆你母",
    "你🐎",
    "什麼鸡巴",
    "卖逼",
    "你老母",
    "没🐎",
    "奶奶的",
    "没🐴",
    "他ㄇ的",
    "什么勾吧",
    "積掰",
    "TMD",
    "什麼寄吧",
    "烂批",
    "她娘",
    "全家死",
    "吊佢佬未",
    "烂比",
    "sb",
    "小B樣",
    "匿🐎",
    "什么雞扒",
    "騷媽",
    "吊你好撚",
    "B样",
    "什么勾八",
    "操妳母",
    "妳爹",
    "Sb",
    "旎🐴",
    "操你老娘",
    "甚么寄八",
    "霓🐴",
    "SB",
    "干你良",
    "傻吊",
    "怩🐴",
    "迷奸",
    "甚麼鸡巴",
    "废物",
    "幹暴妳母",
    "臭b",
    "杂种",
    "王八",
    "小雞巴",
    "錶子",
    "幹爆妳爸",
    "甚麼勾吧",
    "老娼",
    "溺🐴",
    "昵🐎",
    "on9",
    "傻卵",
    "贱逼",
    "什么寄八",
    "贱种",
    "轮奸",
    "駛你母",
    "傻逼",
    "机掰",
    "它媽",
    "戇9",
    "二B",
    "昵🐴",
    "幹死妳妹",
    "猊🐴",
    "死全家",
    "鸡奸",
    "刹笔",
    "么有🐴",
    "龜兒子",
    "🐔🎱",
    "狗娘",
    "驶你老师",
    "泥🐎",
    "狗比",
    "妮🐴",
    "逼样",
    "靠北",
    "幹暴妳爸",
    "您妈",
    "爛婊",
    "狗操",
    "ㄙㄞ",
    "逆🐎",
    "没种",
    "rnm",
    "狗种",
    "死妈",
    "没有🐎",
    "他马的",
    "拎娘",
    "臭表",
    "没有🐴",
    "沙比",
    "甚麼寄吧"
  ]

logo = """
                                   '-^+)+^,-'''--'.
                              '"=OPO****UU**=))((==+"-.
                            )SE9D*(+^^^+++)(=*=)^)=*=+,"-
                          )9#P=+^++))))+)++(+)=U=+++=*+,"^-
                        -USD==+))+*(+++())+*U+(***+)+=U=".,^
                       ^DO=(U(+)+=O++)+=*+)+O=+(U*U",-'('  -(
                      ^D)((O)+*=^O(+)+)*O))+**++=OU^-^,")'. '(
                     'U,^ U,"(*+)O+)+)+*D*++(P+)^USO)))+**+)'-+
                     ,^="(*^+**+(O+)+++)DO+++9=++(9E)+++)U+)(')'
                     ^-O+O(++*D(+O++)+)+OP)=*OO++(PG(+=))U)))^,)
                     '-O^O(++*OO=DU+)+)+*P=**-**(=P#+^O=+U)*))^O.
                     '-O^**^+=PD(*3+)++^*P=U= +O*O*P,^UP^O)U=+^*-
                     ='O)+O=+^OU*USO*==)PP9GE#M8MMP*-+=S(*==D+++,
                     U'=O^)O3PE8Q88P)^U)*,-DBEDUEW9E-^*D*=*)S=+++
                     =+'9*++ESWMO+P9        *=^"*M"3",PO***^PU++(
                     -= *3+^S*'=O^(#        UO((US"P,,SO=D=+OO(^='
                     .=',9*,UW )O(UU        '"==,')D,^SO^P=^*U*^=-
                      ="-U3^)8)."="           '+))*O^^ES"*=^***=)+
    ."+"              U)^)E=^ME,,'               '9O^)#P,=)+)O)U=*
    )''U              *=^)3D,PGU,-      '     ')DEO)^=EO^U^)^*U+*O=
   'O-'*'            '**+(D3(POPS3SO*(^---,=DE#Q@P"))*SO^P,))+O=+*3-
   ^,"-)D,.          ,=*+*=D*S*ODDP9#EE#EME#3O,=8+"UOU##^S(-(+)O(^*O.
 -.     (U*          (,O)O+U*D^D999P9##SEW+   =9P'UP*SS3U*9.,(+(O=,*U'
'(       )E         '(,U=O**U=*9MM=*PPPSO+  +39E(^SU=P*O3=SU'")+(U=))=^
 +.      -M=U#P*    (-(*O*+DSP3E#O^UPPSS  -DEPOS,*3=+O3EDED9U^^+++(**)+,-
 '=-  '",OD,UMPE3*++- =^='"OSP3EP*,*SD#" =3P**OP=***=-'*E9SDO*)(=("-=*. "^
  'E#PPP*=)=3E9O3EEMP*3OSP*,=SSE*OU^U9S-UO**U*(-=O)=*=-PEPPP3P*====*^O("'"^
   '3#O*UOPPPPSPPDDDE#9SPPEP+D##D-=*+D#DU=)"''^O3P*+*U*=3PPPP#O*=*(P=O()).+'
    -##E3SPPPPPPPPPPDE3PPSSD*S#PSPOP9#9UO*=OPEE93S#3UP*OSPPPD3E*O*P=UO+++=='
     '=OS93SPPDPPPPPP3#PS*=U39PPPPEG##EE3S3#PPPPPSOUPP9PPPPPP33OO=+=O+^(OD-
        '+*ODP3SPPPPPPPS*'O8GPPPPSS*(*=EPPP9DPPPD3*))OSPPPPPDEO3(+^UU==OS,
             )OPDS33P3P3#**8#DPPP9++ = DSPPPSSPS9EEPOPPEE9PPPEOE)+)=U**UP*)"
            -+ =*+-=**P=O*OOS39PE^.* ) =EDPPP333SDSWPDPSPPPP9#PP*(+,+)*+(U-^)
            '(^(US=(D^=U*SOD3S3SP  *-  ,EPPPPPPPPP#E9=+3PPPES#OUU*++),)O,P*'*-"""
