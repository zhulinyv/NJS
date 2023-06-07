## 使用说明

查询： `？前缀 关键词`

添加（全局）搜索引擎： `search.add` `search.add.global`

快速添加： `search.add(.global) [预置的搜索引擎名称] [自定义前缀（可选）]`

删除（全局）搜索引擎： `search.delete` `search.delete.global`

查看搜索引擎列表： `search.list` `search.list.global`

**其中所有非全局指令均需要在目标群中进行，所有全局指令均只有Bot管理员能执行**

### 参数说明：

#### 快速添加
* 预置的搜索引擎名称：bot内置的引擎名称，目前有 `google` `bing` `baidu` `duckduckgo` `startpage` `zhwikipedia` `enwikipedia` `yahoo` `yandex`
* 自定义前缀：你可以使用自己的前缀来代替bot预设的前缀；关于“前缀”的说明见下

#### 前缀
就是你给这个搜索引擎起的代号，好记就行，例如给谷歌娘叫`go`，给度娘叫`bd`，等等。**只支持英文和数字**

#### 链接：
需要使用搜索引擎的搜索url，**而非首页url**；这类url的明显特征就是，其中带有`%s`，并且在搜索时`%s`会被替换成你的搜索关键字

例如：
```plaintext
Google: https://www.google.com/search?q=%s
Baidu: https://www.baidu.com/s?wd=%s
Bing: https://www.bing.com/search?q=%s
Duckduckgo: https://duckduckgo.com/?q=%s
```

获取这类链接有三种方法：

1. 使用搜索引擎

一般用`xxx search url`（xxx换成你要添加的引擎的名字）当关键词就能搜到


2. 查看浏览器设置

打开浏览器的搜索引擎设置，这里会出现默认配置好的搜索引擎，以及一些你使用过的搜索引擎。点击“编辑”，在“查询URL”一栏通常就是我们要找的

```plaintext
Tip：部分搜索引擎在此可能显示的有一些变量，例如 {google:baseURL}search?q=%s ，本插件无法识别这种，还请留意
```

3. 人工智能（不是

打开你要使用的搜索引擎，随便搜点什么（建议使用英文或数字，中文被编码后根本分不清……），把链接复制下来，把你原先输入的搜索关键字换成`%s`，大功告成！

```plaintext
Tip：某些搜索引擎的链接可能包含你的一些个人信息，建议在隐私浏览窗口中进行上述操作。
另外，搜索关键词后面的很多附加参数并不会影响搜索结果，因此一般可以去除，除非你明确知道它们被用于你想要的用途（例如开关安全搜索）
例如： https://www.bing.com/search?q=%s&form=xxxx 其中的 &from=xxxx就可以去掉 
```