from amis import (
    Action,
    ActionType,
    Alert,
    AmisAPI,
    App,
    DisplayModeEnum,
    Flex,
    Form,
    Horizontal,
    Html,
    InputNumber,
    InputPassword,
    InputTag,
    InputText,
    LevelEnum,
    Page,
    PageSchema,
    Remark,
    Select,
    Switch,
    TableColumn,
    TableCRUD,
    Tpl,
    Wrapper,
)

from ..l4d2_utils.config import NICKNAME

logo = Html(
    html="""
<p align="center">
    <a href="https://github.com/Agnes4m/nonebot_plugin_l4d2_server">
        <img src="https://ghproxy.com/https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_l4d2_server/main/image/logo.png"
         width="256" height="256" alt="l4d2-server">
    </a>
</p>
<h1 align="center">Nonebot-Plugin-L4d2-Server 控制台</h1>
<div align="center">
    <a href="https://github.com/Agnes4m/nonebot_plugin_l4d2_server/" target="_blank">
    Github仓库</a>
</div>
<br>
<br>
"""
)
login_api = AmisAPI(
    url="/l4d2/api/login",
    method="post",
    adaptor="""
        if (payload.status == 0) {
            localStorage.setItem("token", payload.data.token);
        }
        return payload;
    """,
)

login_form = Form(
    api=login_api,
    title="",
    body=[
        InputText(
            name="username",
            label="用户名",
            labelRemark=Remark(shape="circle", content="后台管理用户名，默认为l4d2"),
        ),
        InputPassword(
            name="password",
            label="密码",
            labelRemark=Remark(shape="circle", content="后台管理密码，默认为admin"),
        ),
    ],
    mode=DisplayModeEnum.horizontal,
    horizontal=Horizontal(left=3, right=9, offset=5),
    redirect="/l4d2/admin",
)
body = Wrapper(className="w-2/5 mx-auto my-0 m:w-full", body=login_form)
login_page = Page(title="", body=[logo, body])

global_config_form = Form(
    title="全局配置",
    name="global_config",
    initApi="/l4d2/api/l4d2_global_config",
    api="post:/l4d2/api/l4d2_global_config",
    body=[
        Switch(
            label="控制总开关（摆设）",
            name="total_enable",
            value="${total_enable}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(shape="circle", content="关闭后，禁用网页控制台，请参考文档启动方法"),
        ),
        InputText(
            label="后台管理用户名",
            name="web_username",
            value="${web_username}",
            labelRemark=Remark(shape="circle", content="登录本后台管理所需要的用户名。"),
        ),
        InputPassword(
            label="后台管理密码",
            name="web_password",
            value="${web_password}",
            labelRemark=Remark(shape="circle", content="登录本后台管理所需要的密码。"),
        ),
        InputText(
            label="后台管理token密钥",
            name="web_secret_key",
            value="${web_secret_key}",
            labelRemark=Remark(shape="circle", content="用于本后台管理加密验证token的密钥。"),
        ),
        InputText(
            label="字体",
            name="l4_font",
            value="${l4_font}",
            labelRemark=Remark(shape="circle", content="机器人返回图片中文字的字体。"),
        ),
        Switch(
            label="是否图片发送单服务器查询",
            name="l4_image",
            value="${l4_image}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(shape="circle", content="开启时，会查询单服务器会使用图片，避免长信息风控"),
        ),
        Select(
            label="图片风格",
            name="l4_style",
            value="${l4_style}",
            source="${l4_styles}",
            labelRemark=Remark(shape="circle", content="仅仅是批量查询的风格"),
        ),
        Switch(
            label="是否优先上传地图",
            name="l4_only",
            value="${l4_only}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(shape="circle", content="开启时，上传地图会保证优先级，从而阻碍其他指令"),
        ),
        Switch(
            label="是否显示connect",
            name="l4_connect",
            value="${l4_connect}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(shape="circle", content="关闭后，查询服务器将不再显示connect和ip地址"),
        ),
        InputNumber(
            label="定时推送间隔（min）",
            name="l4_push_interval",
            value="${l4_push_interval}",
            labelRemark=Remark(shape="circle", content="设置好后，使用推送服务器定时指令，将以x分钟为间隔推送一次"),
        ),
        InputNumber(
            label="定时推次数",
            name="l4_push_times",
            value="${l4_push_times}",
            labelRemark=Remark(shape="circle", content="设置好后，将按照推送间隔时间推送x此"),
        ),
        InputNumber(
            label="当前路径序号",
            name="l4_number",
            value="${l4_number}",
            labelRemark=Remark(shape="circle", content="如果选定了路径，则上传地图优先传这个路径"),
        ),
        InputTag(
            label="求生上传地图用户",
            name="l4_master",
            value="${l4_master}",
            enableBatchAdd=True,
            placeholder="添加qq号",
            visibleOn="${total_enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="在这里加入的用户，才能上传地图"),
        ),
        InputTag(
            label="坐牢三指令tag",
            name="l4_zl_tag",
            value="${l4_zl_tag}",
            enableBatchAdd=True,
            placeholder="添加qq号",
            visibleOn="${total_enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="在这里的指令，可以响应坐牢三指令"),
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)

upload_map_form = Form(
    title="全局配置",
    name="global_config",
    api="post:/l4d2/api/l4d2_map_config",
    body=[
        InputText(
            label="服务器host",
            name="web_username",
            value="${web_username}",
            labelRemark=Remark(shape="circle", content="127.0.0.1"),
        ),
        InputPassword(
            label="服务器",
            name="web_password",
            value="${web_password}",
            labelRemark=Remark(shape="circle", content="登录本后台管理所需要的密码。"),
        ),
        InputText(
            label="后台管理token密钥",
            name="web_secret_key",
            value="${web_secret_key}",
            labelRemark=Remark(shape="circle", content="用于本后台管理加密验证token的密钥。"),
        ),
        InputText(
            label="查询key",
            name="l4_key",
            value="${l4_key}",
            labelRemark=Remark(shape="circle", content="用于获取拓展功能的key。"),
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)


group_select = Select(
    label="分群配置（暂未完成）", name="group_id", source="${group_list}", placeholder="选择群"
)
group_config_form = Form(
    title="分群配置（暂未完成）",
    visibleOn="group_id != null",
    initApi="/l4d2/api/l4d2_group_config?group_id=${group_id}",
    api="post:/l4d2/api/l4d2_group_config?group_id=${group_id}",
    body=[
        Switch(
            label="分群开关",
            name="enable",
            value="${enable}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(shape="circle", content="针对该群的群聊学习开关，关闭后，仅该群不会学习和回复。"),
        ),
        InputNumber(
            label="占位符",
            name="answer_threshold",
            value="${answer_threshold}",
            visibleOn="${enable}",
            min=2,
            labelRemark=Remark(shape="circle", content="单文本"),
        ),
        InputTag(
            label="占位符",
            name="ban_words",
            value="${ban_words}",
            enableBatchAdd=True,
            placeholder="占位符，词条",
            visibleOn="${enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="占位符词条"),
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        ActionType.Ajax(
            label="保存至所有群",
            level=LevelEnum.primary,
            confirmText="确认将当前配置保存至所有群？",
            api="post:/l4d2/api/l4d2_group_config?group_id=all",
        ),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)

server_control = Select(
    label="服务器设置", name="id_rank", source="${server_list}", placeholder="选择服务器"
)

server_ditail = Form(
    title="",
    api="post:/l4d2/api/l4d2_server_config?id_rank=${id_rank}",
    initApi="/l4d2/api/l4d2_server_config?id_rank=${id_rank}",
    visibleOn="id_rank != null",
    body=[
        Switch(
            label="是否是远程服务器",
            name="place",
            value="${place}",
            onText="是的",
            offText="不是",
            labelRemark=Remark(shape="circle", content="开启则确认为远程服务器"),
        ),
        InputText(
            label="服务器名称",
            name="server_id",
            value="${server_id}",
            labelRemark=Remark(shape="circle", content="服务器名字"),
        ),
        InputText(
            label="服务器ip地址",
            name="host",
            value="${host}",
            labelRemark=Remark(shape="circle", content="服务端所在ip地址,也可以是域名"),
        ),
        InputText(
            label="所在端口",
            name="port",
            value="${port}",
            labelRemark=Remark(shape="circle", content="服务端所在端口"),
        ),
        InputPassword(
            label="rcon控制台密码",
            name="rcon",
            value="${rcon}",
            labelRemark=Remark(shape="circle", content="服务端rcon密码"),
        ),
        InputText(
            label="服务器本地文件位置",
            name="location",
            value="${location}",
            labelRemark=Remark(shape="circle", content="求生服务器所在路径,该路径下有文件srcds_run"),
        ),
        InputText(
            label="远程账户",
            name="account",
            value="${account}",
            visibleOn="${place}",
            labelRemark=Remark(shape="circle", content="远程服务器的登录账户名"),
        ),
        InputPassword(
            label="远程密码",
            name="password",
            value="${password}",
            visibleOn="${place}",
            labelRemark=Remark(shape="circle", content="远程服务器的登录密码"),
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)

query_table = TableCRUD(
    mode="table",
    title="",
    syncLocation=False,
    api="/l4d2/api/get_query_contexts",
    interval=60000,
    itemActions=[
        ActionType.Url(
            tooltip="加入游戏",
            icon="fa fa-gamepad",
            confirmText="加入steam://connect/" + "${ip}",
            url="steam://connect/" + "${ip}",
            # url= "http://"+'${ip}',
            blank=True,
        ),
    ],
    columns=[
        TableColumn(label="服主", name="tag", searchable=True),
        TableColumn(label="序号", name="number", searchable=True),
        TableColumn(label="名称", name="name", searchable=True),
        TableColumn(label="地图", name="map_", searchable=True),
        TableColumn(label="玩家", name="rank_players", searchable=True),
        TableColumn(label="延迟", name="ping", searchable=True),
        TableColumn(label="IP 地址", name="ip", searchable=True),
    ],
)

server_page = PageSchema(
    url="/messages",
    icon="fa fa-comment",
    label="本地服务器管理",
    schema=Page(
        title="本地服务器管理",
        interval=120000,
        initApi="/l4d2/api/get_l4d2_messages",
        body=[
            Alert(
                level=LevelEnum.info,
                className="white-space-pre-wrap",
                body=(f"此数据库记录了{NICKNAME}所在服务器下的求生服务器。\n" f"· 功能暂未完善"),
            ),
            server_control,
            server_ditail,
        ],
    ),
)
query_page = PageSchema(
    url="/contexts",
    icon="fa fa-comments",
    label="远程服务器查询",
    schema=Page(
        title="远程服务器查询",
        body=[
            Alert(
                level=LevelEnum.info,
                className="white-space-pre-wrap",
                body=(
                    f"此数据库记录了{NICKNAME}所记录可查询的服务器ip。\n"
                    # '· 点击"回复列表"可以查看该条内容已学习到的可能的回复。\n'
                    # '· 点击"禁用"可以将该学习进行禁用，以后不会再学。\n'
                    f"· 功能暂未完善"
                ),
            ),
            query_table,
        ],
    ),
)

database_page = PageSchema(
    label="数据库", icon="fa fa-database", children=[server_page, query_page]
)  # type: ignore

config_page = PageSchema(
    url="/configs",
    isDefaultPage=True,
    icon="fa fa-wrench",
    label="配置",
    schema=Page(
        title="配置",
        initApi="/l4d2/api/get_group_list",
        body=[global_config_form, group_select, group_config_form],
    ),
)
l4d2_page = PageSchema(
    label="求生之路", icon="fa fa-wechat (alias)", children=[config_page, database_page]
)  # type: ignore

github_logo = Tpl(
    className="w-full",
    tpl='<div class="flex justify-between"><div></div><div><a href="https://github.com/Agnes4m/nonebot_plugin_l4d2_server" target="_blank" title="Copyright"><i class="fa fa-github fa-2x"></i></a></div></div>',
)
header = Flex(
    className="w-full", justify="flex-end", alignItems="flex-end", items=[github_logo]
)

admin_app = App(
    brandName="L4d2-Server",
    logo="https://ghproxy.com/https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_l4d2_server/main/image/logo.png",
    header=header,
    pages=[{"children": [config_page, database_page]}],
    footer='<div class="p-2 text-center bg-blue-100">Copyright © 2022 - 2023 <a href="https://github.com/Agnes4m/nonebot_plugin_l4d2_server" target="_blank" class="link-secondary">AGNES_DIGIAL</a> X<a target="_blank" href="https://github.com/baidu/amis" class="link-secondary" rel="noopener"> amis v2.2.0</a></div>',
)
