<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot_plugin_russian_ban

轮盘禁言小游戏

</div>

## 安装
    pip install nonebot_plugin_russian_ban
## 使用
    nonebot.load_plugin('nonebot_plugin_russian_ban')
## 介绍

此功能需要给bot设置为管理员。

### 开始游戏

__指令__：`无赌注轮盘` `自由轮盘`

开启群内随机ban人游戏

__指令__：`拨动滚轮` `重新装弹`

重置子弹的位置。

__指令__：`开枪`

顾名思义，开枪。

__指令【管理员，群主，超管】__：`开启自由轮盘` `关闭自由轮盘`

控制当前群内可否发起自由轮盘游戏，【管理员，群主，超管】可无视此设定在群内发起轮盘。

### 快捷禁言/解禁

此项功能是为轮盘禁言打扫战场用。

__指令【管理员，群主，超管】__：`@bot添加名单 代号 @name`

在本群添加重点关照人群，以便通过代号快捷禁言，可以一次设置多人。
    
    示例：
    
    管理员：@bot添加名单 机器人@bot 文酱@本群喵喵怪文酱 小叶子@茶酱
    机器人：添加成功
    
    管理员：禁言小叶子
    系统提示：小叶子被禁言1天
    
    管理员：解封小叶子
    系统提示：小叶子被解除禁言
    
__指令【管理员，群主，超管】__：`禁言 代号/@name`

给@的成员禁言1小时。可@多人。如果给群友设置过代号，可以通过代号快捷禁言

__指令【管理员，群主，超管】__：`解封` `解封 代号/@name`

给@的成员解除禁言。可@多人。如果给群友设置过代号，可以通过代号快捷解除禁言。

如果没有指定成员会返回当前被封成员列表。之后可以根据提示进一步设置。
    
## 其他

如有建议，bug反馈，以及讨论新玩法，新机制（或者单纯没有明白怎么用）可以来加群哦~

![群号](https://github.com/KarisAya/nonebot_plugin_game_collection/blob/master/%E9%99%84%E4%BB%B6/qrcode_1665028285876.jpg)
