from __future__ import annotations

import json
from pathlib import Path
from typing import  Dict, Optional, Any  # noqa: F401

from pydantic import BaseModel

from .web_config import common_config
from ..chatbots import chatbots
from ..utils import md_to_pic

Root = Path() / "data" / "SparkGPT"


class User(BaseModel):
    user_id: str
    image: Optional[bytes]
    bots_hash: Optional[int]
    bots: Dict[str, Any] = {}

    @property
    def store_path(self):
        return Root / "users" / f"{self.user_id}.json"

    def __init__(self, user_id: str, *args, **kwargs):
        super().__init__(user_id=user_id, *args, **kwargs)
        store_path = self.store_path
        if not store_path.exists():
            store_path.parent.mkdir(parents=True, exist_ok=True)
            self.save()
        else:
            with open(self.store_path, "r") as f:
                data = json.load(f)
            super().__init__(**data)
            for name, bot in self.bots.items():
                class_ = chatbots.get_model_class(bot["model"])
                self.bots[name] = class_(**bot)

    def save(self):
        self.bots = {
            key: value
            for key, value in sorted(self.bots.items(), key=lambda x: -len(x[0]))
        }
        copy = self.copy()
        copy.image = None
        copy.bots_hash = None
        data = copy.dict()
        with self.store_path.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    async def get_bots_img(self):
        bots_hash = hash(str(self.bots) + str(public_user.bots))
        if bots_hash == self.bots_hash and self.image:
            return self.image
        else:
            private_bots = list(self.bots.values())
            if private_bots:
                md = f"私有会话\n使用' {common_config().private_command}名称 <问题> '即可使用相应会话进行对话  \n\n| 名称 | 模型 | 预设 | 指令 |  \n| -- | -- | -- | -- |  \n"
                for bot in private_bots:
                    md += f"| {bot.name} | {bot.model} | {bot.prompt_name} | {bot.command_name} |  \n"
            else:
                md = "私有会话:  \n\n你没有创建过私有会话"

            md += "  \n"
            public_bots = list(public_user.bots.values())
            if public_bots:
                md += f"公有会话\n使用' {common_config().public_command}名称 <问题> '即可使用相应会话进行对话  \n\n| 名称 | 模型 | 预设 | 指令 |  \n| -- | -- | -- | -- |  \n"
                for bot in public_bots:
                    md += f"| {bot.name} | {bot.model} | {bot.prompt_name} | {bot.command_name} |  \n"
            else:
                md += "公有会话:  \n\nSparkGPT管理员没有创建过公有会话"

            md += "  \n"

            img = await md_to_pic(md, width=400)
            self.image = img
            self.bots_hash = bots_hash
            return img


class Users:
    users: dict = {}

    def __getitem__(self, user_id: int | str) -> User:
        user_id = str(user_id)
        if user_id not in self.users:
            self.load_user(user_id)
        return self.users.get(user_id)

    def load_user(self, user_id: str):
        try:
            self.users[user_id] = User(user_id=user_id)
        except Exception as e:
            raise Exception("Failed to load user") from e


users = Users()
public_user = users["public_user"]
