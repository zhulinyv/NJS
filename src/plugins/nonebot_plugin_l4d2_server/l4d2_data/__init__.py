import sqlite3

from nonebot.log import logger

from ..l4d2_utils.config import (
    DATASQLITE,
    L4d2_BOOLEAN,
    L4d2_INTEGER,
    L4d2_players_tag,
    L4d2_server_tag,
    L4d2_TEXT,
    table_data,
    tables_columns,
)


class L4D2DataSqlite:
    """连接数据库和断开数据库，以及一些检查函数"""

    def __init__(self):
        """连接数据库"""
        self.datasqlite_path = DATASQLITE
        self.datasqlite_path.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.datasqlite_path / "L4D2.db")
        self._check_tables_exist()
        self._check_data_existence()
        self._check_data_validity()
        logger.info("已连接求生数据库")

    def _base_conn(self):
        return self.conn

    def _check_tables_exist(self) -> None:
        """
        检查表是否存在
        """
        c = self.conn.cursor()
        for table in table_data:
            c.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            if c.fetchone() is None:
                if table == "L4d2_players":
                    c.execute(f"CREATE TABLE {table} (qq INTEGER PRIMARY KEY)")
                elif table == "L4D2_server":
                    c.execute(f"CREATE TABLE {table} (number INTEGER PRIMARY KEY)")
                self.conn.commit()

    def _check_data_existence(self) -> None:
        """
        检查表头是否存在，如果不存在则新建并填充默认值
        """
        c = self.conn.cursor()
        for table, tag in tables_columns.items():
            for column in tag:
                c.execute(f"PRAGMA table_info({table})")
                if not any(col[1] == column for col in c.fetchall()):
                    if column in L4d2_BOOLEAN:
                        c.execute(
                            f"ALTER TABLE {table} ADD COLUMN {column} BOOLEAN DEFAULT 0"
                        )
                    elif column in L4d2_INTEGER:
                        c.execute(
                            f"ALTER TABLE {table} ADD COLUMN {column} INTEGER DEFAULT NULL"
                        )
                    else:
                        c.execute(
                            f"ALTER TABLE {table} ADD COLUMN {column} TEXT DEFAULT NULL"
                        )
        self.conn.commit()

    def _check_data_validity(self) -> None:
        """
        检查数据库数据的合法性
        错误数据默认填充NULL或者False
        """
        c = self.conn.cursor()
        columns = None
        table = None
        for table in table_data:
            if table == "L4d2_players":
                columns = L4d2_players_tag
            else:
                columns = L4d2_server_tag
        if not columns:
            return
        for column in columns:
            if column in L4d2_INTEGER:
                c.execute(
                    f"UPDATE {table} SET {column} = NULL WHERE typeof({column}) != 'integer'"
                )
            elif column in L4d2_TEXT:
                c.execute(
                    f"UPDATE {table} SET {column} = NULL WHERE typeof({column}) != 'text'"
                )
            elif column in L4d2_BOOLEAN:
                c.execute(
                    f"UPDATE {table} SET {column} = 'False' WHERE typeof({column}) != 'boolean'"
                )
        self.conn.commit()

    def _close(self):
        """断开连接到数据库"""
        self.conn.close()
        logger.info("已断开求生数据库")


sq_L4D2 = L4D2DataSqlite()
