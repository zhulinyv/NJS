## 获取setu

    命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
    
    张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
    
    r18: 不填则不会出现r18图片, 填了会根据r18模式管理中的数据判断是否可返回r18图片
    
    关键词: 任意, 多tag使用空格分开 (可不填)
    
    参考 (空格可去掉):   
    
        setu 10张 r18 白丝
        
        setu 10张 白丝
        
        setu r18 白丝
        
        setu 白丝
        
        setu

## 权限管理

注意：

1. 全部群聊或私聊默认均未在白名单, 但可以通过设置 setu_enable_private = True 将私聊默认全部开启, 群聊还需通过白名单管理指令添加。
2. superuser在任意聊天或在设置 setu_enable_private = True 的情况下好友私聊中, 会话均不受cd和白名单本身的影响, 但会受 撤回时长, r18, 最大张数 的影响。
3. 在群聊中默认以该群作为操作对象, 但在私聊需要用户提供操作对象。
4. 此部分的事件响应器均为 on_command 生成的, 触发时需要带有[命令头](https://v2.nonebot.dev/docs/api/config#Config-command_start)。

白名单管理：

    setu_wl add  添加会话至白名单 eg: setu_wl add user_114514/group_1919810
    setu_wl del  移出会话自白名单 eg: setu_wl del user_114514/group_1919810

黑名单管理：

    setu_ban add  添加会话至黑名单 eg: setu_ban add user_114514/group_1919810
    setu_ban del  移出会话自黑名单 eg: setu_ban del user_114514/group_1919810

r18模式管理：

    setu_r18 on  开启会话的r18模式 eg: setu_r18 on group_1919810
    setu_r18 off 关闭会话的r18模式 eg: setu_r18 off group_1919810

cd时间更新:

    setu_cd xxx  更新会话的冷却时间, xxx为int类型的参数 eg: setu_cd 10 group_1919810

撤回时间更新:

    setu_wd xxx  撤回前等待的时间, xxx为int类型的参数 eg: setu_wd 10 group_1919810

最大张数更新:

    setu_mn xxx  单次发送的最大图片数, xxx为int类型的参数   eg: setu_mn 10 group_1919810

更换setu代理服务器:

    setu_proxy xxx   使用的代理服务器, xxx 为 string 类型的参数
    警告: 这部分带了一个ping代理服务器的操作, 这个响应器是superuser only, 用了os.popen().read()操作, 请不要尝试给自己电脑注入指令

​    

## 其他指令

获取插件帮助信息:

    "setu_help" | "setu_帮助" | "色图_help" | "色图_帮助"

查询黑白名单:

    "setu_roste" | "色图名单"


数据库更新:
>此指令默认从 github.com[^2] 拉取数据库，如果无法访问可以考虑使用科学上网或更换镜像或者手动从仓库下载换上去。

    setu_db      从指定的路径拉取 lolicon.db 数据库，默认为此仓库