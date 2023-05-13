import os
import sqlite3
from collections import Counter


class CardRecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS card_record"
                "(gid INT NOT NULL, uid INT NOT NULL, cid INT NOT NULL, num INT NOT NULL, PRIMARY KEY(gid, uid, cid))"
            )

    def add_card_num(self, gid, uid, cid):
        num = 1
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO card_record (gid, uid, cid, num) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        return num

    def get_cards_num(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT cid, num FROM card_record WHERE gid=? AND uid=? AND num>0", (gid, uid)
            ).fetchall()
        return [c[0] for c in r] if r else []

    def get_group_ranking(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT uid FROM card_record WHERE gid=? AND num>0", (gid,)
            ).fetchall()
        if not r:
            return -1
        cards_num = Counter([s[0] for s in r])
        if uid not in cards_num:
            return -1
        user_card_num = cards_num[uid]
        return sum(n > user_card_num for n in cards_num.values()) + 1


DB_PATH = os.path.expanduser("~/.hoshino/pcr_stamp.db")
db = CardRecordDAO(DB_PATH)
