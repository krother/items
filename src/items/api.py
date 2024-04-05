"""
API for the items project
"""
import os

from .model import Item
from .sqldb import SQLDB


__all__ = [
    "Item",
    "ItemsDB",
    "ItemsException",
    "MissingSummary",
    "InvalidItemId",
]


class ItemsException(Exception):
    pass


class MissingSummary(ItemsException):
    pass


class InvalidItemId(ItemsException):
    pass


class ItemsDB:
    def __init__(self, db_path):
        self._db_path = db_path
        self._db = SQLDB(os.path.join(db_path, ".items_db"))

    def add_item(self, item: Item):
        """Add an item, return the id of the item."""
        if not item.summary:
            raise MissingSummary
        if item.owner is None:
            item.owner = ""
        item = Item(summary=item.summary,
                    owner=item.owner,
                    state=item.state)  # enable adding same item twice
        item_id = self._db.create(item)
        return item_id

    def get_item(self, item_id: int):
        """Return an item with a corresponding id."""
        item = self._db.read(item_id)
        if item is not None:
            return item
        else:
            raise InvalidItemId(item_id)

    def list_items(self, owner=None, state=None):
        """Return a list of items."""
        all_items = self._db.read_all()
        if (owner is not None) and (state is not None):
            return [
                item
                for item in all_items
                if (item.owner == owner and item.state == state)
            ]
        elif owner is not None:
            return [item for item in all_items if item.owner == owner]
        elif state is not None:
            return [item for item in all_items if item.state == state]
        else:
            return [item for item in all_items]

    def count(self):
        """Return the number of items in the db."""
        return self._db.count()

    def update_item(self, item_id: int, item_mods: Item):
        """Update an item with modifications."""
        mods = {
            k:v
            for k, v in item_mods.model_dump().items()
            if v is not None
            }
        rowcount = self._db.update(item_id, mods)
        if rowcount == 0:
            raise InvalidItemId(item_id)

    def start(self, item_id: int):
        """Set an item state to in progress."""
        self.update_item(item_id, Item(state="in progress"))

    def finish(self, item_id: int):
        """Set an item state to done."""
        self.update_item(item_id, Item(state="done"))

    def delete_item(self, item_id: int):
        """Remove an item from db with a given item id."""
        rowcount = self._db.delete(item_id)
        if rowcount == 0:
            raise InvalidItemId(item_id)

    def delete_all(self):
        """Remove all items from the db."""
        self._db.delete_all()

    def close(self):
        pass

    def path(self):
        return self._db_path
