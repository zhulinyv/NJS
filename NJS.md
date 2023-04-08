# o(〃＾▽＾〃)o 目前使用的插件：……
天下没有不散的宴席，感谢大家陪[**脑积水**](https://github.com/zhulinyv/NJS)走过的 300 多个日日夜夜，大家都是用爱发电，且用且珍惜……
[**脑积水**](https://github.com/zhulinyv/NJS)基于 NoneBot 开源项目，如有需要，可以自行查找相关资料了解。
**插件名称旁边即为插件仓库地址，可以自行查看配置项。**

——2023年1月20日17时43分38秒

## 1.头像表情包制作 [nonebot_plugin_petpet](https://github.com/noneplugin/nonebot-plugin-petpet)
<details>
<summary><b>指令：</b></summary>
<a href="https://smms.app/image/ygMJk1Kl4Iz37BZ" target="_blank"><img src="https://s2.loli.net/2022/12/11/ygMJk1Kl4Iz37BZ.png" ></a>
<p>头像表情包</p>
<p><b>其它指令：</b></p>
<p dir="auto">随机表情 + @user/qq号/自己/图片</p>
<p><b>以下为超管指令：</b></p>
<p dir="auto">发送 <code>启用表情/禁用表情 [表情名]</code>，如：<code>禁用表情 摸</code>、<code>启用表情 petpet 贴 爬</code></p>
<p dir="auto">发送 <code>全局启用表情 [表情名]</code> 可将表情设为黑名单模式；</p>
<p dir="auto">发送 <code>全局禁用表情 [表情名]</code> 可将表情设为白名单模式；</p>
</details>

## 2.**~~涩图~~** 二次元图片 [nonebot_plugin_setu4](https://github.com/Special-Week/nonebot_plugin_setu4)
<details>
<summary><b>指令：</b></summary>
<p><b>获取涩图：</b></p>
<pre><code>
命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
r18: 不填则不会出现r18图片, 填了会根据r18模式管理中的数据判断是否可返回r18图片
关键词: 任意 (可不填)
参考 (空格可去掉):   
    setu 10张 r18 白丝
    setu 10张 白丝    
    setu r18 白丝
    setu 白丝
    setu
</code></pre>
<p><b>其它指令：</b></p>
<pre><code>
获取插件帮助信息:
"setu_help" | "setu_帮助" | "色图_help" | "色图_帮助"
查询黑白名单:
"setu_roste" | "色图名单"
</pre></code>
<p><b>超管指令：</p></b>
<pre><code>
白名单管理：
setu_wl add  添加会话至白名单
setu_wl del  移出会话自白名单
黑名单管理：
setu_ban add  添加会话至黑名单
setu_ban del  移出会话自黑名单
r18模式管理：
setu_r18 on  开启会话的r18模式
setu_r18 off 关闭会话的r18模式
cd时间更新:
setu_cd xxx  更新会话的冷却时间, xxx 为 int 类型的参数
撤回时间更新:
setu_wd xxx  撤回前等待的时间, xxx 为 int 类型的参数
最大张数更新:
setu_mn xxx  单次发送的最大图片数, xxx 为 int 类型的参数
</pre></code>
</details>

## 3.轮盘禁言 [nonebot_plugin_russian_ban](https://github.com/KarisAya/nonebot_plugin_russian_ban)
<details>
<summary><b>指令：</summary></b>
<p dir="auto"><strong>指令</strong>：<code>无赌注轮盘</code> <code>自由轮盘</code></p>
<p dir="auto">开启群内随机ban人游戏</p>
<p dir="auto"><strong>指令</strong>：<code>拨动滚轮</code> <code>重新装弹</code></p>
<p dir="auto">重置子弹的位置。</p>
<p dir="auto"><strong>指令</strong>：<code>开枪</code></p>
<p dir="auto">顾名思义，开枪。</p>
<p><b>超管指令:</b></p>
<p dir="auto"><strong>指令【管理员，群主，超管】</strong>：<code>开启自由轮盘</code> <code>关闭自由轮盘</code></p>
<p dir="auto">控制当前群内可否发起自由轮盘游戏，【管理员，群主，超管】可无视此设定在群内发起轮盘。</p>
<p dir="auto"><strong>指令【管理员，群主，超管】</strong>：<code>@bot添加名单 代号 @name</code></p>
<p dir="auto">在本群添加重点关照人群，以便通过代号快捷禁言，可以一次设置多人。</p>
<p dir="auto"><strong>指令【管理员，群主，超管】</strong>：<code>禁言 代号/@name</code></p>
<p dir="auto">给@的成员禁言1小时。可@多人。如果给群友设置过代号，可以通过代号快捷禁言</p>
<p dir="auto"><strong>指令【管理员，群主，超管】</strong>：<code>解封</code> <code>解封 代号/@name</code></p>
<p dir="auto">给@的成员解除禁言。可@多人。如果给群友设置过代号，可以通过代号快捷解除禁言。</p>
<p dir="auto">如果没有指定成员会返回当前被封成员列表。之后可以根据提示进一步设置。</p>
</details>

## 4.缩写解释 [nonebot_plugin_abbrreply](https://github.com/anlen123/nonebot_plugin_abbrreply)
<details>
<summary><b>指令：</summary></b>
<p>指令：sx lsp；缩写 lsp</p>
<p>备注：lsp可任意替换，支持数字。</p>
</details>

## 5.肯德基查询 [nonebot_plugin_kfcrazy](https://github.com/Kaguya233qwq/nonebot_plugin_kfcrazy)
<details>
<summary><b>指令：</summary></b>
<p dir="auto">在有bot的群内发送<code>/kfc</code>开始查询肯德基的物品详情，流程：</p>
<p dir="auto">1.输入<code>/kfc</code>以开始一个肯德基查询</p>
<p dir="auto">2.输入[城市名]或[城市名] [地区（县）名]，注意用空格分开</p>
<p dir="auto">3.输入店铺关键词匹配店铺，可发送空格来获取当前地区部分结果</p>
<p dir="auto">4.输入店铺前对应序号查询店铺内所有在售食品主题分类</p>
<p dir="auto">5.输入主题分类对应序号，可查询食品详情信息</p>
<p dir="auto">6.结束（finish）</p>
<p dir="auto">在任意一个阶段中发送“退出”来中断一个查询流程。</p>
</details>

## 6.AI绘图(使用第三方API) [nonebot-plugin-aidraw](https://github.com/A-kirami/nonebot-plugin-aidraw#%E5%9B%BE%E5%83%8F%E7%94%9F%E6%88%90%E5%8F%82%E6%95%B0)
<details>
<summary><b>指令：</summary></b>
<pre><p>
◉old+ 绘画/画画/画图/作图/绘图/约稿
（说明：使用描述性文本生成图画, 可用参数见文本生成参数, 管理参数见绘图管理参数）
◉old+ 以图绘图/以图生图/以图制图
（说明：在基准图像上使用描述性文本生成图画, 支持回复图片消息使用, 可用参数见图像生成参数）
◉old+ 个人标签排行/我的标签排行
（说明：查看我的所有使用过的标签的排行）
◉old+ 群标签排行/本群标签排行
（说明：查看本期所有使用过的标签的排行）
</pre></p>
<p><b>其它参数：</b></p>
<p>
<a href="https://smms.app/image/7PEhrxczmqYbU3l" target="_blank"><img src="https://s2.loli.net/2022/10/23/7PEhrxczmqYbU3l.png" ></a>
</p>
</details>

## 7. 二次元图像分析 [nonebot-plugin-savor](https://github.com/A-kirami/nonebot-plugin-savor)
<details>
<summary><b>指令：</summary></b>
<p>鉴赏/分析 + 图片(支持回复图片)</p>
</details>

## 8.娶群友 [nonebot_plugin_groupmate_waifu](https://github.com/KarisAya/nonebot_plugin_groupmate_waifu)
<details>
<summary><b>指令：</summary></b>
<pre><p>
**娶群友**
纯爱 双向奔赴版，每天刷新一次，两个人会互相抽到对方。
**娶群友@name**
有机会娶到at的人。。。
**离婚**
雪花飘飘北风萧萧，天地一片苍茫~
**本群cp**
查看当前群内的cp
**群友卡池**
查看当前群可以娶到的群友列表
**透群友**
ntr 宫吧老哥狂喜版，每次抽到的结果都不一样。
**群友记录**
查看当前群的群友今日被透的次数，被透次数是跨群的，也就是说群友在别的群挨透也会在记录里显示出来。
</p></pre>
</details>

## 9.抽老婆（与上个插件类似） yinpa
<details>
<summary><b>指令：</summary></b>
<pre><p>
抽老婆
分手
透
透@name
透群主/透管理
</p></pre>
</details>

## 10.漂流瓶 [nonebot_plugin_bottle](https://github.com/Todysheep/nonebot_plugin_bottle)
<details>
<summary><b>指令：</summary></b>
<pre><p>
扔漂流瓶 [文本/图片]
寄漂流瓶 [文本/图片] （同扔漂流瓶，防止指令冲突用）
捡漂流瓶
评论漂流瓶 [漂流瓶编号] [文本]
举报漂流瓶 [漂流瓶编号]
查看漂流瓶 [漂流瓶编号]
超管指令&功能须知:
</b>SUPERUSER指令：</b>
清空漂流瓶
删除漂流瓶 [漂流瓶编号]
功能须知：
扔漂流瓶指令无字数限制，如需要可在代码中修改
捡漂流瓶若捡到的漂流瓶存在回复，则会显示最近三条(默认)，使用查看漂流瓶查看所有回复
查看漂流瓶为保证随机性，无评论时不展示漂流瓶内容，可在代码中修改
举报漂流瓶五次(默认)后将自动删除
清空漂流瓶无确认过程，使用需谨慎
漂流瓶数据库存放在data/bottle/data.json中
黑名单群组可在__init__.py同级路径config.py中添加
</p></pre>
</details>

## 11.颜值评分 beauty_rate
<details>
<summary><b>指令：</summary></b>
<pre><p>颜值评分</p></pre>
</details>

## 12.今日运势 [nonebot_plugin_fortune](https://github.com/MinatoAquaCrews/nonebot_plugin_fortune)
<details>
<summary><b>指令：</b></summary>
<pre><p>
一般抽签：今日运势、抽签、运势；
指定主题抽签：[xx抽签]，例如：pcr抽签、holo抽签、碧蓝抽签；
指定签底并抽签：指定[xxx]签，在./resource/fortune_setting.json内手动配置；
抽签设置：查看当前群抽签主题的配置；
查看（抽签）主题：显示当前已启用主题；
今日运势帮助：显示插件帮助文案；
</p></pre>
<p><b>超管指令: </b></p>
<p>设置[原神/pcr/东方/vtb/xxx]签：设置群抽签主题；</p>
<p>重置（抽签）主题：设置群抽签主题为随机；</p>
<p>[超管] 刷新抽签：全局即刻刷新抽签，防止过0点未刷新；</p>
</details>

## 13.今日人品（与上个插件类似） jrrp
<details>
<summary><b>指令：</summary></b>
<p>。jrrp或/jrrp或#jrrp或jrrp</p>
</details>

## 14.~~无聊~~趣味占卜 [nonebot_plugin_shindan](https://github.com/noneplugin/nonebot-plugin-shindan)
<details>
<summary><b>指令：</summary></b>
<pre><p>
默认占卜列表及对应的网站id如下：
<a href="https://smms.app/image/E9PWsVD3j4Zwclb" target="_blank"><img src="https://s2.loli.net/2022/12/30/E9PWsVD3j4Zwclb.jpg" ></a>
发送 “占卜指令 名字” 即可，如：人设生成 小Q
发送 “/占卜列表” 可以查看上述列表；
超级用户可以发送 “/添加占卜 id 指令”、“/删除占卜 id” 增删占卜列表，可以发送 “/设置占卜 id image/text”设置输出形式
</p></pre>
</details>

## 15.日韩中 VITS 模型拟声 [nonebot_plugin_moegoe](https://github.com/Yiyuiii/nonebot-plugin-moegoe)
<details>
<summary><b>指令：</summary></b>
<pre><p>
●让[派蒙|凯亚|安柏|丽莎|琴|香菱|枫原万叶|迪卢克|温迪|可莉|早柚|托马|芭芭拉|优菈|云堇|钟离|魈|凝光|雷电将军|北斗|甘雨|七七|刻晴|神里绫华|雷泽|神里绫人|罗莎莉亚|阿贝多|八重神子|宵宫|荒泷一斗|九条裟罗|夜兰|珊瑚宫心海|五郎|达达利亚|莫娜|班尼特|申鹤|行秋|烟绯|久岐忍|辛焱|砂糖|胡桃|重云|菲谢尔|诺艾尔|迪奥娜|鹿野院平藏]说(中文)
●让[宁宁|爱瑠|芳乃|茉子|丛雨|小春|七海|妃爱|华乃|亚澄|诗樱|天梨|里|广梦|莉莉子]说日语：(日语)
●让[Sua|Mimiru|Arin|Yeonhwa|Yuhwa|Seonbae]说韩语：(韩语)
</p></pre>
</details>

## 16.QQ表情随机回复 Candy_reply
<details>
<summary>指令：</summary>
<a target="_blank" rel="noopener noreferrer nofollow" href="https://user-images.githubusercontent.com/66541860/189467041-991465fc-f51c-4883-98a4-dd3c0517ca04.png"><img src="https://user-images.githubusercontent.com/66541860/189467041-991465fc-f51c-4883-98a4-dd3c0517ca04.png" alt="help" data-canonical-src="https://static.cherishmoon.fun/LittlePaimon/readme/new/help.jpg" style="max-width: 100%;"></a>
</details>

## 17.早晚安 morning_and_night
<details>
<summary><b>指令：</summary></b>
<p>早安；晚安；来份兽耳图；横屏壁纸；竖屏壁纸</p>
</details>

## 18.塔罗牌 [nonebot_plugin_tarot](https://github.com/MinatoAquaCrews/nonebot_plugin_tarot)
<details>
<summary><b>指令：</summary></b>
<pre><p>
◯占卜：[占卜]；
◯得到单张塔罗牌回应：[塔罗牌]；
◯[超管] 开启/关闭群聊转发模式：[开启|启用|关闭|禁用] 群聊转发，可降低风控风险。
</p></pre>
</details>

## 19.小派蒙（原神机器人） [LittlePaimon](https://github.com/CMHopeSunshine/LittlePaimon)
<details>
<summary><b>指令：</summary></b>
<pre><p>
阿巴阿巴......
太多了自己康（图片加载较慢，请耐心等待或先浏览下文），也可以发送 “<b>pmhelp</b>” 获取帮助。
</p></pre>
<p><b>帮助列表</b></p>
<a href="https://smms.app/image/HAw1zPkxUn7FE9V" target="_blank"><img src="https://s2.loli.net/2022/12/11/HAw1zPkxUn7FE9V.png" ></a>
</details>

## 20.疫情小助手 [nonebot-plugin-covid-19-by](https://github.com/bingqiu456/nonebot-plugin-covid-19-by)
<details>
<summary><b>指令：</summary></b>
<pre><p>
/疫情菜单
获取菜单 详细内容如下：
/查询疫情[地区] ##查询疫情地区
/疫情资讯 ##查询疫情新闻
/境外输入排行榜 ##境外输入排行榜
/疫情现状 ##本国疫情
/查风险[地区] 如 /查风险广州市,广州市,全部
/covid_19开启 ##开启本群
/covid_19关闭 ##关闭本群
/疫情文转图开 ##开启文字转图片
/疫情文转图关 ##关闭文字转图片
</p></pre>
</details>

## 21.每日发癫 Daily_epilepsy
<details>
<summary><b>指令：</summary></b>
<pre><p>发癫+名字</p></pre>
</details>

## 22. 114514 homoNumber
<details>
<summary><b>指令：</summary></b>
<pre><p>homonumber + 数字</p></pre>
</details>

## 23.超分辨率重建 [nonebot_plugin_RealESRGAN](https://github.com/ppxxxg22/nonebot_plugin_RealESRGAN)
<details>
<summary><b>指令：</summary></b>
<pre><p>重建, 超分, real-esrgan, 超分辨率重建, esrgan, real_esrgan</p></pre>
</details>

## 24.明日方舟工具箱 [nonebot_plugin_arktools](https://github.com/NumberSir/nonebot_plugin_arktools)
<details>
<summary><b>指令：</summary></b>
<pre><p>
**直接反馈部分：**
方舟今日资源       ->    查看今天开放的资源关卡
更新方舟今日资源    ->    手动更新今天开放的资源关卡
方舟最新活动    ->    查看最新的活动相关信息
更新方舟游戏数据   ->   更新至最新的游戏素材，以便公招识别与干员查询使用
更新方舟游戏数据 -f   ->   若提示是最新数据，但仍有缺失，可以在命令后附带 -f 提示符强制更新
**公招部分：**
公招[图片]    ->    查询推荐的公招标签
回复公招图片：公招 -> 同上
公招 [标签1 标签2 ...] -> 手动输入公招标签
**干员信息：**
干员 [干员名称] ->   查询干员的技能升级材料、专精材料、精英化材料、模组材料
**塞壬音乐：**
塞壬点歌 [歌名]  ->   以网易云音乐小卡片的形式发送歌曲（其实不是塞壬唱片的歌也可以）
塞壬歌单     ->   查看当前塞壬音乐的所有专辑
</p></pre>
</details>

## 25.碧蓝档案 Wiki  [NoneBot-Plugin-BAWiki](https://github.com/lgc2333/nonebot-plugin-bawiki)
<details>
<summary><b>指令：</summary></b>
<pre><p>
ba日程表 --> 日程表
ba学生图鉴 --> 学生图鉴
ba学生wiki  --> 学生wiki
ba羁绊 --> 羁绊查询
ba角评 --> 角色评价
ba总战力 --> 总战力一图流
ba活动 --> 查询活动攻略图
ba综合战术考试 --> 查询综合战术考试攻略图
ba制造 --> 查询制造功能机制图
ba千里眼 --> 查询国际服未来的卡池与活动
ba语音 --> 发送学生语音
ba互动家具 --> 查询互动家具总览图
ba抽卡 --> 模拟抽卡
ba切换卡池 --> 设置模拟抽卡的UP池
ba表情 --> 随机发送一个国际服社团聊天表情
ba漫画 --> 随机发送一话官推漫画
ba清空缓存 --> 清空缓存（超管指令）
</p></pre>
</details>

## 26.磁力搜索 [nonebot_plugin_BitTorrent](https://github.com/Special-Week/nonebot_plugin_BitTorrent)
<details>
<summary><b>指令：</summary></b>
<pre><p>磁力搜索 xxx | bt xxx   (xxx为关键词)</p></pre>
</details>

## 27.人生重开模拟器 [nonebot-plugin-remake](https://github.com/noneplugin/nonebot-plugin-remake)
<details>
<summary><b>指令：</summary></b>
<pre><p>@脑积水 remake/liferestart/人生重开/人生重来</p></pre>
</details>

## 28.答案之书 [nonebot_plugin_answersbook](https://github.com/A-kirami/nonebot-plugin-answersbook)
<details>
<summary><b>指令：</summary></b>
<pre><p>
翻看答案+问题
问题+翻看答案
</p></pre>
</details>

## 29.点歌 [nonebot_plugin_simplemusic](https://github.com/noneplugin/nonebot-plugin-simplemusic)
<details>
<summary><b>指令：</summary></b>
<pre><p>点歌/qq点歌/网易点歌/酷我点歌/酷狗点歌/咪咕点歌/b站点歌+关键词</p></pre>
</details>

## 30.天气 [nonebot-plugin-heweather](https://github.com/kexue-z/nonebot-plugin-heweather)
<details>
<summary><b>指令：</summary></b>
<pre><p>天气+地区；地区+天气</p></pre>
</details>

## 31.在线运行代码 [nonebot_plugin_code](https://github.com/yzyyz1387/nonebot_plugin_code)
<details>
<summary><b>指令：</summary></b>
<pre><p>
code [语言] [-i] [inputText]
[代码]
-i：可选 输入 后跟输入内容
</p></pre>
<summary>运行示例</summary>
<p>运行代码示例(python)(无输入)：</p>
<p>code py</p>
<p>    print("Hello World")</p>
<p>运行代码示例(python)(有输入)：</p>
<p>code py -i Hello World</p>
<p>    print(input())</p>
</details>

## 32.emoji 合成器 [nonebot_plugin_emojimix](https://github.com/noneplugin/nonebot-plugin-emojimix)
<details>
<summary><b>指令：</summary></b>
<pre><p>[emoji]+[emoji]</p></pre>
</details>

## 33.echo
<details>
<summary><b>指令：</summary></b>
<pre><p>echo+（任意内容）（群聊需要艾特）</p></pre>
</details>


## 34.Epic 限免游戏资讯 [nonebot_plugin_epicfree](https://github.com/monsterxcn/nonebot_plugin_epicfree)
<details>
<summary><b>指令：</summary></b>
<pre><p>
发送「喜加一」查找限免游戏
发送「喜加一订阅」订阅游戏资讯
发送「喜加一订阅删除」取消订阅游戏资讯
</p></pre>
</details>

## 35.一言 [nonebot_plugin_hitokoto](https://github.com/A-kirami/nonebot-plugin-hitokoto)
<details>
<summary><b>指令：</summary></b>
<pre><p>一言</p></pre>
</details>

## 36.随机唐可可 [nonebot_plugin_randomtkk](https://github.com/MinatoAquaCrews/nonebot_plugin_randomtkk)
<details>
<summary><b>指令：</summary></b>
<pre><p>
1.开始游戏：[随机唐可可][空格][简单/普通/困难/地狱/自定义数量]，开始游戏后会限时挑战，可替换为其他角色名；
⚠ 可以[随机唐可可]不指定难度（默认普通）的方式开启游戏，可替换为其他角色名
⚠ 角色名包括组合「LoveLive!-μ's」、「LoveLive!Sunshine!!-Aqours」、「LoveLive!Superstar!!-Liella」成员名称及常见昵称
2.显示帮助：[随机唐可可][空格][帮助]，可替换为其他角色名，效果一样；
3.输入答案：[答案是][行][空格][列]，行列为具体数字，例如：答案是114 514；
4.答案正确则结束此次游戏；若不正确，则直至倒计时结束，Bot公布答案并结束游戏；
5.提前结束游戏：[找不到唐可可]（或其他角色名，需要与开启时输入的角色名相同），仅游戏发起者可提前结束游戏；
6.各群聊互不影响，每个群聊仅能同时开启一局游戏。
</p></pre>
</details>

## 37.脑积水帮助 njs_help
<details>
<summary><b>指令：</summary></b>
<pre><p>njs帮助, njs菜单, njs列表</p></pre>
</details>

## 38.复读姬 [nonebot_plugin_repeater](https://github.com/ninthseason/nonebot-plugin-repeater)
<details>
<summary><b>指令：</summary></b>
<pre><p>被动技能</p></pre>
</details>

## 39.查看服务器状态 [nonebot-plugin-picstatus](https://github.com/lgc2333/nonebot-plugin-picstatus)
<details>
<summary><b>指令：</summary></b>
<pre><p>运行状态（或者状态 / zt / yxzt / status）</p></pre>
</details>

## 40.查看谁艾特我 [nonebot_plugin_who_at_me](https://github.com/SEAFHMC/nonebot-plugin-who-at-me)
<details>
<summary><b>指令：</summary></b>
<pre><p>
/谁艾特我	查看到底是谁艾特了你
/clear_db	清理当前用户的消息记录
/clear_all	  清理全部消息记录
</p></pre>
</details>

## 41.撤回信息 [nonebot_plugin_withdraw](https://github.com/noneplugin/nonebot-plugin-withdraw)
<details>
<summary><b>指令：</summary></b>
<pre><p>
@机器人 撤回           # 撤回倒数第一条消息
@机器人 撤回 1        # 撤回倒数第二条消息
@机器人 撤回 0-3     # 撤回倒数三条消息
</p></pre>
</details>

## 42.智能聊天  [nonebot_plugin_smart_reply](https://github.com/zhulinyv/NJS/blob/Bot/src/plugins/nonebot_plugin_smart_reply/NoneBot2%E7%BC%9D%E5%90%88%E6%80%AA%E5%9B%9E%E5%A4%8D%E6%8F%92%E4%BB%B6.md)
<details>
<summary><b>指令：</summary></b>
<pre><p>
使用 青云客|小爱同学|OpenAI 的聊天api；
响应戳一戳：20%的机率掉落涩图，25%的机率回复可莉或纳西妲语音，20%的几率戳回去，35%的机率回复随机内容；
※※※具有屏蔽词拉黑功能。
由于 ChatGPT 是记录上文的，可以 艾特脑积水+api刷新对话 来重置对话。
由于 api 较多，可以通过 "查看api" 来查看当前使用的接口。
</p></pre>
<pre><p>
超管指令：以下指令均需要艾特
rm_qq + QQ号
切换小爱同学模式1/模式2|青云客|ChatGPTapi模式1/模式2
切换图片api
查看当前api
</p></pre>
</details>

## 43.60s读世界 [nonebot_plugin_read_60s](https://github.com/bingganhe123/60s-)
<details>
<summary><b>指令：</summary></b>
<pre><p>今日早报on+xx:xx(时间)；（计划任务）</p></pre>
</details>

## 44.历史上的今天 [nonebot-plugin-today-in-history](https://github.com/AquamarineCyan/nonebot-plugin-today-in-history)
<details>
<summary><b>指令：</summary></b>
<pre><p>历史上的今天；（计划任务）</p></pre>
</details>

## 45.游戏抽卡 [nonebot_plugin_gamedraw](https://github.com/HibiKier/nonebot_plugin_gamedraw)
<details>
<summary><b>指令：</summary></b>
<pre><p>
**1.原神**（当武器和角色无UP池时，所有抽卡命令都指向 '常驻池'）
原神N抽 （常驻池）
原神角色N抽 （角色UP池）
原神武器N抽 （武器UP池）
**2.赛马娘**
赛马娘N抽 （抽马）
赛马娘卡N抽 （抽卡）
**3.坎公骑冠剑**
坎公骑冠剑N抽 （抽角色）
坎公骑冠剑武器N抽 （抽武器）
**4.碧蓝航线**
碧蓝轻型N抽 （轻型池）
碧蓝重型N抽 （重型池）
碧蓝特型N抽 （特型池）
碧蓝活动N抽 （活动池）
</p></pre>
<p><b>其他命令&更新命令:</b></p>
<p><pre>
'重置原神抽卡'（重置保底）
'重载原神卡池'
'重载方舟卡池'
'重载赛马娘卡池'
'重载坎公骑冠剑卡池'

'更新明日方舟信息'
'更新原神信息'
'更新赛马娘信息'
'更新坎公骑冠剑信息'
'更新pcr信息'
'更新碧蓝航线信息'
'更新fgo信息'
'更新阴阳师信息'
</p></pre>
</details>

## 46.无数据库的轻量问答插件 [nonebot_plugin_word_bank2](https://github.com/kexue-z/nonebot-plugin-word-bank2)
<details>
<summary>指令：</summary>
<p>
<h4 dir="auto"><a id="user-content-开始使用" class="anchor" aria-hidden="true" href="#开始使用"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>开始使用</h4>
<h5 dir="auto"><a id="user-content-问答教学" class="anchor" aria-hidden="true" href="#问答教学"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>问答教学</h5>
<ul dir="auto">
<li>
<p dir="auto">设置词条命令由<code>问句</code>和<code>答句</code>组成。设置之后, 收到<code>消息</code>时触发。并非所有人都可以设置词条, 详见<a href="#permission">权限</a></p>
</li>
<li>
<p dir="auto">格式<code>[模糊|全局|正则|@]问...答...</code></p>
<ul dir="auto">
<li><code>模糊|正则</code> 匹配模式中可任性一个或<code>不选</code>, <code>不选</code> 表示 <code>全匹配</code></li>
<li><code>全局</code>, <code>@</code> 可与以上匹配模式组合使用</li>
</ul>
</li>
<li>
<p dir="auto">教学中可以使用换行</p>
<ul dir="auto">
<li>例如
<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="问
123
答
456"><pre class="notranslate"><code>问
123
答
456
</code></pre></div>
</li>
</ul>
</li>
<li>
<p dir="auto">问答句中的首首尾空白字符会被自动忽略</p>
</li>
<li>
<p dir="auto">私聊好友个人也可以建立属于自己的词库, 可以实现类似备忘录的功能</p>
</li>
</ul>
<h5 dir="auto"><a id="user-content-问句选项" class="anchor" aria-hidden="true" href="#问句选项"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>问句选项</h5>
<ul dir="auto">
<li>
<p dir="auto"><code>问...答...</code> 全匹配模式, 必须全等才能触发答</p>
</li>
<li>
<p dir="auto"><code>模糊问...答...</code> 当<code>问句</code>出现在<code>消息</code>里时则会触发</p>
</li>
<li>
<p dir="auto"><code>正则问...答...</code>, 当<code>问句</code>被<code>消息</code>正则捕获时则会匹配</p>
</li>
<li>
<p dir="auto">例如: 正则问[他你]不理答你被屏蔽了</p>
<table>
<thead>
<tr>
<th>消息</th>
<th>回复</th>
</tr>
</thead>
<tbody>
<tr>
<td>他不理</td>
<td>你被屏蔽了</td>
</tr>
<tr>
<td>他不理我</td>
<td>你被屏蔽了</td>
</tr>
<tr>
<td>你不理我</td>
<td>你被屏蔽了</td>
</tr>
</tbody>
</table>
</li>
<li>
<p dir="auto"><code>全局问...答...</code>, 在所有群聊和私聊中都可以触发, 可以和以上几种组合使用</p>
<ul dir="auto">
<li>例如: <code>全局模糊问 晚安 答 不准睡</code></li>
</ul>
</li>
<li>
<p dir="auto"><code>@问...答...</code>, 只有 <code>event.tome</code> 时才会触发，如被@、被回复时或在私聊中，可以和以上几种组合使用</p>
<ul dir="auto">
<li>例如: <code>全局模糊@问 晚安 答 不准睡</code></li>
</ul>
</li>
<li>
<p dir="auto">问句可包含<code>at</code> 即在 QQ 聊天中手动 at 群友</p>
<ul dir="auto">
<li>建议只在<code>问...答...</code>中使用</li>
<li>例如: <code>问 @这是群名称 答 老婆!</code></li>
</ul>
</li>
</ul>
<h5 dir="auto"><a id="user-content-答句选项" class="anchor" aria-hidden="true" href="#答句选项"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>答句选项</h5>
<ul dir="auto">
<li>
<p dir="auto"><code>/at</code> + <code>qq号</code>, 当答句中包含<code>/at</code> + <code>qq号</code>时将会被替换为@某人</p>
<ul dir="auto">
<li>例如: <code>问 群主在吗 答 /at 123456789在吗</code></li>
</ul>
</li>
<li>
<p dir="auto"><code>/self</code>, 当答句中包含<code>/self</code>时将会被替换为发送者的群昵称</p>
<ul dir="auto">
<li>例如: <code>问 我是谁 答 你是/self</code> (群昵称为: 我老婆)</li>
</ul>
</li>
<li>
<p dir="auto"><code>/atself</code>, 当答句中包含<code>/atself</code>时将会被替换为@发送者</p>
<ul dir="auto">
<li>例如: <code>问 谁是牛头人 答 @这是群昵称</code></li>
</ul>
</li>
</ul>
<h5 dir="auto"><a id="user-content-删除词条" class="anchor" aria-hidden="true" href="#删除词条"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>删除词条</h5>
<ul dir="auto">
<li>
<p dir="auto"><code>删除[模糊|全局|正则|@]词条</code> + 需要删除的<code>问句</code></p>
<ul dir="auto">
<li>例如: <code>删除全局模糊@词条 你好</code></li>
</ul>
</li>
<li>
<p dir="auto">以下指令需要结合自己的<code>COMMAND_START</code> 这里为 <code>/</code></p>
</li>
<li>
<p dir="auto">删除词库: 删除当前群聊/私聊词库</p>
<ul dir="auto">
<li>例如: <code>/删除词库</code></li>
</ul>
</li>
<li>
<p dir="auto">删除全局词库</p>
<ul dir="auto">
<li>例如: <code>/删除全局词库</code></li>
</ul>
</li>
<li>
<p dir="auto">删除全部词库</p>
<ul dir="auto">
<li>例如: <code>/删除全部词库</code></li>
</ul>
</li>
</ul>
<h5 dir="auto"><a id="user-content-查询词条" class="anchor" aria-hidden="true" href="#查询词条"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>查询词条</h5>
<ul dir="auto">
<li>
<p dir="auto">超管查询指定词库</p>
<ul dir="auto">
<li><code>查询[群|用户]{id}[全局][模糊|正则]词库</code></li>
<li>例如：<code>查询群123模糊词库</code> <code>查询用户114514词库</code> <code>查询全局词库</code></li>
</ul>
</li>
<li>
<p dir="auto">查询指定词库</p>
<ul dir="auto">
<li><code>查询[模糊|正则]词库</code></li>
<li>例如 <code>查询词库</code></li>
</ul>
</li>
<li>
<p dir="auto"><span id="user-content-permission">权限</span></p>
</li>
</ul>
<table>
<thead>
<tr>
<th></th>
<th>群主</th>
<th>群管理</th>
<th>私聊好友</th>
<th>超级用户</th>
</tr>
</thead>
<tbody>
<tr>
<td>增删词条</td>
<td>O</td>
<td>O</td>
<td>O</td>
<td>O</td>
</tr>
<tr>
<td>增删全局词条</td>
<td>X</td>
<td>X</td>
<td>X</td>
<td>O</td>
</tr>
<tr>
<td>删除词库</td>
<td>O</td>
<td>O</td>
<td>O</td>
<td>O</td>
</tr>
<tr>
<td>删除全局词库</td>
<td>X</td>
<td>X</td>
<td>X</td>
<td>O</td>
</tr>
<tr>
<td>删除全部词库</td>
<td>X</td>
<td>X</td>
<td>X</td>
<td>O</td>
</tr>
</tbody>
</table>
</p>
</details>

## 47.以图搜图 [nonebot_plugin_hikarisearch](https://github.com/noneplugin/nonebot-plugin-hikarisearch)
<details>
<summary><b>指令：</summary></b>
<pre><p>
搜图/saucenao搜图/iqdb搜图/ascii2d搜图/ehentai搜图/tracemoe搜图 + 图片
或 回复包含图片的消息，回复搜图
</p></pre>
</details>

## 48.快速搜索 [nonebot_plugin_giyf](https://github.com/KoishiMoe/nonebot-plugin-giyf)
<details>
<summary><b>指令：</summary></b>
<pre><p>
查询： ？前缀 关键词
添加（全局）搜索引擎： search.add search.add.global
快速添加： search.add(.global) [预置的搜索引擎名称] [自定义前缀（可选）]
删除（全局）搜索引擎： search.delete search.delete.global
查看搜索引擎列表： search.list search.list.global
**备注：**
其中所有非全局指令均需要在目标群中进行，所有全局指令均只有Bot管理员能执行
</p></pre>
</details>

## 49.黑名单（超管指令） [nonebot-plugin-blacklist](https://github.com/tkgs0/nonebot-plugin-blacklist)
<details>
<summary><b>指令：</b></summary>
<p>添加(删除)黑名单用户(群) + qid(@sb.)</p>
<p>添加黑名单所有好友(群)</p>
<p>查看用户(群聊)黑名单</p>
<p>重置黑名单</p>
<p>超级用户不受黑名单影响</p>
</details>

## 50.插件管理 [nonebot_plugin_manager](https://github.com/nonepkg/nonebot-plugin-manager)
<details>
<summary><b>指令：</b></summary>
<p dir="auto"><strong>使用前请先确保命令前缀为空，否则请在以下命令前加上命令前缀 (默认为<code>/</code>)。</strong></p>
<ul dir="auto">
<li>
<p dir="auto"><code>npm ls</code>查看当前会话插件列表</p>
<ul dir="auto">
<li><code>-s, --store</code>互斥参数，查看插件商店列表（仅超级用户可用）</li>
<li><code>-u user_id, --user user_id</code>互斥参数，查看指定用户插件列表（仅超级用户可用）</li>
<li><code>-g group_id, --group group_id</code>互斥参数，查看指定群插件列表（仅超级用户可用）</li>
<li><code>-a, --all</code>可选参数，查看所有插件（包括不含 Matcher 的插件）</li>
</ul>
</li>
<li>
<p dir="auto"><code>npm info 插件名</code>查询插件信息 （仅超级用户可用）</p>
</li>
<li>
<p dir="auto"><code>npm chmod mode plugin ...</code>设置插件权限（仅超级用户可用）</p>
<ul dir="auto">
<li><code>mode</code>必选参数，需要设置的权限，参考上文</li>
<li><code>plugin...</code>必选参数，需要设置的插件名</li>
<li><code>-a, --all</code>可选参数，全选插件</li>
<li><code>-r, --reverse</code>可选参数，反选插件</li>
</ul>
</li>
<li>
<p dir="auto"><code>npm block plugin...</code>禁用当前会话插件（需要权限）</p>
<ul dir="auto">
<li><code>plugin...</code>必选参数，需要禁用的插件名</li>
<li><code>-a, --all</code>可选参数，全选插件</li>
<li><code>-r, --reverse</code>可选参数，反选插件</li>
<li><code>-u user_id ..., --user user_id ...</code>可选参数，管理指定用户设置（仅超级用户可用）</li>
<li><code>-g group_id ..., --group group_id ...</code>可选参数，管理指定群设置（仅超级用户可用）</li>
</ul>
</li>
<li>
<p dir="auto"><code>npm unblock plugin...</code>启用当前会话插件（需要权限）</p>
<ul dir="auto">
<li><code>plugin...</code>必选参数，需要禁用的插件名</li>
<li><code>-a, --all</code>可选参数，全选插件</li>
<li><code>-r, --reverse</code>可选参数，反选插件</li>
<li><code>-u user_id ..., --user user_id ...</code>可选参数，管理指定用户设置（仅超级用户可用）</li>
<li><code>-g group_id ..., --group group_id ...</code>可选参数，管理指定群设置（仅超级用户可用）</li>
</ul>
</li>
</ul>
</details>

## 51.文本生成器 [nonebot-plugin-oddtext](https://github.com/noneplugin/nonebot-plugin-oddtext)
<details>
<summary><b>指令：</summary></b>
<pre><p>
指令 + 文本
▪ 抽象话 ▪ 火星文 ▪ 蚂蚁文 ▪ 翻转文字 ▪ 故障文字 ▪ 古文码 ▪ 口字码 
▪ 符号码 ▪ 拼音码 ▪ 还原符号码 / 解码符号码 ▪ 还原拼音码 / 解码拼音码 
▪ 问句码 ▪ 锟拷码 / 锟斤拷 ▪ rcnb ▪ 解码rcnb
</p></pre>
<p><b>指令及示例：</b></p>
<a href="https://smms.app/image/Gwc9Wuki15EjRs6" target="_blank"><img src="https://s2.loli.net/2022/11/04/Gwc9Wuki15EjRs6.png" ></a>
</details>

## 52.通用订阅推送 [nonebot-bison](https://github.com/felinae98/nonebot-bison)
<details>
<summary><b>指令：</summary></b>
<p>@脑积水发送："添加订阅"</p>
<p>支持的平台：</p>
<ul dir="auto">
<li>***微博
<ul dir="auto">
<li>图文</li>
<li>视频</li>
<li>纯文字</li>
<li>转发</li>
</ul>
</li>
<li>***Bilibili
<ul dir="auto">
<li>视频</li>
<li>图文</li>
<li>专栏</li>
<li>转发</li>
<li>纯文字</li>
</ul>
</li>
<li>***Bilibili 直播
<ul dir="auto">
<li>开播提醒</li>
</ul>
</li>
<li>***RSS
<ul dir="auto">
<li>富文本转换为纯文本</li>
<li>提取出所有图片</li>
</ul>
</li>
<li>***明日方舟
<ul dir="auto">
<li>塞壬唱片新闻</li>
<li>游戏内公告</li>
<li>版本更新等通知</li>
<li>泰拉记事社漫画</li>
</ul>
</li>
<li>***网易云音乐
<ul dir="auto">
<li>歌手发布新专辑</li>
<li>电台更新</li>
</ul>
</li>
<li>***FF14
<ul dir="auto">
<li>***游戏公告</li>
</ul>
</li>
<li>mcbbs 幻翼块讯
<ul dir="auto">
<li>Java 版本资讯</li>
<li>基岩版本资讯</li>
<li>快讯</li>
<li>基岩快讯</li>
<li>周边消息</li>
</ul>
</li>
</ul>
</details>

## 53.横屏/竖屏壁纸；兽耳图 random_wp
<details>
<summary><b>指令：</summary></b>
<pre><p>
来份[二次元/壁纸推荐/白毛/兽耳/星空/横屏壁纸/竖屏壁纸/萝莉/必应壁纸]
PUID + Pixiv画师ID
关键词搜图 + 关键词
</p></pre>
</details>

## 54.随机丁真/车蔡徐坤 random_dz_or_cxk
<details>
<summary><b>指令：</summary></b>
<pre><p>
我测你们码；随机丁真；丁真；一眼丁真
ikun；坤坤；小黑子
</p></pre>
</details>

## 55.疯狂星期四文案 [nonebot_plugin_crazy_thursday](https://github.com/MinatoAquaCrews/nonebot_plugin_crazy_thursday)
<details>
<summary><b>指令：</summary></b>
<pre><p>
1、天天疯狂，疯狂星期[一|二|三|四|五|六|日|天]，输入疯狂星期八等不合法时间将提示；
2、支持日文触发：狂乱[月|火|水|木|金|土|日]曜日；
</p></pre>
</details>

## 56.番剧资源搜索 [nonebot_plugin_animeres](https://github.com/Melodyknit/nonebot_plugin_animeres)
<details>
<summary><b>指令：</summary></b>
<pre><p>资源+番剧名称 或 动漫资源+番剧名称</p></pre>
</details>

## 57.战地1、5战绩查询 [nonebot-plugin-bfchat](https://github.com/050644zf/nonebot-plugin-bfchat)
<details>
<summary><b>指令：</summary></b>
<table>
<thead>
<tr>
<th>命令</th>
<th>作用</th>
<th>备注</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>bf help</code></td>
<td>返回本列表</td>
<td></td>
</tr>
<tr>
<td><code>bf init</code></td>
<td>初始化本群绑定功能，未初始化的群，群员不能使用绑定功能</td>
<td>仅SUPERUSER和群管理员有效</td>
</tr>
<tr>
<td><code>bf1 [玩家id]</code><br><code>bfv [玩家id]</code></td>
<td>查询 <code>[玩家id]</code>的bf1/bfv战绩信息</td>
<td>如果查询玩家是me，则会将数据保存至本地<br>且一小时内再次查询不会再发起请求</td>
</tr>
<tr>
<td><code>bf1 [玩家id] weapons</code><br><code>bfv&nbsp;[玩家id] weapons</code></td>
<td>查询 <code>[玩家id]</code>的bf1/bfv武器信息</td>
<td></td>
</tr>
<tr>
<td><code>bf1 [玩家id] vehicles</code><br><code>bfv&nbsp;[玩家id] vehicles</code></td>
<td>查询 <code>[玩家id]</code>的bf1/bfv载具信息</td>
<td></td>
</tr>
<tr>
<td><code>bf1 bind [玩家id]</code><br><code>bfv bind [玩家id]</code></td>
<td>将 对应游戏的 <code>[玩家id]</code>与命令发送人绑定，绑定后可使用 <code>me </code>代替 <code>[玩家id]</code><br>例如 <code>bfv me</code></td>
<td>bf1与bfv绑定不互通</td>
</tr>
<tr>
<td><code>bf1 list</code><br><code>bfv list</code></td>
<td>列出该服务器所有已绑定的bf1/bfv玩家信息</td>
<td>使用本地数据，不会自动更新</td>
</tr>
<tr>
<td><code>bf1 server [服务器名]</code><br><code>bfv server [服务器名]</code></td>
<td>查询名字包含 <code>[服务器名]</code>的bf1/bfv服务器</td>
<td></td>
</tr>
</tbody>
</table>
</details>

## 58.战舰世界水表查询 [hikari_bot](https://github.com/benx1n/HikariBot)
<details>
<summary>指令:</summary>
<a href="https://smms.app/image/dpAOKwfjlHrqaCe" target="_blank"><img src="https://s2.loli.net/2022/12/11/dpAOKwfjlHrqaCe.jpg" ></a>
</details>

## 59.词云 [nonebot-plugin-wordcloud](https://github.com/he0119/nonebot-plugin-wordcloud)
<details>
<summary><b>指令：</summary></b>
<pre><p>
今日词云、昨日词云、本周词云、本月词云、年度词云 或 历史词云 即可获取词云。
如果想获取自己的词云，可在上述指令前添加 我的，如 /我的今日词云。
</p></pre>
</details>

## 60.二次元化图像 [nonebot-plugin-cartoon](https://github.com/A-kirami/nonebot-plugin-cartoon)
<details>
<summary><b>指令：</summary></b>
<pre><p>二次元化/动漫化/卡通化 + 图片(支持回复图片)</p></pre>
</details>

## 61.群事件变化通知 notice
<details>
<summary><b>指令：</summary></b>
<pre><p>被动技能，被动技能：当有成员进退群、管理员变动、群文件上传时会提示。</p></pre>
</details>

## 62.碧蓝航线wiki Azur_Lane
<details>
<summary><b>指令：</summary></b>
<pre><p>
碧蓝航线wiki + 任意内容

任意内容可以为 角色名、武器名、其它 等，
与bilibili游戏wiki一致，wiki上有的都可以替换任意内容
</p></pre>
</details>

## 63.今天吃(喝)什么 what_to_eat_or_drink
<details>
<summary><b>指令：</summary></b>
<pre><p>
今(天|晚)(早上|晚上|中午|夜宵)吃什么
今(天|晚)(早上|晚上|中午|夜宵)喝什么
</p></pre>
</details>

## 64.中英互翻 [nonebot_plugin_easy_translate](https://github.com/nikissXI/nonebot_plugins/tree/main/nonebot_plugin_easy_translate)
<details>
<summary><b>指令：</summary></b>
<pre><p>
翻译/x译x [内容]
直接翻译是自动识别，x是指定语言
x支持：中（简中）、繁（繁中）、英、日、韩、法、俄、德
</p></pre>
</details>

## 65.记事本 [nonebot_plugin_note](https://github.com/Passerby-D/nonebot_plugin_note)
<details>
<summary><b>指令：</summary></b>
<ul dir="auto">
<li>
<p dir="auto"><code>note/记事/记事本 [记事内容]</code> 进行记事<br>
实例：<code>/记事 这里记录自己的一件事情，后期可以通过记事列表命令查看，记事删除命令删除</code></p>
</li>
<li>
<p dir="auto"><code>interval_note/间隔记事/间隔记事本 [记事内容] [时] [分] [秒]</code>，我将每隔[时][分][秒]提醒您一次<br>
实例：<code>/间隔记事 后面是时分秒，时分秒之间有空格，每隔一个周期提醒，比如这个010就是每隔1分钟提醒一次 0 1 0</code></p>
</li>
<li>
<p dir="auto"><code>cron_note/定时记事/定时记事本 [记事内容] （日）/（mon/tue/wed/thu/fri/sat/sun） （[时]） （[分]） [秒]</code>，我将在每月的[日][时][分][秒]/每周的[星期x][时][分][秒]/每天的[时][分][秒]/每时的[分][秒]/每分的[秒]提醒您一次<br>
实例：<br>
<code>/定时记事 每周的tue(星期二)日0时24分0秒提醒 tue 0 24 0</code><br>
<code>/定时记事 每月的29日0时26分0秒提醒 29 0 26 0 </code><br>
<code>/定时记事 每时的26分50秒提醒 26 50  </code><br>
<code>/定时记事 每分的26秒提醒 26 </code></p>
</li>
<li>
<p dir="auto"><code>date_note/单次记事/单次记事本 [记事内容] [年] [月] [日]（或今天/明天/后天/大后天） [时] [分] [秒]</code>，我将在这个时刻提醒您<br>
实例：<br>
<code>/单次记事 将在2022年11月29日0时31分0秒提醒 2022 11 29 0 31 00</code><br>
<code>/单次记事 将在2022年11月29日0时32分10秒提醒(今天就是这个日子) 今天 0 32 10 </code></p>
</li>
<li>
<p dir="auto"><code>note_list/记事列表/记事本列表</code> 来查看记事列表<br>
实例：<code>/记事列表</code></p>
</li>
<li>
<p dir="auto"><code>note_delete/记事删除/记事本删除 [记事内容]</code> 来删除一个记事项目<br>
实例：<code>/记事删除 这里记录自己的一件事情，后期可以通过记事列表命令查看，记事删除命令删除</code></p>
</li>
</ul>
<p><b>超管指令：</b></p>
<ul dir="auto">
<li>
<p dir="auto"><code>note_check/记事查看/记事本查看 [QQ账号]/all</code> 来查看某人/所有的记事项目<br>
实例：<br>
<code>/记事查看 all</code><br>
<code>/记事查看 123456</code></p>
</li>
<li>
<p dir="auto"><code>note_remove/记事移除/记事本移除 [QQ账号] [记事内容]</code> 来移除某人的某项记事内容<br>
实例：<code>/记事移除 123456 记事内容</code></p>
</li>
<li>
<p dir="auto"><code>note_spy/记事监控/记事本监控 [QQ账号]</code> 来监控某人的记事记录<br>
实例：<code>/note_spy 123456</code></p>
</li>
<li>
<p dir="auto"><code>note_spy_remove/记事监控移除/记事本监控移除 [QQ账号]</code> 来移除对某人的监控<br>
实例：<code>/记事本监控移除 123456</code></p>
</li>
<li>
<p dir="auto"><code>note_ban/记事禁止/记事本禁止 1/2（word/user） [内容]</code> 来设置禁用词/黑名单<br>
实例：<br>
<code>/记事禁止 1 1表示禁止的记事内容</code><br>
<code>/记事禁止 2 123456</code></p>
</li>
<li>
<p dir="auto"><code>note_ban_list/记事禁止列表/记事本禁止列表</code> 来查看禁用词和黑名单<br>
实例：<code>/记事禁止列表</code></p>
</li>
<li>
<p dir="auto"><code>note_ban_remove/记事禁止移除/记事本禁止移除 1/2（word/user） [内容]</code> 来移除禁用词/黑名单<br>
实例：<br>
<code>/记事禁止移除 1表示移除禁止的记事内容</code><br>
<code>/记事禁止移除 2 123456</code></p>
</li>
</ul>
</details>

## 66.ChatGPT(OpenAI)对话(使用token) [nonebot-plugin-chatgpt-plus](https://github.com/AkashiCoin/nonebot-plugin-chatgpt-plus)
<details>
<summary><b>指令：</summary></b>
<pre><p>
chat+任意聊天内容
（这个对话是记录上文的）
艾特脑积水+刷新对话 来**刷新**本轮对话
艾特脑积水+导出对话 来导出本轮对话id
艾特脑积水+导入对话+对话id+父消息id(可选) 来导入对话
</p></pre>
</details>

## 67.命令别名 [nonebot-plugin-alias](https://github.com/noneplugin/nonebot-plugin-alias)
<details>
<summary><b>指令：</summary></b>
<pre><p>
alias [别名]=[指令名称] 添加别名
alias [别名] 查看别名
alias -p 查看所有别名
unalias [别名] 删除别名
unalias -a 删除所有别名
默认只在当前群聊/私聊中生效，使用 -g 参数添加全局别名；增删全局别名需要超级用户权限
alias -g [别名]=[指令名称] 添加全局别名
unalias -g [别名] 删除全局别名
</p></pre>
</details>

## 68.群友召唤术 [nonebot_plugin_summon](https://github.com/zhulinyv/nonebot_plugin_summon)
<details>
<summary><b>指令：</summary></b>
<pre><p>
设置召唤术+昵称+QQ号
召唤+昵称
戳+昵称+数字

删除召唤术+昵称+QQ号
查看召唤术+昵称+QQ号

超管指令：切换召唤术
</p></pre>
</details>

## 69.戒色打卡日记 [nonebot_plugin_abstain_diary](https://github.com/Ikaros-521/nonebot_plugin_abstain_diary)
<details>
<summary><b>指令：</summary></b>
<pre><p>
戒色命令如下(【】中的才是命令哦，记得加命令前缀)：

【戒色目标】【设置戒色目标】，后面追加戒色目标天数。例如：/戒色目标 30
【戒色】【戒色打卡】，每日打卡，请勿中断喵。例如：/戒色
【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况。例如：/群戒色
【放弃戒色】【取消戒色】【不戒色了】，删除戒色目标。例如：/放弃戒色
【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况

财能使人贪，色能使人嗜，名能使人矜，潜能使人倚，四患既都去，岂在浮尘里。
</p></pre>
</details>

## 70.Apex查询 [nonebot-plugin-apex-api-query](https://github.com/H-xiaoH/nonebot-plugin-apex-api-query)
<details>
<summary><b>指令：</summary></b>
<pre><p>
<b>查询玩家信息:</b>
/bridge [玩家名称] 、 /玩家 [玩家名称]、 /uid [玩家UID]、 /UID [玩家UID]
<b>查询大逃杀地图轮换</b>
/maprotation 、 /地图
<b>查询猎杀者信息</b>
/predator 、 /猎杀
<b>查询复制器轮换</b>
/crafting 、 /制造
</p></pre>
</details>

## 71.ChatGPT(OpenAI)对话(使用多api) [nonebot-plugin-gpt3](https://github.com/chrisyy2003/lingyin-bot/tree/main/plugins/gpt3)
<details>
<summary><b>指令：</summary></b>
<pre><p>
<b>指令👈需要@👉描述</b>

刷新/重置对话👈是👉重置会话记录，开始新的对话
重置人格👈是👉重置AI人格
设置人格👈是👉设置AI人格
导出会话/导出对话👈是👉导出历史会话
自定义的指令前缀👈自定义是否需要@👉基本的聊天对话
chat/聊天/开始聊天👈是👉开始连续对话
stop/结束/结束聊天👈否👉结束连续聊天模式
</p></pre>
</details>

## 72.防撤回 [nonebot-plugin-antirecall](https://github.com/Jerry080801/nonebot-plugin-antirecall/)
<details>
<summary><b>指令：</summary></b>
<pre><p>
开启/添加防撤回, enable + 群号1 群号2 ...
关闭/删除防撤回, disable + 群号1 群号2 ...
查看防撤回群聊
开启/关闭绕过管理层
防撤回菜单
开启/关闭防撤回私聊gid uid
查看防撤回私聊
开启防撤回私聊 gid
关闭防撤回私聊
查看防撤回监听
添加/删除防撤回监听 gid	
</p></pre>
</details>

## 73.原神前瞻直播兑换码 [nonebot-plugin-gscode](https://github.com/monsterxcn/nonebot-plugin-gscode)
<details>
<summary><b>指令：</summary></b>
<pre><p>
gscode / 兑换码
</p></pre>
</details>

## 74.签到 sign_in
<details>
<summary><b>指令：</summary></b>
<pre><p>
签到
我的好感
</p></pre>
</details>

## 75.PING|HTTP [nonebot_plugin_ping](https://github.com/zhulinyv/nonebot_plugin_ping)
<details>
<summary><b>指令：</summary></b>
<pre><p>
ping  + url
示例：ping www.baidu.com
httpcat + HTTP状态码
示例：httpcat404
</p></pre>
</details>

## 76.文字表情包制作 [nonebot-plugin-memes](https://github.com/noneplugin/nonebot-plugin-memes)
<details>
<summary><b>指令：</summary></b>
<p dir="auto">发送“文字表情包”显示下图的列表：</p>
<div align="left" dir="auto">
  <a target="_blank" rel="noopener noreferrer nofollow" href="https://camo.githubusercontent.com/027c5cc19e141cec8d1144530d1c066f2114e7d4d50a9c58a5edb584abb9b2cc/68747470733a2f2f73322e6c6f6c692e6e65742f323032322f31312f32392f34393650414d6232354767547579712e6a7067" one-link-mark="yes"><img src="https://camo.githubusercontent.com/027c5cc19e141cec8d1144530d1c066f2114e7d4d50a9c58a5edb584abb9b2cc/68747470733a2f2f73322e6c6f6c692e6e65742f323032322f31312f32392f34393650414d6232354767547579712e6a7067" width="500" data-canonical-src="https://s2.loli.net/2022/11/29/496PAMb25GgTuyq.jpg" style="max-width: 100%;"></a>
</div>
<b>超管指令：</b>
<p dir="auto">发送 <code>启用文字表情/禁用文字表情 [表情名]</code>，如：<code>禁用文字表情 鲁迅说</code></p>
<p dir="auto">超级用户 可以设置某个表情包的管控模式（黑名单/白名单）</p>
<p dir="auto">发送 <code>全局启用文字表情 [表情名]</code> 可将表情设为黑名单模式；</p>
<p dir="auto">发送 <code>全局禁用文字表情 [表情名]</code> 可将表情设为白名单模式；</p>
</details>

## 77.兽语译者 [nonebot_plugin_animalVoice](https://github.com/ANGJustinl/nonebot_plugin_animalVoice/)
<details>
<summary><b>指令：</summary></b>
<table>
<thead>
<tr>
<th align="center">指令</th>
<th align="center">需要@</th>
<th align="center">范围</th>
<th align="center">说明</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center">[兽音加密]/[convert]</td>
<td align="center">否</td>
<td align="center">群聊/私聊</td>
<td align="center">发送需要加密的文字</td>
</tr>
<tr>
<td align="center">[兽音解密]/[deconvert]</td>
<td align="center">否</td>
<td align="center">群聊/私聊</td>
<td align="center">发送需要解密的文字</td>
</tr>
<tr>
<td align="center">[切噜一下]/[cherulize]</td>
<td align="center">否</td>
<td align="center">群聊/私聊</td>
<td align="center">发送需要解密的文字</td>
</tr>
<tr>
<td align="center">[切噜～]/[decherulize]</td>
<td align="center">否</td>
<td align="center">群聊/私聊</td>
<td align="center">发送需要解密的文字</td>
</tr>
</tbody>
</table>
</details>

## 78.AI画图(使用本地SDWebUI) [nonebot-plugin-novelai](https://github.com/sena-nana/nonebot-plugin-novelai)
<details>
<summary><b>指令：</summary></b>
<p dir="auto">.aidraw loli,cute --ntags big breast --seed 114514</p>
<ul dir="auto">
<li>指令使用shell解析输入的参数</li>
<li>square为指定画幅，支持简写为s，其他画幅为portrait和landscape，同样支持简写，默认为portrait</li>
<li>seed若省略则为自动生成</li>
<li>词条使用英文，使用逗号（中英都行，代码里有转换）分割，中文会自动机翻为英文，不支持其他语种</li>
<li>如果你不想用.aidraw，可以用 <strong>绘画</strong> 、 <strong>咏唱</strong> 或 <strong>召唤</strong> 代替。</li>
<li>在消息中添加图片或者回复带有图片的消息自动切换为以图生图模式</li>
</ul>
<p dir="auto">.aidraw on/off</p>
<ul dir="auto">
<li>启动/关闭本群的aidraw</li>
</ul>
<p dir="auto">.anlas check</p>
<ul dir="auto">
<li>查看自己拥有的点数</li>
</ul>
<p dir="auto">.anlas</p>
<ul dir="auto">
<li>查看帮助</li>
</ul>
<p dir="auto">.anlas [数字] @[某人]</p>
<ul dir="auto">
<li>将自己的点数分给别人(superuser点数无限)</li>
</ul>
<p dir="auto">.tagget [图片]</p>
<ul dir="auto">
<li>获取图片的TAG</li>
<li>如果你不想用.tagget，可以用 <strong>鉴赏</strong> 或 <strong>查书</strong> 代替。</li>
</ul>
</details>

## 79.对对联 [nonebot-plugin-couplets](https://github.com/CMHopeSunshine/nonebot-plugin-couplets)
<details>
<summary><b>指令：</summary></b>
<pre><p>
对联 <上联内容> (数量)
· 数量可选，默认为1
</p></pre>
</details>

## 80.整点报时 [nonebot-plugin-nowtime](https://github.com/Cvandia/nonebot_plugin_nowtime)
<details>
<summary><b>指令：</summary></b>
<table>
<thead>
<tr>
<th align="center">指令</th>
<th align="center">需要@</th>
<th align="center">范围</th>
<th align="center">说明</th>
<th align="center">权限</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center">北京时间</td>
<td align="center">否</td>
<td align="center">私聊、群聊</td>
<td align="center">查看现在时间</td>
<td align="center">任何</td>
</tr>
<tr>
<td align="center">开启、关闭整点报时</td>
<td align="center">否</td>
<td align="center">群聊</td>
<td align="center">开启或关闭群聊的整点报时</td>
<td align="center">群主，超管，管理员</td>
</tr>
<tr>
<td align="center">查看整点报时列表</td>
<td align="center">否</td>
<td align="center">群聊</td>
<td align="center">查看已开启整点报时的群聊</td>
<td align="center">群主，超管，管理员</td>
</tr>
</tbody>
</table>
</details>

## 81.星座查询 [nonebot_plugin_xingzuo](https://github.com/mengxinyuan638/xingzuo_luck)
<details>
<summary><b>指令：</summary></b>
<pre><p>
#星座 + 想要查询的星座
</p></pre>
</details>

## 82.心灵鸡汤 [nonebot_plugin_soup](https://github.com/Monarchdos/nonebot_plugin_soup)
<details>
<summary><b>指令：</summary></b>
<table> 
  <tbody><tr align="center">
    <th> 指令 </th>
    <th> 说明 </th>
  </tr>
  <tr align="center">
    <td> 鸡汤 </td>
    <td> 获取一碗心灵鸡汤 </td>
  </tr>
  <tr align="center">
    <td> 毒鸡汤 </td>
    <td> 获取一碗心灵毒鸡汤 </td>
  </tr>
</tbody></table>
</p></pre>
</details>

## 83.原神公告 [nonebot_plugin_yuanshen_notice](https://github.com/mengxinyuan638/nonebot_plugin_yuanshen_notice)
<details>
<summary><b>指令：</summary></b>
<pre><p>
原神公告
查看公告 + 公告序号
</p></pre>
</details>

## 84.B站分享卡片 [nonebot_plugin_bilibili_viode](https://github.com/ASTWY/nonebot_plugin_bilibili_viode)
<details>
<summary><b>指令：</summary></b>
<pre><p>
被动技能，为B站链接或ID生成海报
</p></pre>
</details>

## 85.反闪照 [nonebot_plugin_antiflash](https://github.com/MinatoAquaCrews/nonebot_plugin_antiflash)
<details>
<summary><b>指令：</summary></b>
<pre><p>
(被动技能)
超管指令：开启/启用/禁用反闪照
</p></pre>
</details>

## 86.leetcode每日一题 [nonebot_plugin_leetcode2](https://github.com/Nranphy/nonebot_plugin_leetcode2)
<details>
<summary><b>指令：</summary></b>
<pre><p>
**对指令/每日一题，/lc，/leetcode回复，发送今天的每日一题。**

**可搜索leetcode题目，指令/lc搜索 XXXXX，/lc查找 XXXXX，/leetcode搜索 XXXXX，将以关键词“XXXXX”进行leetcode搜索，发送搜索到的第一道题。**

**随机一题，指令/lc随机，/lc随机一题，/leetcode随机将请求leetcode随机一题，发送请求到的任意题目。**

**查询用户信息/lc查询 XXXXX，/lc查询用户 XXXXX，/leetcode查询 XXXXX，可查询用户基本信息，XXXXX为用户ID（不能用用户名）。**

**加入计划任务** 每日在指定时间向指定群和好友发送当天的每日一题
</p></pre>
</details>

## 87.摩尔质量计算 [nonebot-plugin-molar-mass](https://github.com/kifuan/nonebot-plugin-molar-mass)
<details>
<summary><b>指令：</summary></b>
<pre><p>
发送 **/摩尔质量 化学式** 或** /相对分子质量 化学式** 或 **/mol 化学式**。
</p></pre>
</details>

## 88.反向词典 [nonebot_plugin_wantwords](https://github.com/limnium/nonebot_plugin_wantwords)
<details>
<summary><b>指令：</summary></b>
<pre><p>
找词/反向词典/wantwords <模式> <描述>
模式可选：
zhzh：中—>中
zhen：中—>英
enzh：英—>中
enen：英—>英
<描述>即对希望找到的词的描述
</p></pre>
</details>

## 89.简易群管 [nonebot_plugin_easy_group_manager](https://github.com/zhulinyv/nonebot_plugin_easy_group_manager) 
<details>
<summary><b>指令：</summary></b>
<pre><p>
设置管理员 + @somebody
取消管理员 + @somebody
禁言/口球 + @somebody + 阿拉伯数字
解禁 + @somebody
移出 + @somebody
移出并拉黑 + @somebody
</p></pre>
</details>

## 90.对话超管 [nonebot_plugin_report_manager](https://github.com/Hiroshi12138/nonebot_plugin_report_manager)
<details>
<summary><b>指令：</summary></b>
<pre><p>
反馈开发者+内容
</p></pre>
</details>

## 91.BingGPT(Bing)对话(使用cookies) [nonebot-plugin-bing-chat](https://github.com/Harry-Jing/nonebot-plugin-bing-chat)
<details>
<summary><b>指令：</summary></b>
<pre><p>
chat3    与Bing进行对话
chat-new    新建一个对话
chat-history    返回历史对话
</p></pre>
</details>

## 92.P站图片查询 [nonebot_plugin_pixiv](https://github.com/anlen123/nonebot_plugin_pixiv)
<details>
<summary><b>指令：</summary></b>
<pre><p>
pixiv pid
pixivRank 1/7/30
</p></pre>
</details>

## 93.舔狗日记 [nonebot_plugin_dog](https://github.com/Reversedeer/nonebot_plugin_dog)
<details>
<summary><b>指令：</summary></b>
<pre><p>
舔狗日记
讲个笑话
文案

超管指令:
开启文案/关闭文案
</p></pre>
</details>

## 94.热搜 [nonebot_plugin_hotsearch](https://github.com/Astolfocat/nonebot_plugin_hotsearch)
<details>
<summary><b>指令：</summary></b>
<pre><p>
微博热搜
百度热搜
贴吧热搜
知乎热搜
B站热搜
</p></pre>
</details>

## 95.网易云热评 [nonebot_plugin_ncm_saying](https://github.com/techotaku39/nonebot-plugin-ncm-saying)
<details>
<summary><b>指令：</summary></b>
<pre><p>
网易云/网易云热评
</p></pre>
</details>

## 96.课表查询 [nonebot_plugin_course](https://github.com/InariInDream/nonebot_plugin_course)
<details>
<summary><b>指令：</summary></b>
<pre><p>
完整课表
本周课表
下周课表
上课
设置周数
查看课表
明日早八
</p></pre>
</details>

## 97.随机狗妈 [nonebot_plugin_randomnana](https://github.com/NanakoOfficial/nonebot_plugin_randomnana)
<details>
<summary><b>指令：</summary></b>
<pre><p>
狗妈/随机狗妈
</p></pre>
</details>

## 98.通用指令阻断 [https://github.com/KarisAya/nonebot_plugin_matcher_block](https://github.com/KarisAya/nonebot_plugin_matcher_block)
<details>
<summary><b>指令：</summary></b>
<pre><p>
添加阻断 指令 群
在本群屏蔽 指令

添加阻断 指令 冷却 300
在本群把 指令 设置成每个用户 300 秒冷却。

解除阻断 指令 群
在本群取消屏蔽该指令。

解除阻断 指令 冷却
在本群取消该指令的冷却。

查看阻断
查看本群被阻断的指令。
</p></pre>
</details>

## 99.OCR文本识别
<details>
<summary><b>指令：</summary></b>
<pre><p>
ocr
apiocr
</p></pre>
</details>

# 联系我：
QQ频道：[我的中心花园](https://pd.qq.com/s/8bkfowg3c)
仓库Issues：[Issues](https://github.com/zhulinyv/NJS/issues)
