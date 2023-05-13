<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-hoshino-sign

_✨ NoneBot 签到 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/zhulinyv/NJS.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-hoshino-sign">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-hoshino-sign.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

一个从 hoshino **~~抄~~借鉴**的 nonebot2 签到插件

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-hoshino-sign

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-hoshino-sign
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-hoshino-sign
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-hoshino-sign
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-hoshino-sign
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_hoshino_sign"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| NICKNAME | 是 | 脑积水 | 正经人一般都填了叭 |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 签到/盖章/妈! | 所有人 | 否 | 群聊、私聊、频道 | 签到(获得好感和 pcr 的印章) |
| 收集册(+QQ号/艾特) | 所有人 | 否 | 群聊、私聊、频道 | 查看自己或他人的收集进度 |

### 效果图

**(来自原作者的话) ↓↓↓**

![收集册](https://user-images.githubusercontent.com/98363578/185780489-d60b1484-c4af-4834-b1f4-6db569a91048.PNG)

[![p9cSLCR.png](https://s1.ax1x.com/2023/05/13/p9cSLCR.png)](https://imgse.com/i/p9cSLCR)

红的是已经收集到的，灰的是没收集的

有群排行（卷，都可以卷）

#### 素材来源：

https://tieba.baidu.com/p/6769790810
