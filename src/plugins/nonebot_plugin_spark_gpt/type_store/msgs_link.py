from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class MsgLinks(BaseModel):
    links: Dict[str, Dict[str | int, Any]] = {}

    def get_chatbot(self, user_id: str, msg_id: str | int):
        msg_id = str(msg_id)
        if user_id not in self.links:
            raise Exception("MsgLink Not Found")
        if msg_id in self.links[user_id]:
            self.clean(user_id)
            return self.links[user_id][msg_id]
        else:
            raise Exception("MsgLink Not Found")

    def add_msglink(self, user_id: str, msg_id: str | int, chatbot: Any):
        if user_id not in self.links.keys():
            self.links[user_id] = {}
        self.clean(user_id)
        self.links[user_id][str(msg_id)] = chatbot

    def clean(self, user_id: str):
        if len(self.links[user_id]) > 1000:
            self.links[user_id] = {}


msg_links = MsgLinks()
