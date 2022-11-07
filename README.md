# 脑积水！！
基于 nonebot 的QQ(想用别的适配器我也不拦你)机器人——脑积水！（超级缝合怪）

## 开始使用：

### 环境配置：
1、安装 [Python 3.9.10（不低于3.9即可）](https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe)（注意勾选`Add Python 3.9 to PATH`）。

2、安装 `poetry` 作为Python环境和包管理器。
`pip install poetry`

3、安装 `git` , [下载地址](https://git-scm.com/downloads)。

4、配置 `ffmpeg`, [下载地址](https://ffmpeg.org/)；[来源于网络的教程](https://zhuanlan.zhihu.com/p/118362010)

### 安装脑积水：
1、克隆或直接下载本仓库。`git clone https://github.com/zhulinyv/NJS.git`

2、克隆后 进入 **NJS** 目录`cd NJS`, 运行 `poetry run pip install -r package.txt` 进行安装。

3、配置请参照注释。

4、安装 **go-cqhttp** 插件 `poetry run nb plugin install nonebot-plugin-gocqhttp` , 安装好后, 启动脑积水（在**NJS**目录执行`poetry run nb run`）, 浏览器访问链接[http://127.0.0.1:13579/go-cqhttp](http://127.0.0.1:13579/go-cqhttp)。添加账号配置后重启即可。

### 脑积水帮助文档：[https://zhulinyv.github.io/NJS/](https://zhulinyv.github.io/NJS/)
1、在群聊或私聊中发送 `脑积水帮助` 简便获取帮助。

### 其它：
1、更详细的内容请参照[脑积水帮助文档](https://zhulinyv.github.io/NJS/)，里面含有每个插件的**GitHub仓库链接**。

2、由于插件均为本地导包，所以首次运行可能出现`no model named xxx`, 可能需要安装个别依赖。

3、缺少的依赖请使用`poetry run pip install xxx`进行安装。

4、脑积水包含两个自学习插件, 其中，`./LittlePaimon/plugins/Paimon_Chat` 环境配置~~较麻烦~~ **相当麻烦**，可以直接删除。

### 如有问题：请通过[博客首页](https://zhulinyv.github.io/)联系方式联系我。
