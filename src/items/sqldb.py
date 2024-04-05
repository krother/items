"""
DB for the items project
"""
from sqlmodel import Session, create_engine, select, update, delete

from .model import Item


class SQLDB:
    def __init__(self, db_file_prefix: str):
        self._db = create_engine(f"sqlite:///{db_file_prefix}.db")
        Item.metadata.create_all(self._db)

    def create(self, item: Item) -> int:
        with Session(self._db) as session:
            session.add(item)
            session.commit()
            return item.id

    def read(self, id: int):
        with Session(self._db) as session:
            statement = select(Item).where(Item.id == id)
            item = session.exec(statement).first()
            return item

    def read_all(self):
        with Session(self._db) as session:
            statement = select(Item)
            return session.exec(statement).fetchall()

    def update(self, id: int, mods) -> None:
        with Session(self._db) as session:
            statement = update(Item).where(Item.id==id).values(**mods)
            up = session.exec(statement)
            session.commit()
            return up.rowcount

    def delete(self, id: int) -> None:
        with Session(self._db) as session:
            statement = delete(Item).where(Item.id==id)
            crs = session.exec(statement)
            session.commit()
            return crs.rowcount

    def delete_all(self) -> None:
        with Session(self._db) as session:
            statement = delete(Item)
            crs = session.exec(statement)
            session.commit()
            return crs.rowcount

    def count(self) -> int:
        return len(self.read_all())

    def close(self):
        self._db.close()
