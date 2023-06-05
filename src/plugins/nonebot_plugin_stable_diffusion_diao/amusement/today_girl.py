from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot, ActionFailed, PrivateMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from ..backend import AIDRAW
from ..extension.translation import translate_deepl, translate
from ..extension.daylimit import count
from ..config import config
from ..utils.data import basetag, lowQuality
from ..utils.save import save_img
from ..aidraw import get_message_at
from ..extension.explicit_api import check_safe_method

import random, time, json, re, base64, aiohttp, aiofiles


today_girl = on_command("二次元的")

prompt_dict = { # 来自https://github.com/pcrbot/ai_setu
    "画质": {
        "格子的": "checkered",
        "高分辨率": "highres",
        "超高分辨率": "absurdres",
        "极高分辨率": "incredibly_absurdres",
        "超级高分辨率大文件": "huge_filesize",
        "壁纸": "wallpaper",
        "点阵图": "pixel_art",
        "单色图片": "monochrome",
        "色彩斑斓的": "colorful"
    },
    "优秀实践": {
        "1个女孩": "1girl",
        "solo": "solo",
        "全身": "full body",
        "一个极其娇嫩美丽的女孩": "an extremely delicate and beautiful girl",
        "非常详细2": "extremely detailed",
        "花丛": "flowering shrubs",
        "极其精致和美丽": "an extremely delicate and beautiful",
        "细节的水": "starry detailed water",
        "细节的天空": "beautiful detailed starry sky",
        "美丽细腻的眼睛": "beautiful detailed eyes",
        "裸露的肩膀": "bare shoulders",
        "8k壁纸": "8k_wallpaper",
        "上半身": "upper_body",
        "详细冰": "detailed ice",
        "世界杰作剧院": "world masterpiece theater",
        "繁花草甸": "Flowery meadow",
        "秃积雨云": "cumulonimbus calvus",
        "鬃积雨云": "cumulonimbus capillatus",
        "璀璨星空": "Bright stars",
        "大前额": "big forhead",
        "黑色丝带": "black ribbon",
        "小乳房5": "small breast",
        "漏光": "light_leaks",
        "最佳插图": "best illustration",
        "大号上衣袖子": "large top sleeves",
        "动态角度": "dynamic angle",
        "长刘海": "long bangs",
        "focus on face": "focus_on_face",
        "navel": "navel",
        "过度暴露": "overexposure",
        "星空": "starry sky",
        "美丽的细节辉光": "beautiful detailed glow",
        "侧面钝刘海": "side blunt bangs",
        "蓝眼睛": "blue eyes",
        "机器人女孩": "robot girl",
        "随机分布的云": "randomly distributed clouds",
        "闪耀": "shine",
        "虚饰": "frills",
        "机甲服": "mecha clothes",
        "眼睛之间的毛发": "hairs between eyes",
        "蓝色头发": "azure hair",
        "超详细的": "ultra-detailed",
        "美丽详细的天空7": "beautiful detailed sky",
        "动漫脸": "anime face",
        "天蓝色连衣裙": "skyblue dress",
        "凌乱的长发": "messy_long_hair",
        "发光的眼睛": "glowing eyes",
        "冰晶纹理翅膀": "ice crystal texture wings",
        "非常详细的CG unity 8k壁纸": "extremely detailed CG unity 8k wallpaper",
        "最好的质量3": "best quality",
        "蝴蝶结2": "bowties",
        "插图": "illustration",
        "中胸": "medium_breast",
        "阳光": "sunlight",
        "森林": "forest",
        "茫然凝视": "blank stare",
        "中音": "midriff",
        "绘画": "painting",
        "景深": "Depth of field",
        "明亮的眼睛": "bright_eyes",
        "黑色膝盖": "black kneehighs",
        "1个女孩2": "1 girl",
        "半闭着的眼睛": "half closed eyes",
        "精细的细节": "finely detail",
        "最佳阴影": "best shadow",
        "戏剧性角度": "dramatic_angle",
        "鲜花": "flowers",
        "墨水": "ink",
        "红色的眼睛": "red eyes",
        "红色的月亮": "red moon",
        "中等乳房": "medium_breasts",
        "燃烧": "burning",
        "非常详细的CG": "extremely detailed CG",
        "洛丽": "loli",
        "高等教育": "highres",
        "细节照明": "detailed light",
        "景深2": "depth of field",
        "面纱": "veil",
        "素描": "sketch",
        "裸肩": "bare_shoulder",
        "漂亮细心的女孩": "beautiful detailed girl",
        "查看查看器4": "looking at viewer",
        "red hair": "red hair",
        "漂浮的头发": "floating hair",
        "非常接近观众": "very_close_to_viewers",
        "水彩介质": "watercolor_medium",
        "观看观众": "looking_at_viewers",
        "花": "flower",
        "羽毛": "feather",
        "河": "river",
        "美丽细腻的水": "beautiful detailed water",
        "自然界": "nature",
        "非常细致的眼睛和脸": "extremely_detailed_eyes_and_face",
        "水彩": "watercolor",
        "太神了2": "Amazing",
        "大袖上衣": "big top sleeves",
        "无表情的": "expressionless",
        "开花": "bloom",
        "黑暗魔术师女孩": "dark magician girl",
        "按钮": "buttons",
        "漂亮精致的白色手套": "beautiful detailed white gloves",
        "白色蝴蝶结": "white bowties",
        "风": "wind",
        "缎带": "ribbons",
        "杰作": "masterpiece",
        "透镜光斑": "lens_flare",
        "美丽而精致的水": "beautiful and delicate water",
        "微风": "breeze",
        "独奏": "solo",
        "电影照明2": "cinematic lighting",
        "褶皱裙": "pleated skirt",
        "蓬乱的头发": "disheveled hair",
        "白色1": "hiten_1",
        "日落": "sunset",
        "浮动": "floating",
        "白发": "white_hair"
    },
    "负面实践": {
        "欧维斯": "owres",
        "畸形肢体": "malformed limbs",
        "绘制不良": "poorly drawn",
        "画得不好的手": "poorly drawn hands",
        "残缺不全的": "mutilated",
        "jpegartifacts": "jpegartifacts",
        "2条以上大腿": "more than 2 thighs",
        "文本": "text",
        "2个以上乳头": "more than 2 nipples",
        "眼睛不清": "unclear eyes",
        "缺腿": "missing legs",
        "mutated hands and fingers": "mutated hands and fingers ",
        "变形的，变形的": "deformed",
        "fused fingers": "fused fingers",
        "缺少fngers": "missing fngers",
        "绘制不良的面": "poorly drawn face",
        "用户名": "username",
        "额外的支腿": "extra legs",
        "坏面孔": "bad face",
        "多乳房": "multiple breasts",
        "畸形的": "malformed",
        "长机身2": "long body",
        "jpeg工件3": "jpeg artifacts",
        "洛尔": "lowres",
        "肢": "limb",
        "wort quality ": "wort quality ",
        "福塔": "futa",
        "丢失的手指": "missing fingers",
        "水印": "watermark",
        "变异的手和手指": "mutated hands and fingers",
        "特兰尼": "tranny",
        "降低": "lowers",
        "突变绘制不佳：1.2": "mutation poorly drawn",
        "三条腿": "three legs",
        "克隆的脸": "cloned face",
        "畸形突变": "malformed mutated",
        "解剖结构不良畸形变异": "bad anatomy disfigured malformed mutated",
        "比例不好": "bad proportions",
        "签名": "signature",
        "更少的数字": "fewer digits",
        "复制": "duplicate",
        "脚不好": "bad feet",
        "帧外": "out of frame",
        "最差品质": "worstquality",
        "poorly drawn": "poorly drawn",
        "艺术家姓名": "artist name",
        "突变3": "mutation",
        "裸体": "nude",
        "大乳房": "large breasts",
        "毁容的": "disfigured",
        "低质量": "low quality",
        "套筒": "Sleeveles",
        "最差质量": "worst quality",
        "驼背的3": "Humpbacked",
        "坏手": "bad hands",
        "裁剪过的": "cropped",
        "正常质量": "normal quality",
        "额外的肢体": "extra limbs",
        "变异的": "mutated",
        "丑陋的": "ugly",
        "变异的手": "mutated hands",
        "手指太多": "too many fingers",
        "融合肛门": "fused anus",
        "文本字体用户界面": "text font ui",
        "错误": "error",
        "畸形手": "malformed hands",
        "extra digt ": "extra digt ",
        "雅依": "yaoi",
        "缺失的肢体": "missing limb",
        "病态的": "morbid",
        "新南威尔士州": "nsfw",
        "mutation ": "mutation ",
        "额外的武器": "extra arms",
        "丢失的手臂": "missing arms",
        "三个手臂": "three arms",
        "长机身": "long body",
        "解剖结构不好": "bad anatomy",
        "缺少肢体": "Missing limbs",
        "长脖子": "long neck",
        "模糊不清的": "blurry",
        "额外数字": "extra digit"
    },
    "风格": {
        "原画": "artbook",
        "游戏": "game_cg",
        "漫画": "comic",
        "四格": "4koma",
        "格式图片": "animated_gif",
        "抱枕": "dakimakura",
        "角色扮演": "cosplay",
        "穿越": "crossover",
        "暗的": "dark",
        "亮的": "light",
        "猎奇": "guro",
        "写实": "realistic",
        "照片": "photo",
        "真实": "real",
        "风景": "landscape/scenery",
        "城市风景": "cityscape",
        "科技幻想": "science_fiction",
        "原创": "original",
        "拙劣的模仿": "parody",
        "拟人": "personification",
        "视觉错误": "optical_illusion",
        "名画模仿": "fine_art_parody",
        "素描": "sketch",
        "传统媒体（基本上是手绘稿）": "traditional_media",
        "透明水彩绘": "watercolor_(medium)",
        "剪影": "silhouette",
        "封面": "covr",
        "专辑": "album",
        "图上有字样": "sample",
        "背影像": "back",
        "半身像": "bust",
        "侧面绘": "profile",
        "表情绘（各种表情）": "expressions",
        "一部作品中的主要人物集齐": "everyone",
        "一列列小图组成大图": "column_lineup",
        "透明的背景": "transparent_background",
        "简单的背景无背景": "simple_background",
        "渐变的背景": "gradient_background",
        "背景是前景的放大版": "zoom_layer"
    },
    "头发": {
        "短发": "short hair",
        "卷发": "curly_hair",
        "长发": "long hair",
        "马尾": "pony-tail",
        "双马尾": "twintails",
        "挑染": "streaked hair",
        "灰色渐变": "grey gradient hair",
        "亮棕": "light brown hair",
        "双色": "two-tone hair",
        "五颜六色": "multicolored hair",
        "高马尾": "high ponytail",
        "马尾编发": "braided ponytail ",
        "马尾辫": "ponytail",
        "短马尾": "short_ponytail",
        "双辫子": "twin_braids",
        "中发": "medium hair",
        "超长发": "very long hair",
        "辫子刘海": "braided bangs",
        "侧扫刘海": "swept bangs",
        "眼间头发": "hair between eyes",
        "妹妹切": "bob cut",
        "公主切": "hime_cut",
        "交叉刘海": "crossed bangs",
        "刘海": "bangs",
        "齐刘海": "blunt bangs",
        "翼状头发": "hair wings",
        "长刘海": "long bangs",
        "蓬发": "disheveled hair",
        "波浪形头发": "wavy hair",
        "收拢": "hair in takes",
        "粉色花": "hair pink flowers",
        "呆毛": "ahoge",
        "多根呆毛": "antenna hair",
        "侧马尾": "Side ponytail",
        "露额头": "forehead",
        "钻头卷公主卷": "drill hair",
        "包子头": "hair bun",
        "俩包子头": "double_bun",
        "凌乱发型": "messy_hair"
    },
    "发色": {
        "白": "white hair",
        "金": "blonde hair ",
        "银": "silver hair",
        "灰": "grey hair ",
        "紫": "purple hair",
        "红": "red hair",
        "黄": "yellow hair",
        "绿": "green hair",
        "蓝": "blue hair",
        "黑": "black hair",
        "棕": "brown hair"
    },
    "衣服": {
        "晚礼服": "evening dress",
        "短裙": "Skirt",
        "长裙": "Long skirt",
        "水手服": "shorts under skirt",
        "JK": "JK",
        "黑色丝袜": "black silk stocking",
        "白色丝袜": "white silk stocking",
        "西装": "suit",
        "湿衣服": "wet clothes",
        "比基尼": "bikini",
        "领子": "sailor collar",
        "帽子": "hat",
        "衬衫": "shirt",
        "有领衬衣": "collared shirt ",
        "学校制服": "school uniform",
        "日本学生服": "seifuku",
        "职场制服": "business_suit",
        "夹克": "jacket",
        "火焰纹章军服": "garreg mach monastery uniform",
        "礼服长裙": "revealing dress",
        "礼服": "pink lucency full dress",
        "露出胸口部分的连衣裙": "cleavage dress",
        "无袖连衣裙": "sleeveless dress",
        "白色连衣裙": "whitedress",
        "婚纱": "wedding_dress",
        "水手连衣裙": "Sailor dress",
        "毛衣裙": "sweater dress",
        "罗纹毛衣": "ribbed sweater",
        "毛衣夹克": "sweater jacket",
        "工装服": "dungarees",
        "棕色开襟衫（外套）": "brown cardigan ",
        "连帽衫，卫衣": "hoodie ",
        "长袍": "robe",
        "斗篷": "cape",
        "羊毛衫": "cardigan",
        "围裙": "apron",
        "哥特风格": "gothic",
        "洛丽塔风格": "lolita_fashion",
        "哥特洛丽塔风格": "gothic_lolita",
        "西部风格": "western",
        "格子花纹": "tartan",
        "露单肩": "off_shoulder",
        "露双肩": "bare_shoulders",
        "赤脚": "barefoot",
        "裸足": "bare_legs",
        "横条花纹的": "striped",
        "点状花纹的": "polka_dot",
        "皱边的": "frills",
        "花边": "lace",
        "日本女生运动短裤": "buruma",
        "运动服": "gym_uniform",
        "女用背心": "tank_top",
        "裁剪短夹克": "cropped jacket ",
        "运动胸罩": "black sports bra ",
        "漏脐装": "crop top",
        "睡衣": "pajamas",
        "和服": "japanese_clothes",
        "衣带和服用": "obi",
        "网眼上衣": "mesh",
        "无袖上衣": "sleeveless shirt",
        "袖肩分离装": "detached_sleeves",
        "白色灯笼裤": "white bloomers",
        "高腰腿裤": "high - waist shorts",
        "百褶裙": "pleated_skirt",
        "裙子": "skirt",
        "迷你裙": "miniskirt",
        "热裤": "short shorts",
        "夏日长裙": "summer_dress",
        "灯笼裤": "bloomers",
        "短裤": "shorts",
        "自行车短裤": "bike_shorts",
        "海豚短裤": "dolphin shorts",
        "腰带": "belt",
        "吊索比基尼": "sling bikini",
        "比基尼乳罩": "bikini_top",
        "上身比基尼": " bikini top only ",
        "侧边系带比基尼下装": "side - tie bikini bottom",
        "系带式比基尼": "side-tie_bikini",
        "褶边比基尼": "friled bikini",
        "比基尼内衣": " bikini under clothes",
        "泳装": "swimsuit",
        "学校泳衣": "school swimsuit",
        "连体泳衣": "one-piece swimsuit",
        "竞技泳衣": "competition swimsuit",
        "死库水": "Sukumizu",
        "没胸罩": "no bra",
        "胸罩": "bra ",
        "褶边文胸": "frilled bra ",
        "情趣内衣": "sexy lingerie",
        "透明内衣": "transparent underwear",
        "缠胸布": "sarashi",
        "胸衣": "bustier",
        "吊带胸衣": "chemise",
        "内衣": "underwear",
        "内裤（前加颜色）": "panties",
        "条纹内裤": "striped_panties",
        "没内裤": "no_panties",
        "低腰式内裤": "lowleg_panties/low_leg_panties",
        "侧系带内裤": "side-tie_panties",
        "高腰内裤": "string_panties",
        "丁字裤": "thong",
        "日式丁字裤": "fundoshi",
        "女用贴身内衣裤": "lingerie"
    },
    "鞋子": {
        "鞋子": "shoes ",
        "靴子": "boots",
        "乐福鞋": "loafers",
        "高跟鞋": "high heels",
        "系带靴": "cross-laced_footwear",
        "玛丽珍鞋": "mary_janes",
        "女式学生鞋": "uwabaki",
        "拖鞋": "slippers",
        "马靴": "knee_boots",
        "连裤袜": "pantyhose",
        "大腿连裤袜": "thighband pantyhose",
        "连腰吊带袜": "garter_belt",
        "吊带袜": "garter straps",
        "短袜": "socks",
        "横条袜": "striped_socks",
        "泡泡袜": "loose_socks",
        "裹腿": "legwear",
        "黑色紧身裤": "black leggings ",
        "裤袜": "leggings ",
        "网袜": "fishnets",
        "渔网袜": "fishnet_pantyhose",
        "长袜": "kneehighs",
        "丝袜": "stockings",
        "过膝袜": "thighhighs",
        "条纹过膝袜": "striped_thighhighs",
        "白色过膝袜": "white_thighhighs",
        "损坏了的过膝袜": "torn_thighhighs",
        "日式厚底短袜": "tabi",
        "蕾丝镶边紧身裤": "lace-trimmed legwear",
        "腿部花边环": "leg_garter",
        "腿部系带": "ankle_lace-up",
        "大腿系带": "thigh strap",
        "短裤下的紧身裤": "legwear under shorts"
    },
    "装饰": {
        "光环": "halo",
        "迷你礼帽": "mini_top_hat",
        "贝雷帽": "beret",
        "兜帽": "hood",
        "护士帽": "nurse cap",
        "皇冠": "tiara",
        "鬼角": "oni horns",
        "恶魔角": "demon horns",
        "发带": "hair_ribbon",
        "花丝带": "flower ribbon",
        "发卡": "hairband",
        "发夹": "hairclip",
        "发花": "hair_flower",
        "头饰": "hair_ornament",
        "蝴蝶结": "bowtie",
        "蝴蝶结发饰": "hair_bow",
        "女仆头饰": "maid_headdress",
        "服装饰品头部饰品": "bow",
        "发饰": "hair ornament",
        "心形": "heart hair ornament",
        "创可贴": "bandaid",
        "锥形发髻": "cone hair bun",
        "双发髻": "double bun",
        "半无框的眼镜": "semi-rimless eyewear",
        "太阳镜": "sunglasses",
        "风镜": "goggles",
        "眼罩独眼": "eyepatch",
        "黑色眼罩": "black blindfold",
        "耳机": "headphones",
        "面纱": "veil",
        "口罩": "mouth mask",
        "眼镜": "glasses",
        "耳环": "earrings",
        "首饰": "jewelry",
        "铃铛": "bell",
        "颈带": "ribbon_choker",
        "颈部饰品": "black choker ",
        "项链": "necklace",
        "耳机套脖子上": "headphones around neck",
        "项圈": "collar",
        "水手领": "sailor_collar",
        "领巾": "neckerchief",
        "领带": "necktie",
        "十字架": "cross necklace",
        "吊坠": "pendant",
        "围巾": "scarf",
        "臂章": "armband",
        "臂环": "armlet",
        "臂带": "arm strap",
        "肘部手套": "elbow gloves ",
        "露指手套": "half gloves ",
        "手镯": "bracelet",
        "手套": "gloves",
        "五指手套": "fingerless gloves",
        "锁链": "chains",
        "手链": "shackles",
        "手铐": "handcuffs",
        "手表": "wristwatch",
        "腕带": "wristband",
        "腕饰": "wrist_cuffs",
        "拿着书": "holding book",
        "拿着剑": "holding sword",
        "球拍": "tennis racket",
        "手杖": "cane",
        "双肩包": "backpack",
        "书包": "school bag ",
        "肩背书包": "satchel",
        "手机": "smartphone "
    },
    "胸": {
        "ACUP": "flat_chest",
        "BCUP": "small_breasts",
        "CCUP": "medium breasts",
        "DCUP": "huge breasts",
        "ECUP": "large_breast",
        "FCUP": "large_breast",
        "GCUP": "gigantic breasts",
        "惊天巨乳": "gigantic breasts",
        "飞机场": "flat_cheast"
    },
    "类型": {
        "小女孩": "little girl",
        "小男孩": "little boy",
        "正太": "shota",
        "萝莉": "loli",
        "可爱": "kawaii",
        "雌小鬼": "mesugaki",
        "可爱的女孩": "adorable girl",
        "美少女": "bishoujo",
        "辣妹": "gyaru",
        "姐妹": "sisters",
        "大小姐": "ojousama",
        "成熟女性": "mature female",
        "成熟": "mature",
        "痴女": "female pervert",
        "熟女": "milf"
    },
    "身份": {
        "女王": "queen",
        "学生": "student",
        "医生": "doctor",
        "护士": "nurse",
        "警察": "police",
        "士兵": "soldier",
        "骑士": "knight",
        "女仆": "housemaid",
        "天使": "angel",
        "啦啦队": "cheerleader",
        "版人物": "chibi",
        "伪娘": "trap",
        "魔鬼": "devil",
        "人偶": "doll",
        "妖精": "elf",
        "小精灵": "fairy",
        "女人": "female",
        "兽人": "furry",
        "半兽人": "orc",
        "女巨人": "giantess",
        "后宫": "harem",
        "偶像": "idol",
        "兽耳萝莉模式": "kemonomimi_mode",
        "魔法少女": "magical_girl",
        "男人": "male",
        "美人鱼": "mermaid",
        "巫女": "miko",
        "迷你女孩": "minigirl",
        "怪物": "monster",
        "魔幻少女": "multiple_girls",
        "忍者": "ninja",
        "非人": "no_humans",
        "修女": "nun",
        "空姐": "stewardess",
        "吸血鬼": "vampire",
        "女服务员": "waitress",
        "女巫": "witch",
        "搞基": "yaoi",
        "油库里": "yukkuri_shiteitte_ne",
        "百合": "yuri"
    },
    "表情": {
        "微笑": "smirk",
        "诱惑笑": "seductive smile",
        "露齿而笑": "grin",
        "笑": "laughing",
        "牙": "teeth ",
        "兴奋": "excited",
        "害羞": "nose blush ",
        "脸红": "blush",
        "无表情": "expressionless",
        "失神": "expressionless eyes",
        "困": "sleepy",
        "喝醉的": "drunk",
        "哭": "crying with eyes open",
        "悲伤的": "sad",
        "别扭努嘴": "pout",
        "叹气": "sigh",
        "睁大眼睛": "wide eyed",
        "生气": "angry",
        "苦恼的": "annoyed",
        "皱眉": "frown",
        "严肃": "serious",
        "鄙夷": "jitome",
        "锐利": "scowl",
        "疯狂的": "crazy",
        "黑化的": "dark_persona",
        "得意": "smug",
        "一只眼睛闭上": "one eye closed",
        "半闭眼睛": "half-closed eyes",
        "鼻血": "nosebleed",
        "做鬼脸": "eyelid pull ",
        "舌头": "tongue",
        "吐舌": "tongue out",
        "闭嘴": "closed mouth",
        "张嘴": "open mouth",
        "口红": "lipstick",
        "尖牙": "fangs",
        "咬紧牙关": "clenched teeth",
        "ω猫嘴": ":3",
        "向下吐舌头": ":p",
        "向上吐舌头": ":q",
        "不耐烦": ":t",
        "杯型笑脸": ":d",
        "下流的表情": "naughty_face",
        "忍耐的表情": "endured_face",
        "阿黑颜": "ahegao",
        "血在脸上": "blood on face",
        "唾液": "saliva"
    },
    "二次元": {
        "食物在脸上（食物可替换）": "food on face",
        "淡淡腮红": "light blush",
        "面纹": "facepaint",
        "浓妆": "makeup ",
        "可爱表情": "cute face",
        "白色睫毛": "white colored eyelashes",
        "长睫毛": "longeyelashes",
        "白色眉毛": "white eyebrows",
        "吊眼角": "tsurime",
        "渐变眼": "gradient_eyes",
        "垂眼角": "tareme",
        "猫眼": "slit pupils ",
        "异色瞳": "heterochromia ",
        "红蓝眼": "heterochromia blue red",
        "水汪汪大眼": "aqua eyes",
        "看你": "looking at viewer",
        "盯着看": "eyeball",
        "凝视": "stare",
        "透过刘海看": "visible through hair",
        "看旁边": "looking to the side ",
        "收缩的瞳孔": "constricted pupils",
        "符号形状的瞳孔": "symbol-shaped pupils ",
        "❤": "heart in eye",
        "爱心瞳孔": "heart-shaped pupils",
        "眨眼": "wink ",
        "眼下痣": "mole under eye",
        "闭眼": "eyes closed",
        "没鼻子": "no_nose",
        "动物耳朵": "animal_ears",
        "动物耳绒毛": "animal ear fluff ",
        "狐狸耳朵": "fox_ears",
        "兔子耳朵": "bunny_ears",
        "猫耳": "cat_ears",
        "狗耳": "dog_ears",
        "叔耳": "mouse_ears",
        "头发上耳朵": "hair ear",
        "尖耳": "pointy ears"
    },
    "基础动作": {
        "坐": "sitting",
        "站": "stand",
        "蹲着": "squat",
        "趴": "grovel",
        "躺": "lie",
        "跳": "jump",
        "跑": "run",
        "走": "walk",
        "飞": "fly",
        "歪头": "head tilt",
        "回头": "looking back",
        "向下看": "looking down",
        "向上看": "looking up",
        "闻": "smelling",
        "睡觉": "sleeping",
        "洗澡": "bathing"
    },
    "手动作": {
        "手放在嘴边": "hand_to_mouth",
        "手放头旁边": "arm at side ",
        "手放脑后": "arms behind head",
        "手放后面": "arms behind back ",
        "手放在自己的胸前": "hand on own chest",
        "手交叉于胸前": "arms_crossed",
        "手放臀": "hand on another's hip",
        "单手插腰": "hand_on_hip",
        "双手叉腰": "hands on hip",
        "举手": "hands up ",
        "伸懒腰": "stretch",
        "举手露腋": "armpits",
        "手把腿抓着": "leg hold",
        "抓住": "grabbing",
        "拿着": "holding",
        "用手指做出笑脸": "fingersmile",
        "拉头发": "hair_pull",
        "撮头发": "hair scrunchie",
        "手势": "w ",
        "耶": "peace symbol ",
        "翘大拇指": "thumbs_up",
        "比出中指": "middle_finger",
        "猫爪手势": "cat_pose",
        "手枪手势": "finger_gun",
        "嘘手势": "shushing",
        "招手": "waving",
        "敬礼": "salute",
        "张手": "spread_arms"
    },
    "腿动作": {
        "张开腿": "spread legs",
        "二郎腿": "crossed_legs",
        "曲腿至胸": "fetal_position",
        "抬一只脚": "leg_lift",
        "抬两只脚": "legs_up",
        "前倾": "leaning forward",
        "婴儿姿势": "fetal position",
        "靠墙": " against wall",
        "趴着": "on_stomach",
        "正坐": "seiza",
        "割坐": "wariza/w-sitting",
        "侧身坐": "yokozuwari",
        "盘腿": "indian_style",
        "抱腿": "leg_hug",
        "跨坐": "straddling",
        "下跪": "kneeling",
        "抽烟": "smoking",
        "用手支撑住": "arm_support"
    },
    "复合动作": {
        "拥抱": "hug",
        "膝枕": "lap_pillow",
        "公主抱": "princess_carry",
        "战斗姿态": "fighting_stance",
        "颠倒的": "upside-down",
        "趴着翘臀": "top-down_bottom-up",
        "翘臀姿势": "bent_over",
        "弓身体": "arched_back",
        "背对背": "back-to-back",
        "手对手": "symmetrical_hand_pose",
        "眼对眼（对视）": "eye_contact",
        "掏耳勺": "mimikaki",
        "牵手": "holding_hands",
        "四肢趴地": "all_fours",
        "女胸部贴在一起": "symmetrical_docking",
        "脱衣服": "undressing",
        "掀起裙子": "skirt lift",
        "掀起上衣": "shirt lift",
        "调整过膝袜": "adjusting_thighhigh"
    },
    "动作": {
        "坐": "sitting",
        "站": "stand",
        "蹲着": "squat",
        "趴": "grovel",
        "躺": "lie",
        "跳": "jump",
        "跑": "run",
        "走": "walk",
        "飞": "fly",
        "歪头": "head tilt",
        "回头": "looking back",
        "向下看": "looking down",
        "向上看": "looking up",
        "闻": "smelling",
        "睡觉": "sleeping",
        "洗澡": "bathing",
        "手放在嘴边": "hand_to_mouth",
        "手放头旁边": "arm at side ",
        "手放脑后": "arms behind head",
        "手放后面": "arms behind back ",
        "手放在自己的胸前": "hand on own chest",
        "手交叉于胸前": "arms_crossed",
        "手放臀": "hand on another's hip",
        "单手插腰": "hand_on_hip",
        "双手叉腰": "hands on hip",
        "举手": "hands up ",
        "伸懒腰": "stretch",
        "举手露腋": "armpits",
        "手把腿抓着": "leg hold",
        "抓住": "grabbing",
        "拿着": "holding",
        "用手指做出笑脸": "fingersmile",
        "拉头发": "hair_pull",
        "撮头发": "hair scrunchie",
        "手势": "w ",
        "耶": "peace symbol ",
        "翘大拇指": "thumbs_up",
        "比出中指": "middle_finger",
        "猫爪手势": "cat_pose",
        "手枪手势": "finger_gun",
        "嘘手势": "shushing",
        "招手": "waving",
        "敬礼": "salute",
        "张手": "spread_arms",
        "张开腿": "spread legs",
        "二郎腿": "crossed_legs",
        "曲腿至胸": "fetal_position",
        "抬一只脚": "leg_lift",
        "抬两只脚": "legs_up",
        "前倾": "leaning forward",
        "婴儿姿势": "fetal position",
        "靠墙": " against wall",
        "趴着": "on_stomach",
        "正坐": "seiza",
        "割坐": "wariza/w-sitting",
        "侧身坐": "yokozuwari",
        "盘腿": "indian_style",
        "抱腿": "leg_hug",
        "跨坐": "straddling",
        "下跪": "kneeling",
        "抽烟": "smoking",
        "用手支撑住": "arm_support",
        "拥抱": "hug",
        "膝枕": "lap_pillow",
        "公主抱": "princess_carry",
        "战斗姿态": "fighting_stance",
        "颠倒的": "upside-down",
        "趴着翘臀": "top-down_bottom-up",
        "翘臀姿势": "bent_over",
        "弓身体": "arched_back",
        "背对背": "back-to-back",
        "手对手": "symmetrical_hand_pose",
        "眼对眼（对视）": "eye_contact",
        "掏耳勺": "mimikaki",
        "牵手": "holding_hands",
        "四肢趴地": "all_fours",
        "女胸部贴在一起": "symmetrical_docking",
    },
    "露出": {
        "肩膀": "Bare shoulders",
        "大腿": "Bare thigh",
        "手臂": "Bare arms",
        "肚脐": "Bare navel"
    },
    "场景": {
        "海边": "seaside",
        "沙滩": "sandbeach",
        "树林": "grove",
        "城堡": "castle",
        "室内": "indoor",
        "床": "bed",
        "椅子": "chair",
        "窗帘": "curtain"
    },
    "物品": {
        "书": "book",
        "酒杯": "wine glass",
        "蝴蝶": "butterfly",
        "猫": "cat"
    },
    "天气": {
        "白天": "day",
        "黄昏": "dusk",
        "夜晚": "night",
        "下雨": "rain",
        "雨中": "in the rain",
        "雨天": "rainy days",
        "日落": "sunset",
        "多云": "cloudy",
        "满月": "full_moon",
        "太阳": "sun",
        "月亮": "moon"
    },
    "环境": {
        "天空": "sky",
        "大海": "sea",
        "星星": "stars",
        "山": "mountain",
        "山上": "on a hill",
        "山顶": "the top of the hill",
        "草地": "in a meadow",
        "高原": "plateau",
        "沙漠": "on a desert",
        "春": "in spring",
        "夏": "in summer",
        "秋": "in autumn",
        "冬": "in winter",
        "夏威夷": "in hawaii",
        "好天": "beautiful detailed sky",
        "好水": "beautiful detailed water",
        "海滩上": "on the beach",
        "在大海上": "on the ocean",
        "海边上": "over the sea",
        "海边日落": "in the ocean",
        "傍晚背对阳光": "against backlight at dusk",
        "黄金时段照明": "golden hour lighting",
        "强边缘光": "strong rim light",
        "强阴影": "intense shadows"
    },
    "正面常用": {
        "高质量": "best quality",
        "高细节": "highly detailed",
        "杰作": "masterpiece",
        "超细节": "ultra-detailed",
        "插图": "illustration"
    },
    "负面常用": {
        "lowres": "lowres",
        "bad anatomy": "bad anatomy",
        "bad hands": "bad hands",
        "text": "text",
        "error": "error",
        "missing fingers": "missing fingers",
        "extra digit": "extra digit",
        "fewer digits": "fewer digits",
        "cropped": "cropped",
        "worst quality": "worst quality",
        "low quality": "low quality",
        "normal quality": "normal quality",
        "jpeg artifacts": "jpeg artifacts",
        "signature": "signature",
        "watermark": "watermark",
        "username": "username",
        "blurry": "blurry",
        "missing arms": "missing arms",
        "long neck": "long neck",
        "Humpbacked": "Humpbacked"
    },
    "自定义": {
        "漂亮眼睛": "beautiful detailed eyes",
        "华丽": "gorgeous"
    }
}
# 以下代码来自
# tags大部分来自幻术魔导书

pose_dict = {'站立': 'standing', '单脚站立': 'standing on one leg', 'S型曲线站立': 'contrapposto', '弯腰': 'bent over', '屈膝礼': 'curtsy', '躺着': 'lying', '躺下': 'lying down', '仰卧': 'on back', 
             '侧卧': 'lying on side', '趴着': 'crawling', '趴着翘臀': 'top-down bottom-up', '坐': 'sitting', '鸭子坐': 'wariza', '坐在地上': 'sitting on the ground', 
             '正坐': 'seiza', '姐坐': 'yokozuwari', '印度盘腿': 'indian style', '莲花坐': 'lotus position', '跨坐': 'straddling', '靠在靠背上斜着坐': 'reclining', '跨坐大腿': 'thigh straddling', 
             '二郎腿': 'figure four sitting', '跪': 'on knees', '单膝跪': 'one knee', '身体倾斜': 'leaning', '靠在一边': 'leaning to the side', '身体前倾': 'leaning forward', '身体后倾': 'leaning back', 
             '靠在物体上': 'leaning on object', '手倒立': 'handstand', '头倒立': 'headstand', '颠倒的': 'upside-down', '凹造型': 'posing', '战斗姿势': 'fighting stance', '拔刀起手式': 'battoujutsu stance', 
             '那个姿势': 'the pose', '僵尸姿势': 'zombie pose', '兔耳姿势': 'bunny pose', '抬高手臂上指': 'kamina pose', '三点着地': 'superhero landing', '焦糖舞': 'caramelldansen', '叉腰向上指': 'saturday night fever', 
             '蝎子姿势': 'scorpion pose', '歪头': 'head tilt', '低头': 'head down', '头后仰': 'head back', '脸贴地面': 'faceplant', '蹲': 'squatting', '四肢着地': 'all fours', '胎儿姿势': 'fetal position', 
             '失意体前屈': 'prostration', '抱腿': 'leg hug', '胸放桌上': 'breasts rest on table', '伸展': 'stretch', '竖一字马': 'standing split', '转身': "turn one's back", '弓身': 'arched back', '卡在墙里': 'through wall', 
             '漂浮': 'floating', '浮在水上': 'afloat', '保持平衡': 'balancing', '背着': 'piggyback', '拍打(翅膀)': 'flapping', '盯着': 'staring', '手臂在头后': 'arms behind head', 
             '手臂在背后': 'arms behind back', '伸直双臂': 'outstretched arms', '伸出单臂': 'outstretched arm', '伸出手': 'outstretched hand', '双手垂放': 'arms at sides', '单抬臂': 'arm up', '双抬臂': 'arms up', 
             '张手': 'spread arms', '用手支撑住': 'arm support', '手交叉于胸前': 'arms crossed', '交叉双臂': 'crossed arms', '手臂后拉': 'arm held back', '遮住关键部位的手臂': 'convenient arm', 
             '手臂摆出心姿势': 'heart arms', '翘大拇指': 'thumbs up', '食指抬起': 'index finger raised', '猫爪': 'cat pose', '指枪': 'finger gun', '虎爪': 'claw pose', '爪子': 'paw pose', '狐狸手势': 'fox shadow puppet', 
             'V手势': 'peace hand', '胜利手势': 'victory pose', 'v在嘴上': 'v over mouth', '九字印': 'kuji-in', '嘘手势': 'shushing', '伸小拇指': 'pinky out', '指尖抵指间': 'steepled fingers', '比中指': 'middle finger', 
             '握拳': 'fist', '攥拳': 'clenched hands', '举起拳头': 'raised fist', '紧张手势': 'fidgeting', '舔手指': 'finger to mouth', '双手相扣': 'own hands clasped', '双手相合': 'own hands together', '张开双手': 'open hands', 
             '张开手': 'open hand', '双手比心': 'heart hands', '手杯': 'cupping hands', '爽手势': 'shocker', '用手指比数字': 'finger counting', '兰花指': 'orchid fingers', '手在头发里': 'hand in hair', '手放嘴上': 'hand to own mouth', 
             '手放脸上': 'hand on own face', '双手放脸': 'hands on own face', '手放帽子上': 'hand on headwear', '手放自己头上': 'hand on own head', '手放耳朵': 'hand on ear', '手放前额': 'hand on own forehead', '手放下颚': 'hand on own chin', 
             '手放脸颊': 'hand on own cheek', '手放脖子': 'hand on own neck', '手放肩上': 'hand on own shoulder', '手放胸部': 'hand on own chest', '手放肚子': 'hand on own stomach', '手放臀部': 'hand on own ass', '双手放臀部': 'hands on ass', 
             '手放膝盖': 'hand on own knee', '双手放膝盖': 'hands on own knees', '手在大腿间': 'hand between legs', '双手放脚': 'hands on feet', '手插兜': 'hand in pocket', '双手插兜': 'hands in pockets', '手在内裤里': 'hand in panties', 
             '单手叉腰': 'hand on hip', '双手叉腰': 'hands on hips', '拨头发': 'hair flip', '拉头发': 'hair pull', '撩头发': 'hair tucking', '札头发': 'tying hair', '梳头': 'hairdressing', '卷头发': 'hair twirling', 
             '扎辫子': 'bunching hair', '捏着帽檐': 'hat tip', '提裙': 'skirt hold', '拉起自己衣服': 'lifted by self', '拉起衣服': 'clothes lift', '拉起连衣裙': 'dress lift', '拉下连衣裙下摆': 'dress tug', '胸罩拉到胸上方': 'bra lift', 
             '拉着吊带': 'holding strap', '整理裤袜': 'adjusting legwear', '抓着领带': 'necktie grab', '拨内裤': 'adjusting panties', '拉起和服': 'kimono lift', '抱着枕头': 'pillow hug', '抱着某物': 'object hug', '揉眼睛': 'rubbing eyes', 
             '遮住耳朵': 'covering ears', '抱自己腿': 'hugging own legs', '捏着肚子': 'belly grab', '搅拌': 'whisking', '投掷': 'pitching', '带着': 'carrying', '拿着长枪': 'polearm', '扶眼镜': 'adjusting eyewear', '伸手触及': 'reaching', 
             '打结': 'tying', '指向': 'pointing', '指向观众': 'pointing at viewer', '指向上': 'pointing up', '指向下': 'pointing down', '指向前': 'pointing forward', '展示腋下': 'presenting armpit', '展示内裤': 'presenting panties', '遮着裆部': 'covering crotch', 
             '托腮': 'chin rest', '托颊': 'head rest', '托胸': 'breast hold', '挥手': 'waving', '敬礼': 'salute', '二指敬礼': 'two-finger salute', '瓦肯举手礼': 'vulcan salute', '拿着': 'holding', '力量拳头': 'power fist', '抱着我手势': 'carry me', '皮影戏': 'shadow puppet'}

hairstyle_dict = {
    '发色': '<color>hair', '渐变色': 'gradient colour', '渐变发': 'gradient hair', 
    '条纹头发(挑染)': 'streaked hair ', '金发': 'blonde hair', '多彩头发': 'multicolored hair', 
    '内侧染色': 'colored inner hair', '彩虹发': 'rainbow hair', '超短发': 'very short hair', '短发': 'short hair', 
    '中等长发': 'medium hair', '长发': 'long hair', '超长发': 'very long hair', '极长发': 'absurdly long hair', '披肩发': 'hair over shoulder', 
    '刘海': 'bangs', '不对称刘海': 'asymmetrical bangs', '齐刘海': 'blunt bangs', '单侧齐刘海': 'side blunt bangs', '遮眼刘海': 'hair over eyes', 
    '遮单眼刘海': 'hair over one eye', '分刘海': 'parted bangs', '长刘海': 'long bangs', '扫刘海': 'swept bangs', '朝一个方向的刘海': 'side swept bangs', 
    '斜刘海': 'diagonal bangs', '眼间发': 'hair between eyes', '交错刘海': 'crossed bangs', '大背头': 'hair slicked back', '半遮眼': 'jitome', 
    '掀起的刘海': 'bangs pinned back', '耳前侧发': 'sidelocks', '耳后发': 'hair behind ear', '公主卷': 'drill hair', '单钻头卷': 'side drill', 
    '双钻头卷': 'twin drills', '四钻头卷': 'quad drills', '进气口(侧发顶部竖起)': 'hair intakes', '单侧进气口': 'single hair intake', 
    '侧发后梳': 'half updo', '垂下的长卷发': 'ringlets', '辫子': 'braid', '长辫': 'long braid', '刘海辫': 'braided bangs', '单侧辫': 'side braid', 
    '双侧辫': 'side braids', '单辫': 'single braid', '双辫': 'twin braids', '低双辫': 'low twin braids', '三股辫': 'tri braids', '四股辫': 'quad braids', 
    '多辫': 'multiple braids', '法式 辫': 'french braid', '冠型织辫': 'crown braid', '前辫': 'front braid', '脏辫': 'dreadlocks', '低辫长发': 'low-braided long hair', 
    '发髻/包子头': 'hair bun', '丸子头': 'topknot', '发髻辫': 'braided bun', '双发髻': 'double bun', '三发髻': 'triple bun', '侧发髻': 'side bun', '锥形发髻': 'cone hair bun', 
    '甜甜圈发髻': 'doughnut hair bun', '飞仙髻': 'hair rings', '单发圈': 'single hair ring', '马尾': 'ponytail', '高马尾': 'hair one side up', '低马尾': 
    'low ponytail', '短马尾': 'short ponytail', '侧马尾': 'side ponytail', '双马尾': 'twintails', '低双马尾': 'low twintails', ' 短双马尾': 'short twintails', '高双马尾': 'hair two side up', 
    '不对称双马尾': 'uneven twintails', '马尾辫': 'braided ponytail', '折叠马尾': 'folded ponytail', '分开的单马尾': 'split ponytail', '波波头': 'bob cut', '公主切': 'hime cut', '蘑菇头': 'bowl cut', 
    '帽盔头': 'undercut', '蓬帕杜发型': 'pompadour', '莫霍克发型': 'mohawk', '爆炸头': 'afro', '超大爆炸头': 'huge afro', '精灵头': 'pixie cut', '蜂窝头': 'beehive hairdo', '平头': 'crew cut', '寸头': 'buzz cut', 
    '鲻鱼头': 'mullet', '波浪发(自然卷)': 'wavy hair', '直发': 'straight hair', '卷发': 'curly hair', '刺发': 'spiked hair', '外卷发': 'flipped hair', '呆毛': 'ahoge', '大呆毛': 'huge ahoge', 
    '多呆毛(天线)': 'antenna hair', '心形呆毛': 'heart ahoge', '蝴蝶结状头发': 'bow-shaped hair', '头发很多': 'big hair', '秃头': 'bald', '秃头女孩': 'bald girl', '凌乱头发': 'messy hair', 
    '散发': 'hair spread out', '漂浮头发': 'floating hair', '湿头发': 'wet hair', '嘴里有头发': 'hair in mouth', '有光泽的头发': 'shiny hair', '摆动的头发': 'hair flaps', '扎起的头发': 'tied hair', 
    '多扎头发': 'multi-tied hair', '一缕一缕的头发': 'hair strand', '非对称发型': 'asymmetrical hair', '富有表现力的头发': 'expressive hair', '瀑布发型': 'curtained hair', '美人尖': "widow's peak", 
    '触手头发': 'tentacle hair', '孤颈毛': 'lone nape hair', '丁髷': 'chonmage'
}

race_list = ['兽耳', '兽耳绒毛', '兽耳', '蝙蝠耳', '猫耳', '狗耳', '狐耳', '兔耳', 
 '兔耳', '浣熊耳', '老鼠耳', '松鼠耳', '熊耳', '虎耳', '狼耳', '马耳', 
 '牛耳', '羊耳', '山羊耳', '狮耳', '熊猫耳', '鹿耳', '猴耳', '猪耳', 
 '鼬耳', '羊驼耳', '尖耳', '长尖耳', '垂耳', '机械耳', '皮卡丘耳', 
 '角', '龙角', '山羊角', '牛 角', '鹿角', '恶魔角', '', '']

data_dict = {
    "date": "true",
    "parts": {
        "facestyle": ['可爱脸', '动漫脸', '大额头', '额头记号', '额前宝石', '眼睛疤痕', '头发后的眉毛', '短眉毛', 
                      '粗眉毛', '男性俊眉', '虎牙', '上牙', '尖牙', '圆齿', '牙齿', '舌头', '唾液', '泪痣', '美人痣', 
                      '浓妆', '胡须', '面纹', '脸上疤痕', '微笑', '大笑', '咧嘴笑', '露齿', '邪笑', '沾沾自喜的', '诱人的微笑', 
                      '顽皮的脸', '眉毛翘起', '愤怒', '愤怒', '恼火', '噘嘴', '小皱眉', '中皱眉', '大皱眉', '眉毛下垂', '哭泣', 
                      '哭', '眼泪', '哭的撕心裂肺', '泪如雨下', '眼含泪水的', '沮丧', '绝望', '惊讶', '惊恐', '尖叫', '小尖叫', 
                      '吓得变色了', '慌张', '紧张出大量的汗', '慌张出汗', '紧张', '脸红', '尴尬', '害羞', '无聊', '困倦', '哈欠', 
                      '精疲力竭的', '喝醉的', '无表情', '困惑', '蔑视', '情绪异常激动的', '狂气', '伸出舌头', '喷嚏', '波形嘴', 
                      '猫嘴', '方嘴', '嘴唇微开', '张嘴', '闭嘴', '半闭眼', '闭单眼', '闭单眼', '闭眼', '闭眼', '空洞注视'],
        "height": ["连衣裙", "半身裙", "迷你裙", "长裙", "短裙", "牛仔裙", "针织裙", "花裙", "雪纺裙", "荷叶边裙",
                 "蕾丝裙", "吊带裙", "背心裙", "打底裙", "百褶裙", "铅笔裙", "礼服裙", "晚礼服", "婚纱", "旗袍",
                 "唐装", "中山装", "短裤", "牛仔短裤", "运动短裤", "高腰短裤", "热裤", "背带短裤", "连体裤", "牛仔连体裤",
                 "运动连体裤", "背带裤", "西装裤", "哈伦裤", "运动裤", "休闲裤", "牛仔裤", "小脚裤", "阔腿裤", "直筒裤",
                 "七分裤", "九分裤", "短袖衬衫", "长袖衬衫", "牛仔衬衫", "卫衣", "T恤", "针织衫", "毛衣", "羽绒服",
                 "棉服", "夹克", "风衣", "大衣", "皮衣", "西装", "马甲", "短外套", "连帽衫", "毛呢大衣", "羊毛衫",
                 "皮草", "羊绒衫", "格子裙", "条纹裙", "波点裙", "花卉印花裙", "宽松连衣裙", "收腰连衣裙", "直筒连衣裙",
                 "A字连衣裙", "雪纺连衣裙", "蕾丝连衣裙", "抹胸裙", "荷叶边连衣裙", "旗袍裙", "百褶连衣裙", "花苞裤", 
                 "爆裂牛仔裤", "修身西装裤", "宽松哈伦裤", "铅笔裤", "针织长裤", "网纱长裙", "棉麻连衣裙", 
                 "印花雪纺裙", "背心吊带裙", "雪纺吊带裙", "收腰雪纺裙", "A字蕾丝裙", "金丝绒裙", "露脐上衣", 
                 "单肩上衣", "蝴蝶结上衣", "假两件上衣", "圆领T恤", "V领T恤", "长款毛衣", "短款毛衣", "连帽卫衣", 
                 "短袖针织衫", "长袖针织衫", "毛呢外套", "印花外套", "运动外套", "真皮外套", "大牌马甲", "衬衫裙", "高领毛衣", 
                 "短款皮衣", "牛仔夹克", "短款连帽卫衣", "高腰阔腿裤", "长款羽绒服", "半高领毛衣", "针织开衫", "阔腿裤套装", "短款风衣", 
                 "复古印花连衣裙", "西装外套", "宽松牛仔裤", "短袖针织衫", "半身长裤套装", "毛呢马甲", "蕾丝吊带上衣", "修身西装", "花边长袖衬衫", 
                 "高腰直筒裤", "长袖雪纺衫", "牛仔裤套装", "红色小西装", "衬衫连衣裙", "鱼尾裙", "收腰长款外套", "宽松卫衣", "牛仔长裤", "长袖碎花连衣裙", 
                 "修身休闲裤", "吊带背心", "半身半裙套装", "高腰直筒牛仔裤", "蕾丝短袖上衣", "百搭针织衫", "宽松连帽毛衣", "不规则半身裙", "牛仔连衣裙", "运动长裤",'比基尼', 
                 '系绳比基尼', '微小比基尼', '比基尼铠甲', '无肩带比基尼', '圣诞比基尼', '前系带比基尼', '侧边系带比基尼', '无罩杯比基尼', '泳衣', '连体泳衣', '学校泳衣',
                   '竞赛泳衣', '学校竞赛泳衣', '连衣裙', '短连衣裙', '露背连衣裙', '绕颈连衣裙', '毛衣连衣裙', '紧身连衣裙', '无袖连衣裙', '无吊带连衣裙', ' 荷叶边连衣裙', 
                   '蝉翼纱连衣裙', '格子连衣裙', '芭蕾连衣裙', '夏日长裙', '阿尔卑斯山少女装', '细致的哥特式束腰连衣裙', '太阳裙', '紧身衣', '无肩带紧身衣', '胶衣', '兔女郎紧身衣', 
                   '内层紧身衣', '水手服', '校服', '西装', '黑西装', '燕尾服', '女性西服', '运动服', '体操服', '排球服', '普通雨衣', '透明雨衣', '雨披', '睡袍', '睡衣', '性感睡衣', 
                   '围裙', '女仆围裙', '浴巾', '沙滩巾', '沙滩浴巾', '私服', '长袍', '连衫裤', '内衣', '女用贴身内衣裤', '猫系内衣', '绷带', '手臂带绷带', '手带绷带', '绑着绷带的脚', 
                   '裸体浴巾', '裸体围裙', '裸体工装', '裸体绑带', '女仆装', '修女服', '修道服', '短祭袍', '兜帽斗篷', '舞娘服', '戏服', '玩偶装', '鬼魂装', '木乃伊装', '吸血鬼装', 
                   '洛丽塔', '哥特洛丽塔', '和风洛丽塔', '汉服', '旗袍', '旗袍', '唐装', '和服', '着物', '浴衣', '羽织', '袴', '袴裙', '和服带', '圣诞装', '万圣节装', '婚纱', '丧服'],
        "hairstyle": list(hairstyle_dict.keys()),
        "daimao": list(pose_dict.keys()),
        "breastsize": ["DCUP", "惊天巨乳", "飞机场", "ECUP",
                        "BCUP", "ACUP", "CCUP", "GCUP", "FCUP"],
        "color": [
            ["黄色", "金色"], "深蓝色", "粉色", ["红色", "赤色"], ["白色", "银色"], "灰色",
            "绿色", "棕色", "橙色", "蓝色", "紫色", "彩虹色", "黑色"
        ],
        "haircolor": ["{color}", "白色",],
        "property": ['光', '正面光', '侧面光', '背光', '逆光', 
                     '黄金时段照明', '最佳照明', '闪光', '闪光', 
                     '镜头光晕', '过曝光', '电影光照', '戏剧光', 
                     '光线追踪', '精细光照', '漏光', '射线光束', 
                     '浮动光斑', '阳光', '太阳光束', '斑驳的阳光', 
                     '阳光透过树木', '月光', '圣光', '从上而下的光线', 
                     '发光', '荧光', '漂亮精细的发光', '反射', '涟漪', 
                     '云隙光', '晨光', '霓虹灯', '霓虹灯', '傍晚背对阳光', 
                     '明暗对比', '影', '阴影', '有影的', '最佳阴影', '强烈阴影', 
                     '强烈阴影', '戏剧阴影', '树影', '投下阴影', '眼部阴影'],
        "job": ['光环', '机械式光环', '耳饰', '耳环', '心形耳饰', 
                '月牙耳饰', '水晶耳饰', '耳机', '耳机(带话筒)', 
                '后脑带的耳机', '猫耳耳机', '眼镜', '太阳镜', '护目镜', 
                '眼镜在头上', '护目镜在头上', '带眼镜的', '无框眼镜', 
                '下半无框眼镜', '心形眼镜', '眼罩', '眼罩', '蒙上的眼', 
                '单眼绷带', '面具', '头上面具', '摘下的面具', '狐狸面具', 
                '天狗面具', '口罩', '医用口罩', '防毒面具', '面纱', '脸绷带', 
                'VR头显', '颈饰', '锚形项圈', '颈带', '围巾', '铃铛', '项圈', '狗项圈', 
                '项链', '珠子项链', '领结', '领带', '格子领带', '锁链', '拉丁十字架', '领巾', 
                '脖子挂耳机', '狗牌', '心锁', '脖子挂口哨', '手套', '肘部手套', '猫猫手套', 
                '无指手套', '猫爪', '乳胶手套', '手镯', '花手镯', '珠子手链', '手镯', '腕带', 
                '腕饰', '护腕', '臂章', '臂环', '臂环', '手铐', '手枷', '宽手铐', '腰带', '搭扣', 
                '武装带', '饰带', '大腿带', '腿部花边环', '腿带', '腿上创可贴', '绑脚', '腿部系带', 
                '脚环', '蝴蝶结', '格子蝴蝶结', '流苏', '丝带', '宝石', '钻石', '缎带', '花饰', 
                '徽章', '创可贴', '蓬莱玉枝', '发饰', '蝙蝠发饰', '青蛙发饰', '蛇发饰', '猫头饰', 
                '兔子头饰', '食物主题发饰', '南瓜发饰', '翅膀发饰', '星星发饰', '心形发饰', '蝴蝶发饰', 
                '树叶发饰', 'X发饰', '羽毛发饰', '月牙发饰', '锚发饰', '骷髅发饰', '音符发饰', '胡萝卜发饰', 
                '骨发饰', '雪花头饰', '三叶草发饰', '鱼形发饰', '发髻套', '扎发绒球', '头饰蝴蝶结', '多个蝴蝶结', 
                '发带', '发带', '发夹', '发卡', '头饰花', '发箍', '洛丽塔发箍', '蝴蝶结发箍', '发束', '发束', 
                '女仆头饰', '头纱', '新娘头纱', '花环', '花环', '头上铃铛', '发珠', '蓝牙耳机头饰', '簪子'],
        "background": ['花瓣', '花瓣', '玫瑰花瓣', '飞舞的花瓣', '落下的花瓣', '水面的花瓣', '水面的花', 
                       '漂浮的樱花', '环绕樱花', '五颜六色的花瓣飞舞', '柳絮', '飘在空中的棉絮', 
                       '树叶', '银杏叶', '枫叶', '落叶', '风中叶', '散落的叶子', '虫子(实际上蝴蝶)', 
                       '蝴蝶', '发光蝴蝶', '飞翔的蝴蝶', '蜜蜂', '蜻蜓', '萤火虫', '羽毛', '天空中的鸟和云', 
                       '金鱼', '太阳', '月亮', '月亮', '满月', '弦月', '新月', '红月', '猩红月亮', '蓝月', 
                       '雨', '雷雨', '雷暴', '暴风雨', '暴雨', '大雨', '中雨', '小雨', '雨中', '雨天', '电', '彩虹',
                         '风', '风吹起', '被风扬起', '微风', '飓风', '尘卷风', '龙卷风', '中等风速', '雪', '雪花', '雪花', 
                         '飘着的雪花', '漂亮精细的雪', '雪崩', '被雪覆盖的', '中雪', '小雪', '霜', '冰', '精细的冰', '冰晶', 
                         '云', '积雨云', '随机分布的云', '多云', '多云', '阴天', '雾气', '蒸汽', '潮湿', '水滴', '液体飞溅', 
                         '飞溅的水', '飞溅水花', '滴水', '地平线', '群山地平线', '天空', '渐变天空', '美丽精细的天空', '燃烧的天空', 
                         '天 际线', '夜空', '星空', '星云', '银河', '银河', '超级银河', '星轨', '五彩斑斓的星轨', '流星', '烟花', 
                         '空中烟火', '极光', '黑烟', '硝烟', '火', '火星子', '精致的火焰', '漂亮的火焰', '火焰漩涡', '飞舞的火焰', 
                         '燃烧', '爆裂魔法', '美丽细致的爆炸', '背后的核爆炸', '战争的火焰', '余烬', '熔化', '魔法', '召 唤魔法阵', 
                         '阴阳', '阴阳球', '鬼火', '彩纸屑', '碎纸屑', '飞溅的彩色碎纸', '折纸', '纸鹤', '彩色的折射', '飘浮的玻璃碎片', 
                         '飘浮的丝带', '漂浮的无色晶体', '发光粒子', '气泡', '大五颜六色的泡泡', '万花筒'],
        "race": race_list,
        "propLoop": {
            "start": 2,
            "p": 0.4,
            "d": "，{i}{property:{i}}，{property:{i}}"
        }
    },
    "result": [
        "二次元少女的{name}",
        "，{facestyle}",
        "，穿着{height}",
        "，{haircolor}头发，{hairstyle}",
        {
            "p": 0.01,
            "d": "，发梢向{haircolor:0}渐变"
        },
        {
            "p": 0.01,
            "d": "，有一缕头发是{haircolor:0}的"
        },
        {
            "p": 0.8,
            "d": "，{daimao}"
        },
        "，{breastsize}",
        {
            "，异色瞳,左眼{color:0}，右眼{color:0}": 0.1,
            "，{color}眼睛": 0.9
        },
        "，画面{property:0}，{background:0}",
        {
            "p": 0.01,
            "d": "，多重人格{propLoop}"
        },
        "，有{race}，{job}，"
    ]
}


class Choicer:
    def _compile(self, d):
        t = type(d)
        if t is list:
            r = []
            for x in d:
                if type(x) is str and x.startswith('{') and x.endswith('}'):
                    for y in self.map[x[1:-1]]:
                        r.append(y[0])
                else:
                    r.append(x)
            p = 1.0 / len(r)
            return [(self._compile(x), p) for x in r]
        elif t is str:
            return d
        elif t is dict:
            if 'start' in d:
                return [(self._compile(d['d']), d['p'], d['start'])]
            elif 'p' in d:
                return [(self._compile(d['d']), d['p'])]
            else:
                return [(self._compile(x), d[x]) for x in d]
        else:
            return []
    reg = re.compile('{(.*?)}')

    def _runstr(self, s: str, vals: dict={}) -> str:
        for k in vals:
            s = s.replace(f'{{{k}}}', vals[k])
        for k in self.vals:
            s = s.replace(f'{{{k}}}', self.vals[k])
        
        def repl(match):
            key = match.group(1)
            k = key.split(':')[0]
            if key not in self.m:
                self.m[key] = set()
            
            while True:
                r = self._run(self.map[k])
                if r not in self.m[key]:
                    self.m[key].add(r)
                    return r
        
        return Choicer.reg.sub(repl, s)

    def _run(self, d) -> str:
        t = type(d)
        if t is str:
            return self._runstr(d)
        elif t is list:
            if len(d) == 1 and len(d[0]) == 3: # loop expr
                sb = []
                d = d[0]
                x = d[0]
                i = d[2]

                while True:
                    sb.append(self._runstr(x, {
                        "i": str(i)
                    }))
                    i += 1
                    if self.rand.random() >= d[1]:
                        break
                return ''.join(sb)
            else:
                r = self.rand.random()
                for d2, p in d:
                    if p > r:
                        return self._run(d2)
                    else:
                        r -= p
                return ''
        else:
            return ''

    def __init__(self, config):
        self.rand = random.Random()
        self.date = config['date']
        self.map = {}

        parts = config['parts']
        for name in parts:
            self.map[name] = self._compile(parts[name])
        
        self.result = [self._compile(x) for x in config['result']]

    def _setseed(self, qq):
        self.rand.seed(qq * (int(time.time()/3600/24) if self.date else 1))
    
    def format_msg(self, qq, name):
        self.vals = {
            "name": name
        }
        self._setseed(qq)
        self.m = {}
        return ''.join([self._run(x) for x in self.result])

replace_dict = {
    "ACUP": "flat_chest",
    "BCUP": "small_breasts",
    "CCUP": "medium breasts",
    "DCUP": "huge breasts",
    "ECUP": "large_breast",
    "FCUP": "large_breast",
    "GCUP": "gigantic breasts",
    "惊天巨乳": "gigantic breasts",
    "飞机场": "flat_cheast"
}


@today_girl.handle()
async def _(bot: Bot, 
            event: MessageEvent, 
            msg: Message=CommandArg()
):  
    user_id = str(event.user_id)
    message = msg.extract_plain_text()
    if message == "我":
        if isinstance(event, PrivateMessageEvent):
         user_name = event.sender.nickname
        else:
            get_info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id)
            user_name = get_info["nickname"]
    else:
        user_name = message
    if config.novelai_daylimit and not await SUPERUSER(bot, event):
        left = await count(str(event.user_id), 1)
        if left == -1:
            await today_girl.finish(f"今天你的次数不够了哦，明天再来找我玩吧")
    img_url = None
    random_int_str = str(random.randint(0, 65535))

    at_id = await get_message_at(event.json())
    if at_id:
        img_url = f"https://q1.qlogo.cn/g?b=qq&nk={at_id}&s=640"
        user_id = str(at_id)
        if config.novelai_paid is False:
            await today_girl.finish(f"以图生图功能已禁用")
    user_name += random_int_str
    user_id_random = user_id + random_int_str
    if config.novelai_todaygirl == 2:
        inst = Choicer(data_dict)
        msg = inst.format_msg(user_id_random, user_name)
        to_user = msg.replace(random_int_str, "")
        # 简单粗暴的替换
        for i in data_dict["parts"]["breastsize"]:
            if i in msg:
                to_ai = msg.replace(i, replace_dict[f"{i}"])
        for i in data_dict["parts"]["hairstyle"]:
            if i in to_ai:
                to_ai = to_ai.replace(i, hairstyle_dict[f"{i}"])
                break
        for i in data_dict["parts"]["daimao"]:
            if i in to_ai:
                to_ai = to_ai.replace(i, pose_dict[f"{i}"])
                break

        try:
            to_ai = to_ai.replace(f"二次元少女的{user_name}", "")
            logger.debug(to_ai)
            tags = await translate(to_ai, "en")
        except:
            await today_girl.finish("翻译API出错辣")
    else:
        user_name = user_name.replace(random_int_str, "")
        choice_list = ["类型", "发色", "头发", "衣服", "鞋子", "装饰", "胸",  "表情", "动作", "天气", "环境", "优秀实践"]
        build_msg_zh = []
        build_msg_en = []
        for i in choice_list:
            zh = random.choice(list(prompt_dict[i].keys()))
            en = prompt_dict[i][zh]
            build_msg_zh.append(zh)
            build_msg_en.append(en)

        to_user = f'''
        二次元的{user_name},
        {build_msg_zh[11]},
        是{build_msg_zh[0]},{build_msg_zh[7]},
        {build_msg_zh[1]}色{build_msg_zh[2]},
        穿着{build_msg_zh[3]}和{build_msg_zh[4]},
        有着{build_msg_zh[5]}和{build_msg_zh[6]},
        正在{build_msg_zh[8]},
        画面{build_msg_zh[9]},{build_msg_zh[10]},
        '''.strip()
        
        tags =  build_msg_en[0] +","+ f','.join(build_msg_en)
    
    try:
        await bot.send(event=event, 
                        message=f"锵锵~~~{to_user}\n正在为你生成二次元图像捏")
    except ActionFailed:
        await bot.send(event=event, 
                        message=f"风控了...不过图图我还是会画给你的...")
    tags = "" if tags is None else tags
    tags = basetag + tags
    ntags = lowQuality
    fifo = AIDRAW(tags=tags, 
                ntags=ntags, 
                event=event)
    if img_url:
        async with aiohttp.ClientSession() as session:
            logger.info(f"检测到图片，自动切换到以图生图，正在获取图片")
            async with session.get(img_url) as resp:
                fifo.add_image(await resp.read(), control_net=True)
    try:
        await fifo.load_balance_init()
        await fifo.post()
    except Exception as e:
        await today_girl.finish(f"服务端出错辣,{e.args}")
    else:
        img_msg = MessageSegment.image(fifo.result[0])
        if config.novelai_extra_pic_audit:
            result = await check_safe_method(fifo, [fifo.result[0]], [""], None, True, "_todaygirl")
            if isinstance(result[1], MessageSegment):
                await bot.send(event=event, message=img_msg+f"\n{fifo.img_hash}", at_sender=True, reply_message=True)
        else:
            try:
                await bot.send(event=event, 
                            message=f"这是你的二次元形象,hso\n"+img_msg+f"\n{fifo.img_hash}"+f"\n生成耗费时间{fifo.spend_time}", 
                            at_sender=True, reply_message=True)
            except ActionFailed:
                await bot.send(event=event, 
                            message=img_msg+f"\n{fifo.img_hash}", 
                            at_sender=True, reply_message=True)
            await save_img(fifo=fifo, img_bytes=fifo.result[0], extra=fifo.group_id+"_todaygirl")
