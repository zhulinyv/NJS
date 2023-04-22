# nonebot2智能(障)回复插件

## 功能

基于1个词库、3个聊天 API 和 2个图片 API 的缝合怪。

### 安装方式:

~~1、nb plugin install nonebot-plugin-smart-reply~~
    
~~2、pip install nonebot-plugin-smart-reply~~
    
    3、Download Zip
 
### env配置项:

**.env完全不配置不影响插件运行, 但是部分功能会无法使用**

| 配置名 | 类型 | 默认 | 说明 |
| :---: | :---: | :---: | :---: |
| BAN_DATA_PATH | str | "./data/ban_CD" | 存放被屏蔽用户 CD 时间，删掉可提前解除屏蔽 |
| SETU_API | bool | True | 戳一戳图片默认使用的api, True 为 MirlKoi; False 为 Pixiv |
| API_NUM | int | 2 | 聊天默认使用的api, 1 为 小爱同学; 2 为 青云客; 3 为 ChatGPT |
| API_CD_TIME | int | 180 | 使用 ChatGPT 模式 1 时的对话冷却时间(秒)(防止造成频繁请求造成超时) |
| BAN_CD_TIME | int | 21600 | 当有人骂了 bot 时的屏蔽时间(秒) |
| XIAOAI_APIKEY | str | 寄 | 小爱同学的 ApiKey (申请方式看下文) |
| OPENAI_API_KEY | str | 寄 | 模式2 OpenAI 的 Apikey (申请方式看下文) |
| OPENAI_MAX_TOKENS | str | 2000 | 模式 2 时返回的最大文本字数 |
| BOT_NICKNAME | str | 脑积水 | bot 的昵称 |
| BOT_MASTER | str | (๑•小丫头片子•๑) | bot 主人的昵称 |
| CHATGPT_SESSION_TOKEN | str | None | ChatGPT 的 session token (获取看下文)(如配置则优先使用) |
| CHATGPT_ACCOUNT | str | None | ChatGPT 的登录邮箱(不配置则使用 session token) |
| CHATGPT_PASSWORD | str | None | ChatGPT 的登录密码(不配置则使用 session token) |
| CHATGPT_REFRESH_INTERVAL	 | int | 30 | ChatGPT 的 session token 自动刷新时间(秒) |
| CHATGPT_TIMEOUT | int | 15 | 请求超时的时间 |
| CHATGPT_API | str | [https://chat.openai.com/](https://chat.openai.com/) | API 地址，可配置反代 |

### 小爱同学 apiKey 的申请步骤:

    1. 进入网页 https://apibug.cn/doc/xiaoai.html
    2. 右上角注册登录
    3. 左边接口列表
    4. 找到"小爱同学AI"零元购买
    5. 请求接口中 "&apiKey="后面的值就是你的apiKey, 填在.env内
       
### ChatGPT session token 的获取步骤:

    1. 登录 https://chat.openai.com/chat
    2. 按 F12 打开控制台
    3. 切换到 Application/应用 选项卡，找到 Cookies
    4. 复制 __Secure-next-auth.session-token 的值，配置到 CHATGPT_SESSION_TOKEN 即可

### ChatGPT API 的获取步骤:

    1. 请注册 OpenAI
    2. 在 https://beta.openai.com/account/api-keys 获取

## 开始使用 *★,°*:.☆(￣▽￣)/$:*.°★* 。

**全部指令均需要艾特机器人(私聊不用()**
| 指令 | 说明 |
| :---: | :---: |
| @bot + 任意内容 | 开始聊天 |
| @bot + 查看api | 查看当前使用的api |
| @bot + api刷新对话 | 使用 ChatGPT 时，刷新本轮对话 |

**可以响应戳一戳: 20% 概率掉落图片; 25% 概率回复语音; 20% 概率戳回去; 35% 概率回复文字**

| 超管指令 | 说明 |
| :---: | :---: |
| @bot + rm_qq + QQ号 | 提前解除被屏蔽用户 |
| @bot + 切换图片api | 切换图片api |
| @bot + 切换小爱同学模式1/模式2/青云客/ChatGPTapi模式1/ChatGPTapi模式2 | 切换聊天api |
