<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot_plugin_groupmate_waifu

娶群友

</div>

## 需要安装
[nonebot_plugin_imageutils](https://github.com/noneplugin/nonebot-plugin-imageutils) PIL工具插件，方便图片操作，支持文字转图片

[nonebot_plugin_apscheduler](https://github.com/nonebot/plugin-apscheduler) APScheduler 定时任务插件
## 安装
    pip install nonebot_plugin_groupmate_waifu
## 使用
    nonebot.load_plugin('nonebot_plugin_groupmate_waifu')
## 配置
    # nonebot_plugin_groupmate_waifu
    waifu_cd_bye = 3600 # 分手冷却时间，默认1小时。
    waifu_save = false # 是否将cp记录保存为文件（避免重启bot丢失数据）。
	
    waifu_he = 25 # 在指定娶群友时，成功的概率25%
    waifu_be = 25 # 在指定娶群友时，失败的概率25%
    
    ## 成功就是娶到了，失败就是单身。如果这两个参数加起来不等于100那么剩下的概率是会随机娶一个。
    
    waifu_ntr = 20 # 别人有cp时被指定娶到的概率
    
    yinpa_he = 50 # 在指定透群友时，成功的概率50%
    yinpa_be = 0 # 在指定透群友时，失败的概率0%
    
    ## 同上，如果这两个参数加起来不等于100那么剩下的概率是会随机透一个。
    
## 功能介绍

__指令__：`娶群友`

纯爱 __双向奔赴版__，每天刷新一次，两个人会互相抽到对方。

__指令__：`娶群友@name`

有机会娶到at的人。。。

__指令__：`分手` `离婚`

雪花飘飘北风萧萧，天地一片苍茫~

__指令__：`本群cp`

查看当前群内的cp

__指令__：`群友卡池`

查看当前群可以娶到的群友列表

__指令__：`透群友`

ntr ~~宫吧老哥狂喜版~~，每次抽到的结果都不一样。

__指令__：`涩涩记录`

查看当前群的群友今日被透的次数，被透次数是跨群的，也就是说群友在别的群挨透也会在记录里显示出来。

~~群友背地里玩的挺花（bushi）~~
    
## 其他

获取群友头像的功能使用了 [nonebot-plugin-petpet（Nonebot2 插件，用于制作摸头等头像相关表情包）](https://github.com/noneplugin/nonebot-plugin-petpet) 中的代码

如有建议，bug反馈，以及讨论新玩法，新机制（或者单纯没有明白怎么用）可以来加群哦~

![群号](https://github.com/KarisAya/nonebot_plugin_game_collection/blob/master/%E9%99%84%E4%BB%B6/qrcode_1665028285876.jpg)
