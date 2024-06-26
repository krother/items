import pytest
import items
from items import Item


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    """Path to temporary database"""
    test_path = tmp_path_factory.mktemp("items_db")
    return test_path


@pytest.fixture(scope="session")
def session_items_db(db_path):
    """ItemsDB"""
    db_ = items.ItemsDB(db_path)
    yield db_
    db_.close()


#@pytest.fixture(autouse=True)
#def mock_environment_vars(monkeypatch, db_path):
#    monkeypatch.setenv("ITEMS_DB_DIR", db_path) #.as_posix())


@pytest.fixture(scope="function")
def items_db(session_items_db, request, faker):
    db = session_items_db
    db.delete_all()
    # support for `@pytest.mark.num_items(<some number>)`
    faker.seed_instance(101) # random seed
    m = request.node.get_closest_marker('num_items')
    if m and len(m.args) > 0:
        num_items = m.args[0]
        for _ in range(num_items):
            db.add_item(Item(summary=faker.sentence(),
                             owner=faker.first_name()))
    return db
