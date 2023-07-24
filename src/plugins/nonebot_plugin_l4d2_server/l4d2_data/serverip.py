import sqlite3

from ..l4d2_utils.config import DATASQLITE


class L4D2Server:
    """数据库L4D2_server表的操作"""

    def __init__(self):
        """连接数据库"""
        self.datasqlite_path = DATASQLITE
        self.conn = sqlite3.connect(self.datasqlite_path / "L4D2.db")
        self.c = self.conn.cursor()

    async def bind_server_ip(self, qqgroup, host, port):
        """绑定群订阅ip"""
        self.c.execute(
            "INSERT OR REPLACE INTO L4D2_server (qqgroup, host, port) VALUES (?,?,?)",
            (qqgroup, host, port),
        )
        self.conn.commit()

    async def query_server_ip(self, qqgroup):
        """输入群号，返回数据库里订阅ip元组列表"""
        self.c.execute(
            f"SELECT  number, qqgroup ,host ,port FROM L4D2_server WHERE qqgroup = {qqgroup}"
        )
        msg_list = self.c.fetchall()
        return msg_list

    async def del_server_ip(self, id: int):
        """删除指定id的ip"""
        self.c.execute(f"DELETE FROM L4D2_server WHERE number = {id}")
        self.conn.commit()

    async def query_number(self, number: int):
        """通过序号找服务器"""
        self.c.execute(
            f"SELECT qqgroup , host ,port FROM L4D2_server WHERE number = {number}"
        )
        msg_list = self.c.fetchone()
        return msg_list
