<p align="center" >
  <a href="https://smms.app/image/plcUTsyMaz4QPgo"><img src="https://s2.loli.net/2023/01/21/plcUTsyMaz4QPgo.png" width="256" height="256" alt="NJS"></a>
</p>
<h1 align="center">脑积水 | NJS</h1>
<h4 align="center">✨基于<a href="https://github.com/nonebot/nonebot2" target="_blank">NoneBot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的多功能QQ机器人✨</h4>

<p align="center">
    <a href="https://github.com/zhulinyv/NJS/raw/Bot/LICENSE"><img src="https://img.shields.io/github/license/zhulinyv/NJS" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-green" alt="python">
    <img src="https://img.shields.io/badge/nonebot-2.0.0+-yellow" alt="nonebot-2.0.0">
    <img src="https://img.shields.io/badge/go--cqhttp-1.0.0+-red" alt="go--cqhttp">
    <a href="https://pd.qq.com/s/8bkfowg3c"><img src="https://img.shields.io/badge/QQ频道交流-我的中心花园-blue?style=flat-square" alt="QQ guild"></a>
</p>


## 💬 前言

脑积水**缝合**了很多功能, 因此**不亚于**[真寻](https://github.com/HibiKier/zhenxun_bot)、[早苗](https://space.bilibili.com/3191529)、[椛椛](https://github.com/FloatTech/ZeroBot-Plugin)等机器人, 但**不同的**是: 其它机器人项目大都有自己写的依赖和生态, 由于个人能力有限, 因此脑积水并没有我自己写的依赖和生态, 但这样也带来了一些好处, 基本上每个插件各自独立, 不需要考虑依赖打架的问题, 方便修改。

可能有人会问, 自己利用 NoneBot 或者其它框架搭建一个不是更好嘛？我会实话告诉你, 你是正确的。**但是**如果插件用多用久了, 你就会发现, 各种指令冲突、优先级冲突, 数据库打架, 依赖打架……

当然, 其它整合项目也不会存在冲突和打架的问题。脑积水内置了部分我自己写的东西, 做了更多个性化处理来提升用户体验。所以，如果你也想安装好多好多好多插件，但有不想自己动手解决这些冲突，那么，脑积水是一个不错的选择。

~~**说白了就是我是小垃姬 >_<, 错的不是我, 是这个世界啊啊啊！~\~**~~

## ✨ 已经实现的功能

<details>

<summary>展开查看: </summary>

发送 "njs帮助" 后得到的内容:

![c402cf601e1b88472e16da8517a36f32](https://github.com/zhulinyv/NJS/assets/66541860/f2de3ecf-c0ff-4bc7-bd01-b0a36c316dda)

</details>

## 🎉 开始部署

⚠️ 你可能需要一点 Python 和有关计算机的知识。

⚠️ 需要两个 QQ 号, 一个自己的, 一个机器人的。

⚠️ 系统要求: Windows8 及以上, Linux(推荐:Ubuntu)~~, Mac(不会真的有人用 Mac 跑 Bot 叭), Android 自己研究一下 (bushi)~~。

|⚠️ 推荐配置要求: |CPU|RAM||⚠️ 最低配置要求: |CPU|RAM|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|推荐配置|2线程+|2GB+||该配置下部分功能可能无法正常使用|1线程|1GB|

⚠️ 如果遇到任何部署、使用或二次开发上的问题或建议, 可以在 QQ频道: [我的中心花园-开发交流](https://pd.qq.com/s/8bkfowg3c) 找到我。

### 0️⃣ Star 本项目

<details>

<summary>详细帮助: </summary>

o(〃＾▽＾〃)o

1、点击仓库右上角的 Star。![image](https://user-images.githubusercontent.com/66541860/231970470-fe1c6368-8c05-4701-8074-2443bd8ad13d.png)

2、变成 Starred 即表示成功。![image](https://user-images.githubusercontent.com/66541860/231970624-618b0e8c-06dc-4099-9aba-4993ab267e4a.png)

ヾ(≧▽≦*)o

</details>

### 1️⃣ 安装 浏览器、解压软件、文本编辑器

此过程比较简单, 不再附图。

1、警告: **不要**使用 Internet Explorer！如果你的电脑配置比较低, 可以选择 [百分浏览器](https://www.centbrowser.cn/) 等占用小的浏览器, 解压软件可以选择 [7-Zip](https://www.7-zip.org/)、[WinRAR](https://www.ghxi.com/winrarlh.html) 等解压软件(如果你选择下载源码而不用 Git), 文本编辑器任意, 系统自带的记事本都可以, 也可以使用比较高级一点的, 比如 [VScode](https://code.visualstudio.com/)、[Sublime](https://www.sublimetext.com/) 等。**如果你的电脑上已经有其它同类软件, 则跳过此步骤！**

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

1、打开 powershell, 输入 `git clone -b Bot --depth=1 https://ghproxy.com/https://github.com/zhulinyv/NJS` 来克隆本仓库。

上方链接是镜像源地址, 如有需要, 可将 `https://ghproxy.com/` 删除来直接通过 GitHub 克隆本仓库; `-b Bot` 参数为仅克隆 Bot 分支, 如有需要, 可将其删除以 clone 全部分支。

2、仓库较大, 克隆过程较慢, 耐心等待, 大概会有 4GB 大小。

![image](https://user-images.githubusercontent.com/66541860/213651257-3f3bcb25-329f-4d8b-982a-591494e4513b.png)

备注: 若出现克隆失败的情况, 多半是由于仓库太大造成的, 如果遇到可以尝试用 GitHub 源地址克隆或直接下载 Zip 文件或使用如下命令调整 http 的请求最大容量。

`git config --global http.postBuffer 数字`。(数字即为调整后的最大容量)

如果实在是无法克隆或者下载, 这里有一份[度盘链接](https://pan.baidu.com/s/1JmW1EcgqvZ6Tnsf1m5n0rg?pwd=ytpz), 提取码: ytpz ,下载后可以使用 `git pull` 进行更新。

3、关于额外的资源, 大部分插件会在启动时或启动后自动下载资源。如果出现由于网络问题或其它问题导致的下载失败, 可参照具体插件仓库说明手动下载。

### 6️⃣ 安装 字体

**可选**: 安装字体: 部分插件需要用到特定字体, 不安装不影响使用。

**Windows** 将 ./NJS/data/fonts 目录下的字体文件复制到 /Windows/Fonts 即可; 

**Linux** 将 ./NJS/data/fonts 目录下的字体文件复制到 /usr/share/fonts/truetype 然后用 `sudo fc-cache -fv` 更新字体缓存。

备注: 如果出现中文乱码, 此时必需安装中文字体。

### 7️⃣ 安装 Poetry 和依赖

1、输入 `cd NJS` 回车, 来进入脑积水机器人目录。

2、依次输入以下指令:

```
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install poetry
poetry install
```

第一行为全局换源(清华源)操作。

第二行安装 poetry 。

第三行用 poetry 创建环境并安装依赖。

备注: 换源不是必须操作, 按需使用, 国内换国内源可加速安装过程。

如果依赖安装过程中出现问题, 尝试使用这条命令安装 `poetry run pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` 。


### 8️⃣ 配置 脑积水

1、用记事本等文本编辑器打开 NJS 目录下的 **env.prod** 文件, 里面已经填了一些我使用的配置, 如果另有需要, 可以对照具体插件仓库详细配置项说明在 **env.prod** 文件中添加。

2、在 `SUPERUSER=[""]` **引号**中填写你自己的 QQ 号作为超级管理员, 如果你想拥有多个管理员, 则需要用**英文**逗号隔开。

例如: `SUPERUSER=["1234567890", "0987654321"]`, 其它配置项类似。

注意: 脑积水使用了频道补丁, 因此也可以处理频道信息, 但频道的超管 ID 与 QQ 群的不同, 需要额外配置。

⚠️ 这一步骤非常重要

注意: 其它配置文件请根据[《脑积水使用手册》(已过时)](https://zhulinyv.github.io/NJS/)中具体插件仓库详细配置项说明在 **env.prod** 文件中配置。

注意: 大部分插件都可以在[NoneBot商店](https://nonebot.dev/store)中找到, 配置项较多, 只有少部分是必须的, 可以按需配置。

### 9️⃣ 登录 脑积水

⚠️ 由于 TX 风控, 以下登录方法**可能**无法正常使用, 请留意 [go-cqhttp 仓库 Issue](https://github.com/Mrs4s/go-cqhttp/issues) 和 [go-cqhttp 插件仓库 Issue](https://github.com/mnixry/nonebot-plugin-gocqhttp/issues) 。

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
  </p></pre>
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
  </p></pre>
</details>

<details>
<summary>6、<b>如果</b>出现 code: 45, 登录提示<b>账号被冻结</b>, 展开本条步骤查看解决办法。</summary>
  <pre><p>
  <b>I: Windows 端: </b>
  1、克隆或下载该仓库 <a href="https://github.com/rhwong/unidbg-fetch-qsign-onekey">unidbg-fetch-qsign-onekey</a>。
  2、双击运行 Start_Qsign.bat , 也可以直接右键 Qsign_Monitor.ps1 使用 powershell 运行, 这个脚本用来检测 qsign 是否掉线, 若掉线则重新运行。
  注意: 这个脚本目前存在 bug 不好用: 无法准确检测是否掉线, 会导致 qsign 重复运行。 但由于 qsign 特性, 重复运行后检测到端口冲突会自己关闭, 如此往复, 会占用服务器资源, 影响性能, 不建议使用。
  3、txlib_version 目前选择默认的 8.9.63 即可, (该部分具有时效性, 此教程写于 2023年7月24日 10点45分, 如果想要更新版本, 将在同目录下生成的 txlib_version.json 删除重新配置即可)。 
  4、host 保持默认 127.0.0.1 , port 不可以选择默认(脑积水也是这个端口), 请填写 24680, 你喜欢其它数字也可以(≧∇≦)ﾉ 
  注意: (如果脑积水和 qsign 不在同一服务器上, 请按需填写)。
  5、key 填写 <b>114514</b> , 注意这里填写<b>114514</b> (qsign 的作者填写的是 114514, 但是一键包的作者却改成了 1145141919810)。 
  <a><img src="https://github.com/zhulinyv/NJS/assets/66541860/bbf874ac-dd12-475e-8984-06e42e776563"></a>
  6、打开 <b>./NJS/accounts/你的脑积水的 QQ 号/config-template.yml</b> 文件在 account 下(如图所示选中部分)填写 <b>sign-server: 'http://127.0.0.1:24680'</b>
  <a><img src="https://github.com/zhulinyv/NJS/assets/66541860/b05f6672-b5a0-4e5b-817c-19ba1f6c0013"></a>
  <hr>
  <b>II: 其它服务端: 看这里~!!</b>
  <a href="https://github.com/fuqiuluo/unidbg-fetch-qsign/wiki">unidbg-fetch-qsign wiki</a>
  <a href="https://github.com/fuqiuluo/unidbg-fetch-qsign/wiki/%E9%83%A8%E7%BD%B2%E5%9C%A8Linux"><b>→ Linux 直达 ←</b></a>
  <a href="https://github.com/fuqiuluo/unidbg-fetch-qsign/wiki/%E9%83%A8%E7%BD%B2%E5%9C%A8Windows"><b>→ Windows 直达 ←</b></a>
  <a href="https://github.com/fuqiuluo/unidbg-fetch-qsign/wiki/"><b>→ Android 回家 ←</b></a>
  <a href="https://github.com/fuqiuluo/unidbg-fetch-qsign/wiki/%E9%83%A8%E7%BD%B2%E5%9C%A8Docker"><b>→ Docker 直达 ←</b></a>
  <hr>
  <b>III: 注意</b>
  1、使用 Windows 一键端需要使用<a href="https://github.com/Mrs4s/go-cqhttp/actions/runs/5504923059"> dev 分支下的 go-cqhttp</a>(可能需要登录 GitHub 才可以下载)。
  2、若服务器性能太低, 使用 qsign 服务器出现超时问题, 可以自行修改 go-cqhttp 源代码延长超时时间并进行编译。如果你不会 Go 语言或编译, 可以在本地部署 qsign 并成功登录后上传 device.json 和 session.token 文件复制到 .\NJS\accounts\uin(机器人的QQ号) 目录即可。
  <hr>
  unidbg-fetch-qsign wiki 截图。
  <a><img src="https://github.com/zhulinyv/NJS/assets/66541860/bd9b1ed8-d252-4847-8aa2-7a3ab3b8760f"></a>
  </p></pre>
</details>

### 🔟 使用 脑积水

1、**在群聊或私聊中发送 `njs帮助` 简便获取帮助。**

好多好多好多功能, ~~我自己都还没完全用过~~, 所以你可能需要一段时间来适应。

**详细帮助查看:**

2、脑积水有一个自己的帮助插件, 如果需要对帮助进行修改, 请参照 `.\NJS\data\njs_help\help.json` 文件进行修改。

3、《脑积水食用手册》(已过时): [https://zhulinyv.github.io/NJS](https://zhulinyv.github.io/NJS)

4、备用地址(已过时): [https://www.cnblogs.com/xytpz/p/NJS.html](https://www.cnblogs.com/xytpz/p/NJS.html)

5、默认 WebUI 地址: [http://127.0.0.1:13579/LittlePaimon/login](http://127.0.0.1:13579/LittlePaimon/login)

说明: 可以通过 WebUI 对脑积水进行较为方便的图形化管理。基于 [小派蒙](https://github.com/CMHopeSunshine/LittlePaimon) WebUI 样式修改。

6、更新: 艾特脑积水说更新即可在线更新, 更新成功后, 艾特脑积水说重启来应用新的内容。

7、如有配置、部署或使用中的问题或建议, 请通过本仓库 [Issues](https://github.com/zhulinyv/NJS/issues)、QQ频道: [我的中心花园-开发交流](https://pd.qq.com/s/8bkfowg3c) 或 [博客首页](https://zhulinyv.github.io/) 联系方式联系我。

#### 进阶使用

1、其它插件的安装: 

  方法一: 在 NJS 目录执行 `poetry run nb plugin install xxx`。

  方法二: 
  
  ```
  ① 在 NJS 目录执行 poetry run pip install xxx
  
  ② 在 pyproject.toml 文件如下位置添加刚才安装的插件
  ```

  [https://github.com/zhulinyv/NJS/blob/09adc88317a9a31fcec1ed63c662354fc16b7d42/pyproject.toml#L121](https://github.com/zhulinyv/NJS/blob/09adc88317a9a31fcec1ed63c662354fc16b7d42/pyproject.toml#L121)

  方法三: 直接 clone 或下载某个插件仓库, 把带有 _\_init__.py 的目录放到 NJS\src\plugins 目录下。

2、如果你已经安装并配置好脑积水且对 [NoneBot 文档](https://nonebot.dev/docs/)有一定了解并懂得 Python 基础知识, 那么就可以自己编写插件啦！！

## 👥 鸣谢: 

**感谢 [NoneBot](https://github.com/nonebot/nonebot2) 中的诸多贡献者。**

**感谢 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 中的诸多贡献者。**

**感谢 [unidbg-fetch-qsign](https://github.com/fuqiuluo/unidbg-fetch-qsign) 中的诸多贡献者。**

<hr>
<img width="300px" src="https://count.getloli.com/get/@zhulinyv?theme=rule34"></img>
