﻿help_reply_head = """以下仅为功能名称，并非指令！
发送 "njs+对应序号" 查看指令捏~
发送 "njs+对应序号" 查看指令捏~
发送 "njs+对应序号" 查看指令捏~
(重要的事情说三遍！！！)"""
help_reply_body = """[align=right][size=20][color=#008000]*绿色表示正常可用  [/color]
[color=#0000FF]*蓝色表示部分维护  [/color]
[color=#FF0000]*红色表示正在维护  [/color][/size][/align]

[color=#008000]1.头像表情包制作
2.涩图(bushi)
3.轮盘禁言
4.缩写解释
5.肯德基查询[/color]
[color=#FF0000]6.AI绘图(使用第三方API)[/color]
[color=#008000]7.二次元图像分析
8.娶群友
9.抽老婆(与上个插件类似)
10.漂流瓶
11.颜值评分
12.今日运势
13.今日人品(与上个插件类似)
14.无聊趣味占卜[/color]
[color=#0000FF]15.日韩中 VITS 模型拟声[/color]
[color=#008000]16.QQ表情随机回复
17.早晚安
18.塔罗牌
19.小派蒙(原神机器人)
20.国内新冠消息查询
21.每日发癫
22.114514
23.超分辨率重建
24.明日方舟工具箱
25.碧蓝档案Wiki
26.磁力搜索
27.人生重开模拟器
28.答案之书
29.点歌
30.天气
31.在线运行代码
32.emoji 合成器
33.echo
34.Epic 限免游戏资讯
35.一言
36.随机唐可可
37.脑积水帮助
38.复读姬
39.查看服务器状态
40.查看谁艾特我
41.撤回信息
42.智能聊天
43.60s读世界
44.历史上的今天
45.游戏抽卡
46.无数据库的轻量问答
47.以图搜图
48.快速搜索
49.黑名单
50.插件管理
51.文本生成器
52.通用订阅推送
53.横屏/竖屏壁纸|兽耳图|白毛…
54.随机 丁真|坤坤
55.疯狂星期四文案
56.番剧资源搜索
57.战地1、5战绩查询
58.战舰世界水表BOT
59.词云
60.二次元化图像
61.群事件变化通知
62.碧蓝航线wiki
63.今天吃(喝)什么
64.翻译
65.记事本[/color]
[color=#0000FF]66.ChatGPT(OpenAI)对话(使用token)[/color]
[color=#008000]67.命令别名
68.群友召唤术
69.戒色打卡日记
70.Apex查询
71.ChatGPT(OpenAI)对话(使用多api)
72.防撤回
73.原神前瞻直播兑换码
74.签到
75.PING|QRCODE|HTTP|WHOIS
76.文字表情包制作
77.兽语译者[/color]
[color=#0000FF]78.AI绘图(使用本地SDWebUI)[/color]
[color=#008000]79.对对联
80.整点报时
81.星座查询
82.心灵鸡汤
83.原神公告
84.B站分享卡片[/color]
[color=#0000FF]85.反闪照[/color]
[color=#008000]86.leetcode每日一题
87.摩尔质量计算
88.反向词典
89.简易群管
90.对话超管
91.BingGPT(Bing)对话(使用cookies)
92.P站图片查询
93.舔狗日记
94.B站热搜
95.网易云热评
96.课表查询[/color][/color]

[align=center][color=#000000]Powered by (๑•小丫头片子•๑)[/color][/align]"""
help_reply_foot = """更详细内容：《脑积水使用手册》
优先：zhulinyv.github.io/NJS
备用：cnblogs.com/xytpz/p/NJS.html"""

h2_r = """命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
r18: 不填则不会出现r18图片, 填了会根据r18模式管理中的数据判断是否可返回r18图片
关键词: 任意 (可不填)
获取插件帮助信息: "setu_help" | "setu_帮助" | "色图_help" | "色图_帮助"
查询黑白名单: "setu_roste" | "色图名单"

超管指令: 
白名单管理: setu_wl add / del
黑名单管理: setu_ban add / del
r18模式管理: setu_r18 on / off
cd时间更新: setu_cd xxx
撤回时间更新: setu_wd xxx
最大张数更新: setu_mn xxx
更换setu代理服务器: setu_proxy xxx
更新涩图数据库: setu_db"""

h3_r = """无赌注轮盘/自由轮盘: 开启群内随机ban人游戏
拨动滚轮 重新装弹: 重置子弹的位置。
开枪: 顾名思义，开枪。

超管指令：
指令【管理员，群主，超管】：开启自由轮盘 关闭自由轮盘
指令【管理员，群主，超管】：@bot添加名单 代号 @name
指令【管理员，群主，超管】：禁言 代号/@name
指令【管理员，群主，超管】：解封 解封 代号/@name"""

h4_r = """sx lsp；缩写 lsp
lsp可任意替换，支持数字。"""

h5_r = """
在有脑积水的群内发送/kfc开始查询肯德基的物品详情，流程：
1.输入/kfc以开始一个肯德基查询
2.输入[城市名]或[城市名] [地区（县）名]，注意用空格分开
3.输入店铺关键词匹配店铺，可发送空格来获取当前地区部分结果
4.输入店铺前对应序号查询店铺内所有在售食品主题分类
5.输入主题分类对应序号，可查询食品详情信息
6.结束（finish）
在任意一个阶段中发送“退出”来中断一个查询流程。"""

h6_r = """
指令：
◉old + 绘画/画画/画图/作图/绘图/约稿
（说明：使用描述性文本生成图画, 可用参数见文本生成参数, 管理参数见绘图管理参数）
◉old + 以图绘图/以图生图/以图制图
（说明：在基准图像上使用描述性文本生成图画, 支持回复图片消息使用, 可用参数见图像生成参数）
◉old + 个人标签排行/我的标签排行
（说明：查看我的所有使用过的标签的排行）
◉old + 群标签排行/本群标签排行
（说明：查看本期所有使用过的标签的排行）"""

h7_r = "鉴赏/分析 + 图片"

h8_r = """娶群友
娶群友@name
离婚
本群CP
群友卡池
透群友
透群友@name
群友记录"""

h9_r = """抽老婆/选妃
分手
透/透群主/透管理
透@name
"""

h10_r = """注意指令后有\" \"空格
扔漂流瓶 [文本/图片]
寄漂流瓶 [文本/图片] （同扔漂流瓶，防止指令冲突用）
捡漂流瓶
评论漂流瓶 [漂流瓶编号] [文本]
举报漂流瓶 [漂流瓶编号]
查看漂流瓶 [漂流瓶编号]

超管指令：
清空漂流瓶 删除漂流瓶 [漂流瓶编号]"""

h11_r = "颜值评分"

h12_r = """一般抽签：今日运势、抽签、运势；
指定主题抽签：[xx抽签]，例如：pcr抽签、holo抽签、碧蓝抽签；
指定签底并抽签：指定[xxx]签，在./resource/fortune_setting.json内手动配置；
抽签设置：查看当前群抽签主题的配置；
查看（抽签）主题：显示当前已启用主题；
今日运势帮助：显示插件帮助文案；

超管指令：
设置[原神/pcr/东方/vtb/xxx]签：设置群抽签主题；
重置（抽签）主题：设置群抽签主题为随机；
[超管] 刷新抽签：全局即刻刷新抽签，防止过0点未刷新；"""

h13_r = "jrrp或。jrrp或/jrrp或#jrrp"

h15_r = """原神角色需要 APIkey，如需使用本功能，请投喂主人 2.33 软妹币(每月)￥ QwQ...
●让[派蒙|凯亚|安柏|丽莎|琴|香菱|枫原万叶|迪卢克|温迪|可莉|早柚|托马|芭芭拉|优菈|云堇|钟离|魈|凝光|雷电将军|北斗|甘雨|七七|刻晴|神里绫华|雷泽|神里绫人|罗莎莉亚|阿贝多|八重神子|宵宫|荒泷一斗|九条裟罗|夜兰|珊瑚宫心海|五郎|达达利亚|莫娜|班尼特|申鹤|行秋|烟绯|久岐忍|辛焱|砂糖|胡桃|重云|菲谢尔|诺艾尔|迪奥娜|鹿野院平藏]说(中文)
●让[宁宁|爱瑠|芳乃|茉子|丛雨|小春|七海|妃爱|华乃|亚澄|诗樱|天梨|里|广梦|莉莉子]说日语：(日语)
●让[Sua|Mimiru|Arin|Yeonhwa|Yuhwa|Seonbae]说韩语：(韩语)"""

h16_r = "特定表情触发"

h17_r = "早安/晚安"

h18_r = """◯占卜：[占卜]；
◯得到单张塔罗牌回应：[塔罗牌]；

超管指令：
◯开启/关闭群聊转发模式：[开启|启用|关闭|禁用] 群聊转发，可降低风控风险。"""

h20_r = """/疫情菜单
获取菜单 详细内容如下
/查询疫情[地区] ##查询疫情地区
/疫情资讯 ##查询疫情新闻
/境外输入排行榜 ##境外输入排行榜
/疫情现状 ##本国疫情
/查风险[地区] 如 /查风险广州市,广州市,全部
/covid_19开启 ##开启本群
/covid_19关闭 ##关闭本群
/疫情文转图开 ##开启文字转图片
/疫情文转图关 ##关闭文字转图片"""

h21_r = """发癫+名字
或
发癫+@xxx"""

h22_r = "homonumber + 数字"

h23_r = "重建, 超分, real-esrgan, 超分辨率重建, esrgan, real_esrgan"

h24_r = """使用以下指令触发，需加上指令前缀
格式：
指令 => 含义
[] 代表参数
xxx/yyy 代表 xxx 或 yyy

杂项
方舟帮助 / arkhelp   => 查看指令列表
更新方舟素材          => 手动更新游戏数据(json)与图片
更新方舟数据库        => 手动更新数据库

猜干员
猜干员    => 开始新游戏
#[干员名] => 猜干员，如：#艾雅法拉
提示      => 查看答案干员的信息
结束      => 结束当前局游戏

今日干员
今日干员 => 查看今天过生日的干员
塞壬点歌

塞壬点歌 [关键字] => 网易云点歌，以卡片形式发到群内

干员信息
干员 [干员名] => 查看干员的精英化、技能升级、技能专精、模组解锁需要的材料

公开招募
公招 [公招界面截图]          => 查看标签组合及可能出现的干员
回复截图：公招               => 同上
公招 [标签1] [标签2] ...    => 同上

理智提醒
理智提醒                    => 默认记当前理智为0，回满到135时提醒"
理智提醒 [当前理智] [回满理智] => 同上，不过手动指定当前理智与回满理智"
理智查看                    => 查看距离理智回满还有多久，以及当期理智为多少"

公告推送
添加方舟推送群 / ADDGROUP   => 添加自动推送的群号
删除方舟推送群 / DELGROUP   => 删除自动推送的群号
查看方舟推送群 / GETGROUP   => 查看自动推送的群号"""

h25_r = """ba日程表
ba学生图鉴
ba学生wiki
ba羁绊
ba角评
ba总力战
ba活动
ba综合战术考试
ba制造
ba千里眼
ba语音
ba互动家具
ba抽卡
ba切换卡池
ba表情
ba漫画
ba清空缓存（超管指令）"""

h26_r = "磁力搜索 xxx | bt xxx (xxx为关键词)"

h27_r = "艾特脑积水 remake/liferestart/人生重开/人生重来"

h28_r = """翻看答案+问题
问题+翻看答案"""

h29_r = "点歌/qq点歌/网易点歌/酷我点歌/酷狗点歌/咪咕点歌/b站点歌+关键词"

h30_r = "天气+地区；地区+天气"

h31_r = """指令：
code [语言] [-i] [inputText]
[代码]
-i：可选 输入 后跟输入内容

运行示例
运行代码示例(python)(无输入)：
code py
print("Hello World")

运行代码示例(python)(有输入)：
code py -i Hello World
print(input())
"""

h32_r = "[emoji]+[emoji]"

h33_r = "/echo+（任意内容）群聊需要@脑积水"

h34_r = """发送「喜加一」查找限免游戏
发送「喜加一订阅」订阅游戏资讯
发送「喜加一订阅删除」取消订阅游戏资讯
"""

h35_r = "一言"

h36_r = """1.开始游戏：[随机唐可可][空格][简单/普通/困难/地狱/自定义数量]，开始游戏后会限时挑战，可替换为其他角色名；
⚠ 可以[随机唐可可]不指定难度（默认普通）的方式开启游戏，可替换为其他角色名
⚠ 角色名包括组合「LoveLive!-μ's」、「LoveLive!Sunshine!!-Aqours」、「LoveLive!Superstar!!-Liella」成员名称及常见昵称
2.显示帮助：[随机唐可可][空格][帮助]，可替换为其他角色名，效果一样；
3.输入答案：[答案是][行][空格][列]，行列为具体数字，例如：答案是114 514；
4.答案正确则结束此次游戏；若不正确，则直至倒计时结束，Bot公布答案并结束游戏；
5.提前结束游戏：[找不到唐可可]（或其他角色名，需要与开启时输入的角色名相同），仅游戏发起者可提前结束游戏；
6.各群聊互不影响，每个群聊仅能同时开启一局游戏。"""

h37_r = "脑积水帮助, njs帮助, njs菜单, njs列表"

h38_r = "(被动技能), 需要在.env.prod中配置"

h39_r = "状态；向脑积水发送戳一戳表情；双击脑积水头像戳一戳；"

h40_r = """/谁艾特我 查看到底是谁艾特了你
/clear_db 清理当前用户的消息记录
/clear_all 清理全部消息记录"""

h41_r = """@机器人 撤回 # 撤回倒数第一条消息
@机器人 撤回 1 # 撤回倒数第二条消息
@机器人 撤回 0-3 # 撤回倒数三条消息"""

h42_r = """使用 青云客|小爱同学|OpenAI 的聊天api；
响应戳一戳：20%的机率掉落图片，25%的机率回复可莉或纳西妲语音，20%的机率戳回去，35%的机率回复随机内容；
※※※具有屏蔽词拉黑功能。
由于 ChatGPT 是记录上文的，可以 艾特脑积水+api刷新对话 来重置对话。
由于 api 较多，可以通过 "查看api" 来查看当前使用的接口。

超管指令：以下指令均需要艾特
rm_qq + QQ号
切换小爱同学模式1/模式2|青云客|ChatGPTapi模式1/模式2
切换图片api
查看当前api"""

h43_r = "今日早报on+xx:xx(时间)；（计划任务）"

h44_r = "历史上的今天；（计划任务）"

h45_r = """1.原神（当武器和角色无UP池时，所有抽卡命令都指向 '常驻池'）
原神N抽 （常驻池）
原神角色N抽 （角色UP池）
原神武器N抽 （武器UP池）
2.赛马娘
赛马娘N抽 （抽马）
赛马娘卡N抽 （抽卡）
3.坎公骑冠剑
坎公骑冠剑N抽 （抽角色）
坎公骑冠剑武器N抽 （抽武器）
4.碧蓝航线
碧蓝轻型N抽 （轻型池）
碧蓝重型N抽 （重型池）
碧蓝特型N抽 （特型池）
碧蓝活动N抽 （活动池）

其它指令：
'重置原神抽卡'（重置保底） '重载原神卡池' '重载方舟卡池' '重载赛马娘卡池' '重载坎公骑冠剑卡池'
'更新明日方舟信息'
'更新原神信息'
'更新赛马娘信息'
'更新坎公骑冠剑信息'
'更新pcr信息'
'更新碧蓝航线信息'
'更新fgo信息'
'更新阴阳师信息'"""

h46_r = """格式[模糊|全局|正则|@]问...答...
模糊|正则 匹配模式中可任性一个或不选, 不选 表示 全匹配
全局, @ 可与以上匹配模式组合使用
教学中可以使用换行"""

h47_r = """搜图/saucenao搜图/iqdb搜图/ascii2d搜图/ehentai搜图/tracemoe搜图 + 图片
或 回复包含图片的消息，回复搜图"""

h48_r = """查询： ？前缀 关键词
添加（全局）搜索引擎： search.add search.add.global
快速添加： search.add(.global) [预置的搜索引擎名称] [自定义前缀（可选）]
删除（全局）搜索引擎： search.delete search.delete.global
查看搜索引擎列表： search.list search.list.global
备注：
其中所有非全局指令均需要在目标群中进行，所有全局指令均只有Bot管理员能执行"""

h49_r = """添加黑名单用户+qid/@用户
 删除黑名单用户+qid@用户
添加黑名单群+qid
 删除黑名单群+qid
添加黑名单所有群
 删除黑名单所有群
添加黑名单所有好友
 删除黑名单所有好友

查看用户黑名单
查看群聊黑名单

重置黑名单
"""

h50_r = """npm ls查看当前会话插件列表
-s, --store互斥参数，查看插件商店列表（仅超级用户可用）
-u user_id, --user user_id互斥参数，查看指定用户插件列表（仅超级用户可用）
-g group_id, --group group_id互斥参数，查看指定群插件列表（仅超级用户可用）
-a, --all可选参数，查看所有插件（包括不含 Matcher 的插件）
npm info 插件名查询插件信息 （仅超级用户可用）

npm chmod mode plugin ...设置插件权限（仅超级用户可用）
mode必选参数，需要设置的权限，参考上文
plugin...必选参数，需要设置的插件名
-a, --all可选参数，全选插件
-r, --reverse可选参数，反选插件

npm block plugin...禁用当前会话插件（需要权限）
plugin...必选参数，需要禁用的插件名
-a, --all可选参数，全选插件
-r, --reverse可选参数，反选插件
-u user_id ..., --user user_id ...可选参数，管理指定用户设置（仅超级用户可用）
-g group_id ..., --group group_id ...可选参数，管理指定群设置（仅超级用户可用）

npm unblock plugin...启用当前会话插件（需要权限）
plugin...必选参数，需要禁用的插件名
-a, --all可选参数，全选插件
-r, --reverse可选参数，反选插件
-u user_id ..., --user user_id ...可选参数，管理指定用户设置（仅超级用户可用）
-g group_id ..., --group group_id ...可选参数，管理指定群设置（仅超级用户可用）"""

h51_r = """指令 + 文本
支持的指令：
● 抽象话 
● 火星文 
● 蚂蚁文 
● 翻转文字（仅英文）
● 故障文字 
● 古文码 
● 口字码
● 符号码 
● 拼音码 
● 还原符号码 / 解码符号码 
● 还原拼音码 / 解码拼音码
● 问句码 
● 锟拷码 / 锟斤拷 
● rcnb 
● 解码rcnb"""

h52_r = """艾特 脑积水 发送添加订阅开始使用：
微博：
● 图文
● 视频
● 纯文字
● 转发
Bilibili：
● 视频
● 图文
● 专栏
● 转发
● 纯文字
Bilibili 直播：
● 开播提醒
RSS：
● 富文本转换为纯文本
● 提取出所有图片
● 明日方舟：
● 塞壬唱片新闻
● 游戏内公告
● 版本更新等通知
● 泰拉记事社漫画
● 网易云音乐：
● 歌手发布新专辑
● 电台更新
FF14：
● 游戏公告
mcbbs 幻翼块讯：
● Java 版本资讯
● 基岩版本资讯
● 快讯
● 基岩快讯
● 周边消息"""

h53_r = "来份[二次元/壁纸推荐/白毛/兽耳/星空/横屏壁纸/竖屏壁纸/萝莉/必应壁纸]\nPUID + Pixiv画师ID\n关键词搜图 + 关键词"

h54_r = """我测你们码；随机丁真；丁真；一眼丁真
ikun；坤坤；小黑子"""

h55_r = "1、天天疯狂，疯狂星期[一|二|三|四|五|六|日|天]，输入疯狂星期八等不合法时间将提示；2、支持日文触发：狂乱[月|火|水|木|金|土|日]曜日；"

h56_r = """资源+番剧名称 
或 
动漫资源+番剧名称"""

h57_r = """BFI+ID
BFV+ID"""

h59_r = """发送 今日词云、昨日词云、本周词云、本月词云、年度词云 或 历史词云 即可获取词云。
如果想获取自己的词云，可在上述指令前添加 我的，如 我的今日词云。"""

h60_r = "二次元化/动漫化/卡通化 + 图片(支持回复图片)"

h61_r = "被动技能：当有成员进退群、管理员变动、群文件上传时会提示。"

h62_r = """碧蓝航线wiki + 任意内容

任意内容可以为 角色名、武器名、其它 等，
与bilibili游戏wiki一致，wiki上有的都可以替换任意内容"""

h63_r = """今(天|晚)(早上|晚上|中午|夜宵)吃什么
今(天|晚)(早上|晚上|中午|夜宵)喝什么"""

h64_r = """翻译/x译x [内容]
直接翻译是自动识别，x是指定语言
x支持：中（简中）、繁（繁中）、英、日、韩、法、俄、德"""

h66_r = """chat+任意聊天内容
（这个对话是记录上文的）
艾特脑积水+刷新对话 -> 来刷新本轮对话
艾特脑积水+导出对话 -> 来导出本轮对话id
艾特脑积水+导入对话+对话id+父消息id(可选) -> 来导入对话
艾特脑积水+保存会话/保存对话+会话名称 -> 来将当前对话保存
艾特脑积水+查看会话/查看对话 -> 来查看已保存的对话
艾特脑积水+切换会话/切换对话+会话名称 -> 来切换到制定对话"""

h67_r = """alias [别名]=[指令名称] 添加别名
alias [别名] 查看别名
alias -p 查看所有别名
unalias [别名] 删除别名
unalias -a 删除所有别名
默认只在当前群聊/私聊中生效，使用 -g 参数添加全局别名；增删全局别名需要超级用户权限
alias -g [别名]=[指令名称] 添加全局别名
unalias -g [别名] 删除全局别名"""

h68_r = """设置召唤术+昵称+QQ号
召唤+昵称
    戳+昵称+数字

删除召唤术+昵称
召唤列表

超管指令：切换召唤术普通/增强/强力"""

h69_r = """【戒色目标 + 数字】【设置戒色目标 + 数字】，设置戒色目标天数。
【戒色】【戒色打卡】，每日打卡，请勿中断喵。
【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况。
【放弃戒色】【取消戒色】【不戒色了】，删除戒色目标。
【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况
财能使人贪，色能使人嗜，名能使人矜，潜能使人倚，四患既都去，岂在浮尘里。
"""

h70_r = """查询玩家信息: 
bridge [玩家名称] 、 玩家 [玩家名称]、 uid [玩家UID]、 UID [玩家UID]

查询大逃杀地图轮换:
maprotation 、 地图

查询猎杀者信息:
predator 、 猎杀

查询复制器轮换:
crafting 、 制造"""

h71_r = """以下指令均需要艾特
基本的聊天对话 -> 基本会话（默认【chat2】触发）
连续对话 -> chat/聊天/开始聊天
结束聊天 -> stop/结束/结束聊天
切换会话 -> 切换群聊/切换会话/切换
重置会话记录 -> 刷新/重置对话
重置AI人格 -> 重置人格
设置AI人格 -> 设置人格
导出历史会话 -> 导出会话/导出对话
回答渲染为图片 -> 图片渲染（默认关闭）"""

h72_r = """开启/添加防撤回, enable + 群号1 群号2 ...
关闭/删除防撤回, disable + 群号1 群号2 ...
查看防撤回群聊
开启/关闭绕过管理层
防撤回菜单
开启/关闭防撤回私聊gid uid
查看防撤回私聊"""

h73_r = "gscode / 兑换码"

h74_r = """签到
我的好感"""

h75_r = """ping  + 网址
qrcode + 网址
whois + 网址
httpcat + HTTP状态码"""

h77_r = """[兽音加密]/[convert]
[兽音解密]/[deconvert]
[切噜一下]/[cherulize]
[切噜～]/[decherulize]
"""

h78_r = """.aidraw loli,cute --ntags big breast --seed 114514

指令使用shell解析输入的参数
square为指定画幅，支持简写为s，其他画幅为portrait和landscape，同样支持简写，默认为portrait
seed若省略则为自动生成
词条使用英文，使用逗号（中英都行，代码里有转换）分割，中文会自动机翻为英文，不支持其他语种
如果你不想用.aidraw，可以用 绘画 、 咏唱 或 召唤 代替。
在消息中添加图片或者回复带有图片的消息自动切换为以图生图模式

.aidraw on/off
启动/关闭本群的aidraw

.anlas check
查看自己拥有的点数

.anlas
查看帮助

.anlas [数字] @[某人]
将自己的点数分给别人(superuser点数无限)

.tagget [图片]
获取图片的TAG
如果你不想用.tagget，可以用 鉴赏 或 查书 代替。

详细指令：https://nb.novelai.dev/main/aidraw.html#%E6%8C%87%E4%BB%A4%E5%BC%80%E5%A4%B4"""

h79_r = """对联 <上联内容> (数量)
· 数量可选，默认为1"""

h80_r = """北京时间

管理层指令：
开启、关闭整点报时
查看整点报时列表"""

h81_r = "#星座 + 想要查询的星座"

h82_r = "鸡汤/毒鸡汤"

h83_r = """原神公告
查看公告 + 公告序号"""

h84_r = "被动技能，为B站链接或ID生成海报"

h85_r = """(被动技能)
超管指令：开启/启用/禁用反闪照"""

h86_r = """对指令/每日一题，/lc，/leetcode回复，发送今天的每日一题。
可搜索leetcode题目，指令/lc搜索 XXXXX，/lc查找 XXXXX，/leetcode搜索 XXXXX，将以关键词“XXXXX”进行leetcode搜索，发送搜索到的第一道题。
随机一题，指令/lc随机，/lc随机一题，/leetcode随机将请求leetcode随机一题，发送请求到的任意题目。
查询用户信息/lc查询 XXXXX，/lc查询用户 XXXXX，/leetcode查询 XXXXX，可查询用户基本信息，XXXXX为用户ID（不能用用户名）。
加入计划任务 每日在指定时间向指定群和好友发送当天的每日一题"""

h87_r = "发送 /摩尔质量 化学式 或 /相对分子质量 化学式 或 /mol 化学式"

h88_r = """找词/反向词典/wantwords <模式> <描述>
模式可选：
zhzh：中—>中
zhen：中—>英
enzh：英—>中
enen：英—>英
<描述>即对希望找到的词的描述
"""

h89_r = """需要超级用户或群主或管理员权限
设置管理员 + @somebody
取消管理员 + @somebody
禁言/口球 + @somebody + 阿拉伯数字
解禁 + @somebody
移出 + @somebody
移出并拉黑 + @somebody"""

h90_r = "反馈开发者 + 内容"

h91_r = """chat3    与Bing进行对话
chat-new    新建一个对话
chat-history    返回历史对话"""

h92_r = """pixiv pid
pixivRank 1/7/30"""

h93_r = "舔狗日记\n讲个笑话\n文案\n\n超管指令:\n开启文案/关闭文案"

h94_r = "b站热搜"

h95_r = "网抑云|网易云热评"

h96_r = "完整课表\n本周课表\n下周课表\n上课\n设置周数\n查看课表\n明日早八"