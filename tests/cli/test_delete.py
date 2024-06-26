import items


def test_delete(items_db, items_cli):
    i = items_db.add_item(items.Item(summary="Update pytest section"))
    items_cli(f"delete {i}")
    assert items_db.count() == 0
