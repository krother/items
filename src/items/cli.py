"""Command Line Interface (CLI) for the items project."""
from io import StringIO
from typing import List

import rich
import typer
from rich.table import Table

import items
from items.utils import items_db


app = typer.Typer(add_completion=False)


@app.command()
def version():
    """Return the version of the items application."""
    print(items.__version__)


@app.command()
def add(summary: List[str], owner: str = typer.Option(None, "-o", "--owner")):
    """Add an item to the db."""
    summary = " ".join(summary) if summary else None
    with items_db() as db:
        db.add_item(items.Item(summary=summary, owner=owner, state="todo"))


@app.command()
def delete(item_id: int):
    """Remove an item in the db with a given id."""
    with items_db() as db:
        try:
            db.delete_item(item_id)
        except items.InvalidItemId:
            print(f"Error: Invalid item id {item_id}")


@app.command("list")
def list_items(
    owner: str = typer.Option(None, "-o", "--owner"),
    state: str = typer.Option(None, "-s", "--state"),
):
    """
    List the items in the db.
    """
    with items_db() as db:
        the_items = db.list_items(owner=owner, state=state)
        table = Table(box=rich.box.SIMPLE)
        table.add_column("ID")
        table.add_column("state")
        table.add_column("owner")
        table.add_column("summary")
        for t in the_items:
            owner = "" if t.owner is None else t.owner
            table.add_row(str(t.id), t.state, owner, t.summary)
        out = StringIO()
        rich.print(table, file=out)
        print(out.getvalue())


@app.command()
def update(
    item_id: int,
    owner: str = typer.Option(None, "-o", "--owner"),
    summary: List[str] = typer.Option(None, "-s", "--summary"),
):
    """Modify an item in the db with a given id with new info."""
    summary = " ".join(summary) if summary else None
    with items_db() as db:
        try:
            db.update_item(item_id, items.Item(summary=summary, owner=owner, state=None))
        except items.InvalidItemId:
            print(f"Error: Invalid item id {item_id}.")


@app.command()
def start(item_id: int):
    """Set an item state to in progress."""
    with items_db() as db:
        try:
            db.start(item_id)
        except items.InvalidItemId:
            print(f"Error: Invalid item id {item_id}.")


@app.command()
def finish(item_id: int):
    """Set an item state to done."""
    with items_db() as db:
        try:
            db.finish(item_id)
        except items.InvalidItemId:
            print(f"Error: Invalid item id {item_id}.")


@app.command()
def config():
    """List the path to the Items db."""
    with items_db() as db:
        print(db.path())


@app.command()
def count():
    """Return number of items in db."""
    with items_db() as db:
        print(db.count())


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Items is a small command line task tracking application.
    """
    if ctx.invoked_subcommand is None:
        list_items(owner=None, state=None)
