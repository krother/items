
import pytest


@pytest.fixture(autouse=True)
def set_db_env_var(db_path, monkeypatch, items_db):
    monkeypatch.setenv("ITEMS_DB_DIR", db_path.as_posix())
