<p align="center" >
  <a href="https://smms.app/image/plcUTsyMaz4QPgo"><img src="https://s2.loli.net/2023/01/21/plcUTsyMaz4QPgo.png" width="256" height="256" alt="NJS"></a>
</p>
<h1 align="center">脑积水|NJS</h1>
<h4 align="center">✨基于<a href="https://github.com/nonebot/nonebot2" target="_blank">NoneBot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的多功能QQ机器人✨</h4>

<p align="center">
    <a href="https://github.com/zhulinyv/NJS/raw/Bot/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
    <a href="https://pd.qq.com/s/8bkfowg3c"><img src="https://img.shields.io/badge/QQ频道交流-我的中心花园-blue?style=flat-square" alt="QQ guild"></a>
</p>


### 📣 前言

脑积水**缝合**了很多功能，因此**不亚于**[真寻](https://github.com/HibiKier/zhenxun_bot)、[早苗](https://space.bilibili.com/3191529)、[椛椛](https://github.com/FloatTech/ZeroBot-Plugin)等机器人，但**不同的**是：其它机器人项目大都有自己写的依赖和生态，由于个人能力有限，因此脑积水并没有我自己写的依赖和生态，但这样也带来了一些好处，基本上每个插件各自独立，不需要考虑依赖打架的问题，方便修改。

可能有人会问，自己利用 NoneBot 或者 ZeroBot 等框架搭建一个不是更好嘛？我会实话告诉你，你是正确的。**但是**如果插件用多用久了，你就会发现，各种指令冲突、优先级冲突，数据库打架，依赖打架，脑积水解决的正是这一问题。

当然，其它整合项目也不会存在冲突和打架的问题。脑积水内置了部分我自己写的东西，做了更多个性化处理来提升用户体验。

~~**说白了就是我是小垃姬 >_<，错的不是我，是这个世界啊啊啊！~\~**~~

## ⭐ 开始部署

⚠️ 你可能需要一点 Python 和有关计算机的知识。

⚠️ 需要两个 QQ 号，一个自己的，一个机器人的。

⚠️ 系统要求：Windows8 及以上，Linux(推荐:Ubuntu)~~，Mac(不会真的有人用 Mac 跑 Bot 叭)~~。

|⚠️ 推荐配置要求：|CPU|RAM||⚠️ 最低配置要求：|CPU|RAM|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|推荐配置|2线程+|2GB+||该配置下部分功能可能无法正常使用|1线程|1GB|

### 1️⃣ 安装 浏览器、解压软件、文本编辑器

此过程比较简单，不在附图。

警告：**不要**使用 Internet Explorer！如果你的电脑配置比较低，可以选择[百分浏览器](https://www.centbrowser.cn/)等占用小的浏览器，解压软件可以选择[7-Zip](https://www.7-zip.org/)等解压软件，文本编辑器任意，系统自带的记事本都可以，也可以使用比较高级一点的，比如 [VScode](https://code.visualstudio.com/)、[Notepad++](https://notepad-plus-plus.org/)，[Sublime](https://www.sublimetext.com/)等。**如果你的电脑上已经有其它同类软件，则跳过此步骤！**

### 2️⃣ 安装 Python

#### Windows下的安装

1、来到 [Python](https://www.python.org/downloads/windows/) 官网的下载页面，下载并安装 [Python](https://www.python.org/downloads/windows/)，下载 `3.8 及以上的版本`即可(这里我下载的是 3.10.9(64-bit)，如果你是 32 位操作系统，就下载 32 位版本)，但**不要**使用 3.11 版本及以上。

![image](https://user-images.githubusercontent.com/66541860/213637200-dca63b69-fd52-42d1-a3cd-f8b24f492186.png)

2、安装时，注意勾选 `Add python.exe to PATH` 。

![image](https://user-images.githubusercontent.com/66541860/213638736-729c083f-b2ca-41db-affd-31896db5d4cf.png)

3、出现此页面时，就表示你已经安装成功了，此时点击 Close 关闭窗口即可。

![image](https://user-images.githubusercontent.com/66541860/213639081-6ae459c9-6ef6-4dc1-9cb3-8755934dca2b.png)

4、验证你的下载，`Windows + R` 调出运行框，输入 `powershell` 按下回车。

![image](https://user-images.githubusercontent.com/66541860/213639939-d6489fde-998a-4a82-baed-140cc9123220.png)

5、输入 `python --version`，可以看到你的 Python 版本，这里显示的版本应该和刚刚你安装的版本一致，如果不一致，则说明你有多个 Python 或者下载时选错了版本。

![image](https://user-images.githubusercontent.com/66541860/213640522-b6e2756c-32b3-423e-8a7d-c800f5e1b5ef.png)

#### Ubuntu 和 Debian 下的安装

如果是20+的版本，系统会自带python3.8或3.10版本，可以直接使用。

如果是更低的版本，请自行安装 python3.8-3.10 版本。

Ubuntu可能没有自带pip命令，需要运行apt install python3-pip进行安装

Debian系统和Ubuntu系统同理。

#### CentOS 及其它发行版下的安装

建议更换Ubuntu，否则请自行编译安装Python3.8-3.10版本，~~耗子尾汁~~。

CentOS在后续也可能有更多的问题，因此强烈不建议您使用CentOS 如果你执意使用，后续出现的额外问题，例如 playwright 缺依赖，请自行搜索解决。

### 3️⃣ 安装 Git

#### Windows 下的安装

1、来到 [Git](https://git-scm.com/download/win) 官网的下载页面，下载并安装 [Git](https://git-scm.com/download/win) (如果你是 32 位操作系统，就下载 32 位版本)。

![image](https://user-images.githubusercontent.com/66541860/213641134-811ad3b9-bb91-4aa0-921e-b54f11214168.png)

2、下载完安装程序后运行，之后出现的选项均选择 Next 即可，最后安装完成选择 **Finish**。

![image](https://user-images.githubusercontent.com/66541860/213641800-4eac08d6-32e0-46de-8d9d-95516f17e83f.png)

#### Linux 下的安装

Linux发行版可以用其对应的包管理器安装，比如 Ubuntu 用 `apt install git`，CentOS 用 `yum install git`。

使用 `git --version` 来检查是否安装成功。

#### 备注：小派蒙等插件需要使用，如果不需要，可以将 NJS 目录下的 bot.py 文件中的第 32 行最前面写一个 # 注释掉这个插件。

### 4️⃣ 安装 rust

备注：仅插件ChatGPT(API模式)需要。

rust 仅 **Windows** 系统需要安装，其它系统**无需**安装。

如果不需要这个插件，可以去 NJS\src\plugins\nonebot_plugin_gpt3 目录将 **_\_init__.py** 文件重命名为 **init__.py**，此时就不需要安装 rust 了。

1、打开 powershell 分别输入以下两行命令并回车来进行换源操作。

```
$ENV:RUSTUP_DIST_SERVER='https://mirrors.ustc.edu.cn/rust-static'

$ENV:RUSTUP_UPDATE_ROOT='https://mirrors.ustc.edu.cn/rust-static/rustup'
```

2、下载 [rust](https://file.chrisyy.top/rustup-setup.exe)，双击运行，运行后**输入 1 并回车**即可开始安装。

![image](https://user-images.githubusercontent.com/66541860/214579123-ae92f347-dfb6-4eef-afd6-fb718c7ddd37.png)

3、中途会可能会出现 VSinstaller，点击 continue 继续安装，过程较慢，耐心等待。

![image](https://user-images.githubusercontent.com/66541860/214579360-c09be6e1-e968-44da-9a17-5734865197d9.png)

4、点击 Install 确认安装。

![image](https://user-images.githubusercontent.com/66541860/214580166-e3eb2e8b-73a6-44ef-b769-70ba0c908c77.png)

5、安装完成后，点击 close 关闭，等待 rust 继续安装。

![image](https://user-images.githubusercontent.com/66541860/214587212-a58b71aa-accc-498e-97d2-4e81bb9c2647.png)

6、输入 **1** 并回车继续安装，等待安装完成后关闭即可。

![image](https://user-images.githubusercontent.com/66541860/214587555-e7af481e-27b2-429d-b57f-e24afb46bb3d.png)

### 5️⃣ 安装 ffmpeg

#### Windows下的安装

1、来到 [ffmpeg](https://www.gyan.dev/ffmpeg/builds/#release-builds) 下载页面，下载最新版本即可。

![image](https://user-images.githubusercontent.com/66541860/213646782-8ed8dfe1-7784-4bae-b5c7-52566396ad6a.png)

2、解压，进入 .\bin 目录，并复制路径

![image](https://user-images.githubusercontent.com/66541860/213647847-b8a27508-f547-4d93-bdad-d347479035e0.png)

3、`Windows + R` 调出运行框，输入 `control` 按下回车打开控制面板，依次选择：**系统和安全-系统-高级系统设置-环境变量**

4、点击用户变量下方的**编辑**，然后在新弹出的窗口中点击**新建**，粘贴刚刚复制的路径，选择**确定**。

![image](https://user-images.githubusercontent.com/66541860/213648705-2df64a69-635b-4842-85bc-b012074a02d3.png)

5、**重启**计算机。至此，环境配置全部结束。🎉

#### Linux 下的安装

Ubuntu系统可以直接使用 `apt install ffmpeg` 来安装。

其他发行版请自行搜索安装教程，记得添加到环境变量中。

使用 `ffmpeg -version` 来检查是否安装成功。

#### 如果不安装，脑积水则无法发送**语音**和**视频**等信息。

### 6️⃣ 安装 脑积水

1、打开 powershell，输入 `git clone https://ghproxy.com/https://github.com/zhulinyv/NJS` 来克隆本仓库。

2、克隆过程较慢，耐心等待，大概会有 3.5GB 大小。

![image](https://user-images.githubusercontent.com/66541860/213651257-3f3bcb25-329f-4d8b-982a-591494e4513b.png)

### 7️⃣ 安装 Poetry 和依赖

1、输入 `cd NJS` 回车，来进入脑积水机器人目录。

2、输入 `.\requirements.bat` 回车，来安装依赖。依赖较多，耐心等待。

备注：如果出现报错，不予理睬，这些是由于各个作者上传 PyPI 时填写的相同依赖不同版本导致的，但实际可以正常运行。

![image](https://user-images.githubusercontent.com/66541860/213731127-e48e3962-f7be-4f24-85cd-de14cd861508.png)

### 8️⃣ 配置 脑积水

1、用记事本等文本编辑器打开 NJS 目录下的 **env.prod** 文件，里面已经填了一些我使用的配置，如果另有需要，可以对照 **env.else** 添加。

![image](https://user-images.githubusercontent.com/66541860/213742811-823a5010-be38-4386-9293-8f52920e5084.png)

2、在 `SUPERUSER=[""]` **引号**中填写你自己的 QQ 号作为超级管理员，如果你想拥有多个管理员，则需要用**英文**逗号隔开。

例如：`SUPERUSER=["1234567890", "0987654321"]`，其它配置项类似。

⚠️ 下一步骤非常重要

3、其它配置文件请参照 **env.else** 文件中的注释，或根据[《脑积水使用手册》](https://zhulinyv.github.io/NJS/)中具体插件仓库详细配置项说明在 **env.prod** 文件中配置。

注意：配置项较多，只有少部分是必须的，可以按需配置。

### 9️⃣ 登录 脑积水

1、在 NJS 目录中，输入 `poetry run nb run` 来运行脑积水。首次启动较慢，耐心等待。

如果出现类似下图所示报错，是因为 hikari_bot 插件的 API_TOKEN 未配置造成的，可以直接**忽略**或根据步骤 8 的第 3 步中的说明获取。但这并**不影响**其它插件的使用，如果不需要这个插件，可以去 `NJS\src\plugins\hikari_bot` 目录中将 **_\_init__.py** 文件重命名为 **init__.py**。

![image](https://user-images.githubusercontent.com/66541860/213744555-c22c8289-3789-4281-9781-5e372c5c3017.png)

2、启动后，浏览器访问链接 [http://127.0.0.1:13579/go-cqhttp](http://127.0.0.1:13579/go-cqhttp)，添加账号，手动输入账号，密码**不需要**输入，设备选择 iPad 或 Mac，如果你选择 Android，那么你的安卓手机上将无法登录，同理其它也是。

![image](https://user-images.githubusercontent.com/66541860/213741470-5392694c-1141-447c-89f9-4c77b60c6e88.png)

3、点击启动，然后等待二维码绘制完成后点击显示二维码，用机器人 QQ 号扫描二维码登录。

![image](https://user-images.githubusercontent.com/66541860/213741988-2faa1052-f52e-4d93-a94a-02af39569d8b.png)

<details>
<summary>4、如果服务器与手机不在同一网络下，<b>可能</b>会出现<b>无法登录</b>的情况，<b>如果</b>遇到，展开本条步骤查看解决办法。</summary>
  <pre><p>
  5、进入 `.\NJS\accounts\binary` 目录，复制 binary 目录下的 go-cqhttp.exe 文件到自己的电脑。
  6、双击运行，在之后弹出的对话框中均点击确定。
  <a><img src="https://user-images.githubusercontent.com/66541860/213905405-c1c39bf5-9e52-46ad-96d6-62a56d097bca.png"></a>
  7、双击 go-cqhttp.bat 文件运行，输入 3 选择<b>反向 Websocket 通信</b>。
  8、打开 config.yml 文件，将 uin 改为<b>机器人</b>的账号，最下方的 servers 部分改为如图所示内容保存。
  <a><img src="https://user-images.githubusercontent.com/66541860/213905588-344e85e4-0db6-4b44-b57c-a1f7ddb4824d.png"></a>
  <a><img src="https://user-images.githubusercontent.com/66541860/213905671-d6e63b62-39d7-4862-8923-ff4fdfa2db93.png"></a>
  9、此时再次运行 go-cqhttp.bat 文件，使用手机扫码登录。
  10、登录好后将 device.json 和 session.token 文件复制到 .\NJS\accounts\uin(机器人的QQ号) 目录即可。
</details>


### 🔟 使用 脑积水

1、**在群聊或私聊中发送 `njs帮助` 简便获取帮助。**

详细帮助查看：

2、《脑积水食用手册》：[https://zhulinyv.github.io/NJS](https://zhulinyv.github.io/NJS)

3、备用地址：[https://www.cnblogs.com/xytpz/p/NJS.html](https://www.cnblogs.com/xytpz/p/NJS.html)

4、更新：艾特脑积水说更新即可在线更新，更新成功后，艾特脑积水说重启来应用新的内容。

5、如有配置、部署或使用中的问题或建议，请通过本仓库 [Issues](https://github.com/zhulinyv/NJS/issues) 或 [博客首页](https://zhulinyv.github.io/) 联系方式联系我。

####  进阶使用

1、其它插件的安装：

  方法一：
  
  ```
  ① 在 NJS 目录执行 poetry run pip install xxx
  
  ② 在 pyproject.toml 文件第 44 行添加刚才安装的插件
  ```
  
![image](https://user-images.githubusercontent.com/66541860/214586235-f78e30fd-2f5d-4342-8c3c-3ba72eb95180.png)

  方法二：直接 clone 或下载某个插件仓库，把带有 _\_init__.py 的目录放到 NJS\src\plugins 目录下。

2、如果你已经安装并配置好脑积水且对 [Nonebot](https://v2.nonebot.dev) 有一定了解并懂得 Python 基础知识，那么就可以自己编写插件啦！！

## 🎉鸣谢：

感谢 [Nonebot 商店](https://v2.nonebot.dev/store)中的诸多贡献者。
