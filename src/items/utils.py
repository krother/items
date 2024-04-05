import os
import pathlib
from contextlib import contextmanager

import items


def get_path():
    db_path_env = os.getenv("ITEMS_DB_DIR", "")
    if db_path_env:
        db_path = pathlib.Path(db_path_env)
    else:
        db_path = pathlib.Path.home() / "items_db"
    return db_path


@contextmanager
def items_db():
    db_path = get_path()
    db = items.ItemsDB(db_path)
    yield db
    db.close()
