"""
Test Cases:
* `delete` one from a database with more than one
* `delete` the last item
* `delete` a non-existent item
"""
import pytest

from items import InvalidItemId, Item


@pytest.fixture()
def three_items(items_db):
    item1 = items_db.add_item(Item(summary="Update pytest section"))
    item2 = items_db.add_item(Item(summary="Update cibuildwheel section"))
    item3 = items_db.add_item(Item(summary="Update mock tests"))
    return (item1, item2, item3)


def test_delete_from_many(items_db, three_items):
    """
    Count should go from 3 to 2
    And item shouldn't be retrievable.
    But the rest should be.
    """
    (item1, item2, item3) = three_items
    id_to_delete = item2
    ids_still_there = (item1, item3)

    items_db.delete_item(id_to_delete)

    assert items_db.count() == 2
    # item should not be retrievable after deletion
    with pytest.raises(InvalidItemId):
        items_db.get_item(id_to_delete)
    # non-deleted items should still be retrievable
    for i in ids_still_there:
        # just making sure this doesn't throw an exception
        items_db.get_item(i)


def test_delete_last_item(items_db):
    """
    Count should be back to 0
    And item shouldn't be retrievable.
    """
    i = items_db.add_item(Item(summary="Update pytest section"))
    items_db.delete_item(i)
    assert items_db.count() == 0
    with pytest.raises(InvalidItemId):
        items_db.get_item(i)


def test_delete_non_existent(items_db):
    """
    Shouldn’t be able to start a non-existent item.
    """
    i = 42  # any number will do, db is empty
    with pytest.raises(InvalidItemId):
        items_db.delete_item(i)
