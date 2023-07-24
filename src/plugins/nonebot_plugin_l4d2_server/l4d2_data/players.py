import sqlite3
from typing import List, Optional, Tuple, Union

from ..l4d2_utils.config import DATASQLITE


class L4D2Player:
    """数据库L4D2_Player表的操作"""

    def __init__(self):
        """连接数据库"""
        self.datasqlite_path = DATASQLITE
        self.conn = sqlite3.connect(self.datasqlite_path / "L4D2.db")
        self.c = self.conn.cursor()

    async def _add_player_nickname(self, qq, nickname):
        """绑定昵称"""
        # try:
        self.c.execute(
            "INSERT INTO L4d2_players (qq, nickname, steamid) VALUES (?,?,NULL)",
            (qq, nickname),
        )
        self.conn.commit()
        #     return True
        # except sqlite3.IntegrityError:
        #     return False

    async def _add_player_steamid(self, qq, steamid):
        """绑定steamid"""
        self.c.execute(
            "INSERT INTO L4d2_players (qq, nickname, steamid) VALUES (?,NULL,?)",
            (qq, steamid),
        )
        self.conn.commit()

    async def _add_player_all(self, qq, nickname, steamid):
        """用新数据覆盖旧数据"""
        # try:
        self.c.execute(
            "INSERT OR REPLACE INTO L4d2_players (qq, nickname, steamid) VALUES (?,?,?)",
            (qq, nickname, steamid),
        )
        self.conn.commit()
        return True
        # except sqlite3.IntegrityError:
        #     return False

    def _delete_player(self, qq):
        """解除绑定"""
        self.c.execute(f"DELETE FROM L4d2_players WHERE qq = {qq}")
        self.conn.commit()
        return True

    def _query_player_qq(self, qq) -> Union[tuple, None]:
        """通过qq获取数据"""
        self.c.execute(f"SELECT * FROM L4d2_players WHERE qq = '{qq}'")
        return self.c.fetchone()

    async def _query_player_nickname(self, nickname: str) -> Union[tuple, None]:
        """通过nickname获取数据"""
        self.c.execute(f"SELECT * FROM L4d2_players WHERE nickname = '{nickname}'")
        return self.c.fetchone()

    async def _query_player_steamid(self, steamid: str):
        """通过steamid获取数据"""
        self.c.execute(f"SELECT * FROM L4d2_players WHERE steamid = '{steamid}'")
        data_tuple = self.c.fetchone()
        return data_tuple

    async def search_data(
        self, qq: Optional[str], nickname: Optional[str], steamid: Optional[str]
    ) -> Union[tuple, None]:
        """
        输入元组查询，优先qq其次steamid最后nickname，不需要值可以为None
        输出为元组，如果为空输出None
        data = (qq , nickname , steamid )
        """
        if qq:
            self.c.execute("SELECT * FROM L4d2_players WHERE qq=?", (qq,))
            result = self.c.fetchone()
            if result:
                return result
        if steamid:
            self.c.execute("SELECT * FROM L4d2_players WHERE steamid=?", (steamid,))
            result = self.c.fetchone()
            if result:
                return result
        if nickname:
            self.c.execute("SELECT * FROM L4d2_players WHERE nickname=?", (nickname,))
            result = self.c.fetchone()
            if result:
                return result
        return None

    def _query_all_player(self) -> List[Tuple]:
        """获取所有玩家信息"""
        self.c.execute("SELECT * FROM L4d2_players")
        return self.c.fetchall()
