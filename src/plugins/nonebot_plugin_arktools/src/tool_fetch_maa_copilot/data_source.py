import json
import random
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import httpx
from nonebot import logger
from nonebot_plugin_imageutils import text2image

from ..core.database.plugin_sqlite import MAACopilotSubsModel
from ..exceptions import MAAFailedResponseException, MAANoResultException
from ..utils import stage_swap, handbook_stage_swap

ORDERS = {
    "热度": "hot",
    "最新": "id",
    "访问": "views"
}

DEFAULT_PARAMS = {
    "desc": True,
    "limit": 50,
    "page": 1,
    "order_by": ORDERS["最新"],
    "document": "",         # 标题、描述、神秘代码
    "level_keyword": "",    # 关卡名、类型、编号
    "operator": ""          # 包含、排除干员
}

POSSIBLE_KEYS = {
    "document",
    "level_keyword",
    "operator"
}


async def fetch_works(params: dict) -> List[Dict]:
    """根据参数获取结果"""
    url = "https://prts.maa.plus/copilot/query"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    logger.info(response.url)
    data = response.json()
    if data["status_code"] != 200:
        """响应错误"""
        raise MAAFailedResponseException(details=data["status_code"])

    if not data["data"] or not data["data"]["total"] or not data["data"]["data"]:
        """没有作业"""
        raise MAANoResultException(details=params["document"])

    return data["data"]["data"]


async def process_works(works: List[Dict], keyword: str) -> Optional[Tuple[BytesIO, int, str]]:
    """判断最新、加进数据库，返回图片内容 + 关卡id"""
    work = works[0]
    local_data = await MAACopilotSubsModel.filter(sub_keyword=keyword).first()
    local_upload_time = local_data.latest_upload_time
    latest_upload_time = datetime.fromisoformat(work["upload_time"]).timestamp()

    if latest_upload_time <= local_upload_time:
        return None

    content = json.loads(work["content"])
    operators = content["opers"]

    title, details, stage, operators_str = await process_copilot_data(work)
    await MAACopilotSubsModel.filter(sub_keyword=keyword).update(
        sub_groups=local_data.sub_groups,
        sub_keyword=local_data.sub_keyword,
        latest_upload_time=latest_upload_time,
        latest_id=work["id"],
        operators=operators,
        stage=stage,
        title=title,
        details=details
    )

    img_bytes = await build_result_image(title, details, stage, operators_str)
    return img_bytes, work["id"], local_data.sub_groups


async def process_copilot_data(data: Dict) -> Tuple[str, str, str, str]:
    content = json.loads(data["content"])
    stage = content["stage_name"]
    stage = await stage_swap(stage, "code2name")
    stage = await handbook_stage_swap(stage, "code2name")

    title = content["doc"]["title"]
    details = content["doc"]["details"]
    operators = content["opers"]
    operators = [
        f"{o['name']}({o['skill']})"
        for o in operators
    ]
    operators_str = "   ".join(operators)
    return title, details, stage, operators_str


async def build_result_image(title: str, details: str, stage: str, operators_str: str) -> BytesIO:
    text = (
        f"[size=32][b][color=white]{title}[/color][/b][/size]\n"
        f"[size=16][color=white]作业简介: {details}[/color][/size]\n\n"
        f"[size=24][b][color=white]关卡名: {stage}[/color][/b][/size]\n\n"
        f"[size=16][b][color=white]阵容: {operators_str}[/color][/b][/size]"
    )
    img = text2image(
        padding=(20, 20, 20, 20),
        bg_color="black",
        text=text,
        max_width=560
    )
    img_bytes = BytesIO()
    img.save(img_bytes, format="png")
    return img_bytes


async def add_maa_sub(group_id: str, keywords: str) -> str:
    result = await MAACopilotSubsModel.filter(sub_keyword=keywords).first()
    if not result:
        await MAACopilotSubsModel.create(sub_groups=group_id, sub_keyword=keywords)
        return f"{group_id}-{keywords} 已添加订阅！"

    if group_id in result.sub_groups:
        return f"{group_id}-{keywords} 已经添加过了！"

    await MAACopilotSubsModel.filter(sub_keyword=keywords).update(sub_groups=f"{result.sub_groups} {group_id}")
    return f"{group_id}-{keywords} 已添加订阅！"


async def del_maa_sub(group_id: str, keywords: str) -> str:
    result = await MAACopilotSubsModel.filter(sub_keyword=keywords).first()
    if not result or group_id not in result.sub_groups:
        return f"{group_id}-{keywords} 没有订阅过哦！"

    if group_id == result.sub_groups:  # 只有这一个群
        await result.delete()
        return f"{group_id}-{keywords} 已删除订阅！"

    groups = [_ for _ in result.sub_groups.split() if _ != group_id]
    await MAACopilotSubsModel.filter(sub_keyword=keywords).update(sub_groups=" ".join(groups))
    return f"{group_id}-{keywords} 已删除订阅！"


async def que_maa_sub(group_id: str) -> str:
    result = await MAACopilotSubsModel.filter(sub_groups__contains=group_id).all()
    if not result:
        return f"{group_id} 尚未订阅过任何关键词哦！"

    answer = f"{group_id} 订阅过的关键词有: "
    for model in result:
        answer += f'\n{model.sub_keyword.replace("+", ", ")}'

    return answer


class SubManager:
    def __init__(self):
        self.data: List["MAACopilotSubsModel"] = []

    async def reload_sub_data(self):
        """重载数据"""
        if not self.data:
            self.data = await MAACopilotSubsModel.all()

    async def random_sub_data(self):
        """随机获取一条数据"""
        if not self.data:
            return None
        sub = random.choice(self.data)
        self.data.remove(sub)
        if sub:
            return sub.sub_keyword
        await self.reload_sub_data()
        return await self.random_sub_data()
