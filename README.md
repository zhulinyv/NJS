<p align="center" >
  <a href="https://smms.app/image/plcUTsyMaz4QPgo"><img src="https://s2.loli.net/2023/01/21/plcUTsyMaz4QPgo.png" width="256" height="256" alt="NJS"></a>
</p>
<h1 align="center">脑积水 | NJS</h1>
<h4 align="center">✨基于<a href="https://github.com/nonebot/nonebot2" target="_blank">NoneBot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的多功能QQ机器人✨</h4>

<p align="center">
    <a href="https://github.com/zhulinyv/NJS/raw/Bot/LICENSE"><img src="https://img.shields.io/github/license/zhulinyv/NJS" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-green" alt="python">
    <img src="https://img.shields.io/badge/nonebot-2.0.0-yellow" alt="nonebot-2.0.0">
    <img src="https://img.shields.io/badge/go--cqhttp-1.0.0-red" alt="go--cqhttp">
    <a href="https://pd.qq.com/s/8bkfowg3c"><img src="https://img.shields.io/badge/QQ频道交流-我的中心花园-blue?style=flat-square" alt="QQ guild"></a>
</p>


### 💬 前言

脑积水**缝合**了很多功能, 因此**不亚于**[真寻](https://github.com/HibiKier/zhenxun_bot)、[早苗](https://space.bilibili.com/3191529)、[椛椛](https://github.com/FloatTech/ZeroBot-Plugin)等机器人, 但**不同的**是: 其它机器人项目大都有自己写的依赖和生态, 由于个人能力有限, 因此脑积水并没有我自己写的依赖和生态, 但这样也带来了一些好处, 基本上每个插件各自独立, 不需要考虑依赖打架的问题, 方便修改。

可能有人会问, 自己利用 NoneBot 或者其它框架搭建一个不是更好嘛？我会实话告诉你, 你是正确的。**但是**如果插件用多用久了, 你就会发现, 各种指令冲突、优先级冲突, 数据库打架, 依赖打架……

当然, 其它整合项目也不会存在冲突和打架的问题。脑积水内置了部分我自己写的东西, 做了更多个性化处理来提升用户体验。

~~**说白了就是我是小垃姬 >_<, 错的不是我, 是这个世界啊啊啊！~\~**~~

## 🎉 开始部署

⚠️ 你可能需要一点 Python 和有关计算机的知识。

⚠️ 需要两个 QQ 号, 一个自己的, 一个机器人的。

⚠️ 系统要求: Windows8 及以上, Linux(推荐:Ubuntu)~~, Mac(不会真的有人用 Mac 跑 Bot 叭)~~。

|⚠️ 推荐配置要求: |CPU|RAM||⚠️ 最低配置要求: |CPU|RAM|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|推荐配置|2线程+|2GB+||该配置下部分功能可能无法正常使用|1线程|1GB|

### 0️⃣ Star 本项目

o(〃＾▽＾〃)o

1、点击仓库右上角的 Star。![image](https://user-images.githubusercontent.com/66541860/231970470-fe1c6368-8c05-4701-8074-2443bd8ad13d.png)

2、变成 Starred 即表示成功。![image](https://user-images.githubusercontent.com/66541860/231970624-618b0e8c-06dc-4099-9aba-4993ab267e4a.png)

ヾ(≧▽≦*)o

### 1️⃣ 安装 浏览器、解压软件、文本编辑器

此过程比较简单, 不再附图。

1、警告: **不要**使用 Internet Explorer！如果你的电脑配置比较低, 可以选择 [百分浏览器](https://www.centbrowser.cn/) 等占用小的浏览器, 解压软件可以选择 [7-Zip](https://www.7-zip.org/)、[WinRAR](https://www.ghxi.com/winrarlh.html) 等解压软件, 文本编辑器任意, 系统自带的记事本都可以, 也可以使用比较高级一点的, 比如 [VScode](https://code.visualstudio.com/)、[Sublime](https://www.sublimetext.com/) 等。**如果你的电脑上已经有其它同类软件, 则跳过此步骤！**

### 2️⃣ 安装 Python

#### Windows下的安装

1、来到 [Python](https://www.python.org/downloads/windows/) 官网的下载页面, 下载并安装 [Python](https://www.python.org/downloads/windows/), 下载 `3.10 版本`即可(这里我下载的是 3.10.9(64-bit), 如果你是 32 位操作系统, 就下载 32 位版本), 但**不要**使用 3.11 版本及以上; 实际上 3.8 版本以上就可以, 但部分插件需要, 因此 3.10 最为合适。

![image](https://user-images.githubusercontent.com/66541860/213637200-dca63b69-fd52-42d1-a3cd-f8b24f492186.png)

2、安装时, 注意勾选 `Add python.exe to PATH` 。

![image](https://user-images.githubusercontent.com/66541860/213638736-729c083f-b2ca-41db-affd-31896db5d4cf.png)

3、出现此页面时, 就表示你已经安装成功了, 此时点击 Close 关闭窗口即可(Disable path length limit 解除路径长度限制, 可选)。

![image](https://user-images.githubusercontent.com/66541860/213639081-6ae459c9-6ef6-4dc1-9cb3-8755934dca2b.png)

4、验证你的下载, `Windows + R` 调出运行框, 输入 `powershell` 按下回车。

![image](https://user-images.githubusercontent.com/66541860/213639939-d6489fde-998a-4a82-baed-140cc9123220.png)

5、输入 `python --version`, 可以看到你的 Python 版本, 这里显示的版本应该和刚刚你安装的版本一致, 如果不一致, 则说明你有多个 Python 或者下载时选错了版本。

![image](https://user-images.githubusercontent.com/66541860/213640522-b6e2756c-32b3-423e-8a7d-c800f5e1b5ef.png)

#### Ubuntu 和 Debian 下的安装

如果是 20+ 的版本, 系统会自带 Python3.8 或 3.10 版本, 如果是 3.10 版本可以直接使用。

如果是更低的版本, 请自行安装 3.10 版本。

Ubuntu 可能没有自带pip命令, 需要运行 `apt install python3-pip` 进行安装

Debian 系统和 Ubuntu 系统同理。

#### CentOS 及其它发行版下的安装

建议更换 Ubuntu, 否则请自行编译安装Python3.8-3.10版本, ~~耗子尾汁~~。

CentOS 在后续也可能有更多的问题, 因此强烈不建议使用 CentOS 如果你执意使用, 后续出现的额外问题, 例如 playwright 缺依赖, 请自行搜索解决。

### 3️⃣ 安装 Git

#### Windows 下的安装

1、来到 [Git](https://git-scm.com/download/win) 官网的下载页面, 下载并安装 [Git](https://git-scm.com/download/win) (如果你是 32 位操作系统, 就下载 32 位版本)。

![image](https://user-images.githubusercontent.com/66541860/213641134-811ad3b9-bb91-4aa0-921e-b54f11214168.png)

2、下载完安装程序后运行, 之后出现的选项均选择 Next 即可, 最后安装完成选择 **Finish**。

![image](https://user-images.githubusercontent.com/66541860/213641800-4eac08d6-32e0-46de-8d9d-95516f17e83f.png)

#### Linux 下的安装

Linux发行版可以用其对应的包管理器安装, 比如 Ubuntu 用 `apt install git`, CentOS 用 `yum install git`。

使用 `git --version` 来检查是否安装成功。

### 4️⃣ 安装 ffmpeg

#### Windows下的安装

1、来到 [ffmpeg](https://www.gyan.dev/ffmpeg/builds/#release-builds) 下载页面, 下载最新版本即可。

![image](https://user-images.githubusercontent.com/66541860/213646782-8ed8dfe1-7784-4bae-b5c7-52566396ad6a.png)

2、解压, 进入 .\bin 目录, 并复制路径

![image](https://user-images.githubusercontent.com/66541860/213647847-b8a27508-f547-4d93-bdad-d347479035e0.png)

3、`Windows + R` 调出运行框, 输入 `control` 按下回车打开控制面板, 依次选择: **系统和安全-系统-高级系统设置-环境变量**

4、点击用户变量下方的**编辑**, 然后在新弹出的窗口中点击**新建**, 粘贴刚刚复制的路径, 选择**确定**。

![image](https://user-images.githubusercontent.com/66541860/213648705-2df64a69-635b-4842-85bc-b012074a02d3.png)

5、**重启**计算机。至此, 环境配置全部结束。🚧

#### Linux 下的安装

Ubuntu系统可以直接使用 `apt install ffmpeg` 来安装。

其他发行版请自行搜索安装教程, 记得添加到环境变量中。

使用 `ffmpeg -version` 来检查是否安装成功。

#### 如果不安装, 脑积水则无法发送**语音**和**视频**等信息。

### 5️⃣ 安装 脑积水

1、打开 powershell, 输入 `git clone --depth=1 https://ghproxy.com/https://github.com/zhulinyv/NJS` 来克隆本仓库。

上方链接是镜像源地址, 如有需要, 可将 `https://ghproxy.com/` 删除来直接通过 GitHub 克隆本仓库。

2、仓库较大, 克隆过程较慢, 耐心等待, 大概会有 4GB 大小。

![image](https://user-images.githubusercontent.com/66541860/213651257-3f3bcb25-329f-4d8b-982a-591494e4513b.png)

备注: 若出现克隆失败的情况, 多半是由于仓库太大造成的, 如果遇到可以尝试用如下命令调整 http 的请求最大容量或直接下载 Zip 文件。

`git config --global http.postBuffer 数字`。(数字即为调整后的最大容量)

### 6️⃣ 安装 字体

**可选**: 安装字体: 部分插件需要用到特定字体, 不安装不影响使用。

**Windows** 将 ./NJS/data/fonts 目录下的字体文件复制到 /Windows/Fonts 即可; 

**Linux** 将 ./NJS/data/fonts 目录下的字体文件复制到 /usr/share/fonts/truetype 然后用 `sudo fc-cache -fv` 更新字体缓存。

备注: 如果出现中文乱码, 此时必需安装中文字体。

### 7️⃣ 安装 Poetry 和依赖

1、输入 `cd NJS` 回车, 来进入脑积水机器人目录。

2、输入 `.\requirements.bat` 回车, 来安装依赖。依赖较多, 耐心等待。

如果安装依赖过程中出现问题, 尝试使用 `poetry run pip install -r requirements.txt` 来安装。

![image](https://user-images.githubusercontent.com/66541860/213731127-e48e3962-f7be-4f24-85cd-de14cd861508.png)

备注: 部分 Linux 可能无法直接运行这个批处理脚本, 此时可以手动执行以下命令来安装依赖。

```
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install poetry
poetry install
```

### 8️⃣ 配置 脑积水

1、用记事本等文本编辑器打开 NJS 目录下的 **env.prod** 文件, 里面已经填了一些我使用的配置, 如果另有需要, 可以对照 **env.else** 添加。

![image](https://user-images.githubusercontent.com/66541860/213742811-823a5010-be38-4386-9293-8f52920e5084.png)

2、在 `SUPERUSER=[""]` **引号**中填写你自己的 QQ 号作为超级管理员, 如果你想拥有多个管理员, 则需要用**英文**逗号隔开。

例如: `SUPERUSER=["1234567890", "0987654321"]`, 其它配置项类似。

注意: 脑积水使用了频道补丁, 因此也可以处理频道信息, 但频道的超管 ID 与 QQ 群的不同, 需要额外配置。

⚠️ 下一步骤非常重要

3、其它配置文件请参照 **env.else** 文件中的注释, 或根据[《脑积水使用手册》](https://zhulinyv.github.io/NJS/)中具体插件仓库详细配置项说明在 **env.prod** 文件中配置。

注意: 配置项较多, 只有少部分是必须的, 可以按需配置。

目前只有 ChatGPT, Apex, WoWs, 和风天气, Ai画图, 颜值评分, BingGPT 这几个必需 apikey。

### 9️⃣ 登录 脑积水

1、在 NJS 目录中, 输入 `poetry run nb run` 或 `poetry run python bot.py` 来运行脑积水。首次启动较慢, 耐心等待。

如果出现类似下图所示报错, 是因为 hikari_bot 插件的 API_TOKEN 和 nonebot_plugin_bing_chat 的 cookies 未配置造成的, 可以直接**忽略**或根据步骤 7 的第 3 步中的说明获取。但这并**不影响**其它插件的使用, 如果不需要这个插件, 可以去 `NJS\src\plugins\hikari_bot` 和 `NJS\src\plugins\nonebot_plugin_bing_chat` 目录中将 **_\_init__.py** 文件重命名为 **init__.py**。

![image](https://user-images.githubusercontent.com/66541860/213744555-c22c8289-3789-4281-9781-5e372c5c3017.png)
![image](https://user-images.githubusercontent.com/66541860/227728475-d85df47f-5e48-4c90-97f9-282c0c57aaa4.png)
![image](https://user-images.githubusercontent.com/66541860/227728502-4da142d3-e9db-4a90-b049-906fc6f2d434.png)


2、启动后, 浏览器访问链接 [http://127.0.0.1:13579/go-cqhttp](http://127.0.0.1:13579/go-cqhttp), 添加账号, 手动输入账号, 密码**不需要**输入, 设备选择 aPad 或 iPad, 如果你选择 Android, 那么你的安卓手机上将无法登录, 同理其它也是。

![image](https://user-images.githubusercontent.com/66541860/213741470-5392694c-1141-447c-89f9-4c77b60c6e88.png)

3、点击启动, 然后等待二维码绘制完成后点击显示二维码, 用机器人 QQ 号扫描二维码登录。

![image](https://user-images.githubusercontent.com/66541860/213741988-2faa1052-f52e-4d93-a94a-02af39569d8b.png)

<details>
<summary>4、<b>如果</b>服务器与手机不在同一网络下, 登录提示<b>复杂的网络环境</b>, 展开本条步骤查看解决办法。</summary>
  <pre><p>
  1、进入 `.\NJS\accounts\binary` 目录, 复制 binary 目录下的 go-cqhttp.exe(Linux 版没有扩展名) 文件到自己的电脑。
  2、双击运行, 在之后弹出的对话框中均点击确定(Linux 版无需此步骤)。
  <a><img src="https://user-images.githubusercontent.com/66541860/213905405-c1c39bf5-9e52-46ad-96d6-62a56d097bca.png"></a>
  3、运行 go-cqhttp.bat 文件(Linux 运行 go-cqhttp), 输入 3 选择<b>反向 Websocket 通信</b>。
  <a><img src="https://user-images.githubusercontent.com/66541860/227727773-83cea251-478d-4022-b0a9-596084e044d3.png"></a>
  4、打开 config.yml 文件, 将 uin 改为<b>机器人</b>的账号, 最下方的 universal 部分改为 <code>"ws://127.0.0.1:13579/onebot/v11/ws"</code>, 保存。
  <a><img src="https://user-images.githubusercontent.com/66541860/213905588-344e85e4-0db6-4b44-b57c-a1f7ddb4824d.png"></a>
  <a><img src="https://user-images.githubusercontent.com/66541860/213905671-d6e63b62-39d7-4862-8923-ff4fdfa2db93.png"></a>
  5、此时再次运行 go-cqhttp.bat 文件(Linux 运行 go-cqhttp), 使用手机扫码登录。
  6、登录好后将 device.json 和 session.token 文件复制到 .\NJS\accounts\uin(机器人的QQ号) 目录即可。
</details>

<details>
<summary>5、<b>如果</b>服务器与手机在同一网络下, 登录提示<b>账号被冻结</b>, 展开本条步骤查看解决办法。</summary>
  <pre><p>
  1、更换登录协议重试(优先 aPad 或 iPad, 其它协议可能导致部分信息无法处理)。
  2、如果更换登录协议无法解决, 进入 `.\NJS\accounts\binary` 目录, 运行 binary 目录下的 go-cqhttp.exe(Linux 版没有扩展名)。
  3、在弹出的对话框中均点击确定(Linux 版无需此步骤), 之后运行 go-cqhttp.bat(Linux 运行 go-cqhttp), 输入 3 选择<b>反向 Websocket 通信</b>。
  <a><img src="https://user-images.githubusercontent.com/66541860/213905405-c1c39bf5-9e52-46ad-96d6-62a56d097bca.png"></a>
  <a><img src="https://user-images.githubusercontent.com/66541860/227727773-83cea251-478d-4022-b0a9-596084e044d3.png"></a>
  4、打开 config.yml 文件, 将 uin 改为<b>机器人</b>的账号, password 填写机器人账号密码, 最下方的 universal 部分改为 <code>"ws://127.0.0.1:13579/onebot/v11/ws"</code>, 保存。
  <a><img src="https://user-images.githubusercontent.com/66541860/227727909-476bbfbb-9801-4314-b05c-ea16c23356af.png"></a>
  <a><img src="https://user-images.githubusercontent.com/66541860/213905671-d6e63b62-39d7-4862-8923-ff4fdfa2db93.png"></a>
  5、此时再次运行 go-cqhttp.bat 文件(Linux 运行 go-cqhttp), 按照提示输入 1 自动获取 ticket, 如开启了设备锁, 输入 1 选择<b>短信验证</b>。
  <a><img src="https://user-images.githubusercontent.com/66541860/227727962-943f121d-4d8d-4708-a3ae-d981670997a8.png"></a>
  6、登录好后将 device.json 和 session.token 文件复制到 .\NJS\accounts\uin(机器人的QQ号) 目录即可。
</details>

### 🔟 使用 脑积水

1、**在群聊或私聊中发送 `njs帮助` 简便获取帮助。**

详细帮助查看: 

2、《脑积水食用手册》: [https://zhulinyv.github.io/NJS](https://zhulinyv.github.io/NJS)

3、备用地址: [https://www.cnblogs.com/xytpz/p/NJS.html](https://www.cnblogs.com/xytpz/p/NJS.html)

4、仓库文档: [https://github.com/zhulinyv/NJS/blob/Bot/NJS.md](https://github.com/zhulinyv/NJS/blob/Bot/NJS.md)

5、默认 WebUI 地址: [http://127.0.0.1:13579/LittlePaimon/login](http://127.0.0.1:13579/LittlePaimon/login)

说明: 可以通过 WebUI 对脑积水进行较为方便的图形化管理。基于 [小派蒙](https://github.com/CMHopeSunshine/LittlePaimon) WebUI 样式修改。

6、更新: 艾特脑积水说更新即可在线更新, 更新成功后, 艾特脑积水说重启来应用新的内容。

7、如有配置、部署或使用中的问题或建议, 请通过本仓库 [Issues](https://github.com/zhulinyv/NJS/issues) 或 [博客首页](https://zhulinyv.github.io/) 联系方式联系我。

#### 进阶使用

1、其它插件的安装: 

  方法一: 在 NJS 目录执行 `poetry run nb plugin install xxx`。

  方法二: 
  
  ```
  ① 在 NJS 目录执行 poetry run pip install xxx
  
  ② 在 pyproject.toml 文件如下位置添加刚才安装的插件
  ```
  
![image](https://user-images.githubusercontent.com/66541860/214586235-f78e30fd-2f5d-4342-8c3c-3ba72eb95180.png)

  方法三: 直接 clone 或下载某个插件仓库, 把带有 _\_init__.py 的目录放到 NJS\src\plugins 目录下。

2、如果你已经安装并配置好脑积水且对 [NoneBot](https://v2.nonebot.dev) 有一定了解并懂得 Python 基础知识, 那么就可以自己编写插件啦！！

## 👥 鸣谢: 

感谢 [NoneBot](https://github.com/nonebot/nonebot2)中的诸多贡献者。