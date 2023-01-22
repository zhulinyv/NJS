from pathlib import Path
from os import path
import peewee as pw

db_path = Path().absolute() / "data" / "who@me" / "data.db"
db_path.parent.mkdir(exist_ok=True, parents=True)
db = pw.SqliteDatabase(db_path)


class MainTable(pw.Model):
    operator_id = pw.IntegerField()
    operator_name = pw.CharField()
    target_id = pw.IntegerField()
    group_id = pw.IntegerField()
    time = pw.CharField()
    message = pw.TextField()
    message_id = pw.IntegerField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey(
            "operator_id",
            "operator_name",
            "target_id",
            "group_id",
            "time",
            "message",
            "message_id",
        )


if not path.exists(db_path):
    db.connect()
    db.create_tables([MainTable])
    db.close()
