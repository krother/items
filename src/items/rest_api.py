
from typing import Any, Callable

from fastapi import FastAPI  #, Request, Response
#from fastapi.responses import HTMLResponse, JSONResponse
#from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
#from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
# from fastapi_htmx.model import BookRequest, BookResponse, Item

from items.model import Item
from items.utils import items_db

app = FastAPI()


@app.get("/items")
def get_all_items() -> list[Item]:
    """Return a list of all items."""
    with items_db() as db:
        return db.list_items()



#@app.post("/books")
#def get_message(book: BookRequest) -> BookResponse:
#    return BookResponse(full_title=f"{book.title} ({book.subtitle})")


# Also let FastAPI serve the HTMX "frontend" of our application.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
