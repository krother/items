from typing import Optional

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    summary: Optional[str] = None
    owner: Optional[str] = None
    state: str = "todo"

    def __eq__(self, other):
        return (
            self.summary == other.summary and
            self.owner == other.owner and
            self.state == other.state
        )