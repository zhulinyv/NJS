import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from nonebot import get_adapter, get_app, get_driver, logger
from nonebot.adapters.onebot.v11 import Adapter

from ..l4d2_queries.qqgroup import qq_ip_querie
from ..l4d2_utils.config import *
from ..l4d2_utils.utils import split_maohao

CONFIG_PATH = Path() / "data" / "L4D2" / "l4d2.yml"

CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

driver = get_driver()

from .webUI import admin_app, login_page
from .webUI_s import user_app

requestAdaptor = """
requestAdaptor(api) {
    api.headers["token"] = localStorage.getItem("token");
    return api;
},
"""
responseAdaptor = """
responseAdaptor(api, payload, query, request, response) {
    if (response.data.detail == '登录验证失败或已失效，请重新登录') {
        window.location.href = '/l4d2/login'
        window.localStorage.clear()
        window.sessionStorage.clear()
        window.alert('登录验证失败或已失效，请重新登录')
    }
    return payload
},
"""


def authentication():
    def inner(token: Optional[str] = Header(...)):
        try:
            if not token:
                raise HTTPException(status_code=400, detail="登录验证失败或已失效，请重新登录")
            payload = jwt.decode(
                token, config_manager.config.web_secret_key, algorithms="HS256"
            )
            if (
                not (username := payload.get("username"))
                or username != config_manager.config.web_username
            ):
                raise HTTPException(status_code=400, detail="登录验证失败或已失效，请重新登录")
        except (JWTError, ExpiredSignatureError, AttributeError):
            raise HTTPException(status_code=400, detail="登录验证失败或已失效，请重新登录")

    return Depends(inner)


COMMAND_START = driver.config.command_start.copy()
if "" in COMMAND_START:
    COMMAND_START.remove("")


@driver.on_startup
async def init_web():
    if not config_manager.config.total_enable:
        return
    app: FastAPI = get_app()
    logger.success("成功加载网页控制台")

    @app.post("/l4d2/api/login", response_class=JSONResponse)
    async def login(user: UserModel):
        if (
            user.username != config_manager.config.web_username
            or user.password != config_manager.config.web_password
        ):
            return {"status": -100, "msg": "登录失败，请确认用户ID和密码无误"}
        token = jwt.encode(
            {
                "username": user.username,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(minutes=30),
            },
            config_manager.config.web_secret_key,
            algorithm="HS256",
        )
        return {"status": 0, "msg": "登录成功", "data": {"token": token}}

    @app.get(
        "/l4d2/api/get_group_list",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def get_group_list_api():
        try:
            bots = get_adapter(Adapter).bots
            if len(bots) == 0:
                return {"status": -100, "msg": "获取群和好友列表失败，请确认已连接GOCQ"}
            bot = list(bots.values())[0]
            group_list = await bot.get_group_list()
            group_list = [
                {
                    "label": f'{group["group_name"]}({group["group_id"]})',
                    "value": group["group_id"],
                }
                for group in group_list
            ]
            return {"status": 0, "msg": "ok", "data": {"group_list": group_list}}
        except ValueError:
            return {"status": -100, "msg": "获取群和好友列表失败，请确认已连接GOCQ"}

    @app.post(
        "/l4d2/api/l4d2_global_config",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def post_l4d2_global_config(data: dict):
        config_manager.config.update(**data)
        config_manager.save()
        return {"status": 0, "msg": "保存成功"}

    @app.get(
        "/l4d2/api/l4d2_global_config",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def get_l4d2_global_config():
        try:
            bots = get_adapter(Adapter).bots
            if len(bots) == 0:
                return {"status": -100, "msg": "获取群和好友列表失败，请确认已连接GOCQ"}
            bot = list(bots.values())[0]
            groups = await bot.get_group_list()
            member_list = []
            for group in groups:
                members = await bot.get_group_member_list(group_id=group["group_id"])
                member_list.extend(
                    [
                        {
                            "label": f'{member["nickname"] or member["card"]}({member["user_id"]})',
                            "value": member["user_id"],
                        }
                        for member in members
                    ]
                )
            config = config_manager.config.dict(exclude={"group_config"})
            config["member_list"] = member_list
            config["l4_styles"] = ["standard", "black"]

            return config
        except ValueError:
            return {"status": -100, "msg": "获取群和好友列表失败，请确认已连接GOCQ"}

    @app.get("/l4d2/api/user/get_query_contexts", response_class=JSONResponse)
    @app.get(
        "/l4d2/api/get_query_contexts",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def get_query_context():
        try:
            from ..l4d2_utils.command import ALL_HOST

            this_ips = ALL_HOST
            ip_lists = []
            for ip_list, v in this_ips.items():
                for d in v:
                    host, port = split_maohao(d["ip"])
                    ip_lists.append((d["id"], ip_list, host, port))
            data_dict = await qq_ip_querie(ip_lists)
            if not data_dict:
                return {"status": -100, "msg": "返回失败，请确保有可用的服务器ip"}
            data_list = data_dict["msg_list"]
            # logger.info(data_list)
            return {
                "status": 0,
                "msg": "ok",
                "data": {
                    "items": data_list,
                    "total": len(data_list),
                },
            }
        except ValueError:
            return {"status": -100, "msg": "返回失败，请确保网络连接正常"}

    @app.get(
        "/l4d2/api/get_l4d2_messages",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def get_l4d2_messages():
        try:
            l4_ipall = config_manager.config.l4_ipall
            config = [
                {"label": item["server_id"], "value": item["id_rank"]}
                for item in l4_ipall
            ]
            return {"status": 0, "msg": "ok", "data": {"server_list": config}}
        except ValueError:
            return {"status": -100, "msg": "返回失败，请确保网络连接正常"}

    @app.get(
        "/l4d2/api/l4d2_server_config",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def get_l4d2_server_config(id_rank: str):
        try:
            l4_ipall = config_manager.config.l4_ipall
            config = {}
            for item in l4_ipall:
                if item["id_rank"] == id_rank:
                    item["place"] = item["place"] == "True" or item["place"] == True
                    config = item
                    break
            return {"status": 0, "msg": "ok", "data": config}
        except ValueError:
            return {"status": -100, "msg": "返回失败，请确保网络连接正常"}

    @app.post(
        "/l4d2/api/l4d2_server_config",
        response_class=JSONResponse,
        dependencies=[authentication()],
    )
    async def post_l4d2_server_config(id_rank: str, data: dict):
        for one in config_manager.config.l4_ipall:
            if one["id_rank"] == id_rank:
                one.update(**data)
        config_manager.save()
        return {"status": 0, "msg": "保存成功"}

    @app.get("/l4d2", response_class=RedirectResponse)
    async def redirect_page():
        return RedirectResponse("/l4d2/login")

    @app.get("/l4d2/login", response_class=HTMLResponse)
    async def login_page_app():
        return login_page.render(site_title="登录 | l4d2 后台管理", theme="ang")

    @app.get("/l4d2/admin", response_class=HTMLResponse)
    async def admin_page_app():
        return admin_app.render(
            site_title="l4d2-l4d2 后台管理",
            theme="ang",
            requestAdaptor=requestAdaptor,
            responseAdaptor=responseAdaptor,
        )

    @app.get("/l4d2/user", response_class=HTMLResponse)
    async def user_page_app():
        return user_app.render(
            site_title="l4d2服务器查询",
            theme="ang",
        )
