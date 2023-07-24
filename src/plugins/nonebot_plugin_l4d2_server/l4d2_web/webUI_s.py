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
from .webUI import header

query_table = TableCRUD(
    mode="table",
    title="",
    syncLocation=False,
    api="/l4d2/api/user/get_query_contexts",
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
        TableColumn(label="服主", name="tag", searchable=True, sortable=True),
        TableColumn(label="序号", name="number", sortable=True, searchable=True),
        TableColumn(label="名称", name="name", sortable=True, searchable=True),
        TableColumn(label="地图", name="map_", sortable=True, searchable=True),
        TableColumn(label="玩家", name="rank_players", sortable=True, searchable=True),
        TableColumn(label="延迟", name="ping", sortable=True, searchable=True),
        TableColumn(label="IP 地址", name="ip", sortable=True, searchable=True),
    ],
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
    label="数据库",
    icon="fa fa-database",
    url="/contexts",
    isDefaultPage=True,
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

user_app = App(
    brandName="L4d2-Server",
    logo="https://ghproxy.com/https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_l4d2_server/main/image/logo.png",
    header=header,
    pages=[{"children": [database_page]}],
    footer='<div class="p-2 text-center bg-blue-100">Copyright © 2022 - 2023 <a href="https://github.com/Agnes4m/nonebot_plugin_l4d2_server" target="_blank" class="link-secondary">AGNES_DIGIAL</a> X<a target="_blank" href="https://github.com/baidu/amis" class="link-secondary" rel="noopener"> amis v2.2.0</a></div>',
)
