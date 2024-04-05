
from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from items.model import Item
from items.utils import items_db

app = FastAPI()


# By default, FastAPI's JSONResponse will render the response and then forget
# the original data that has been passed in. We subclass the default behavior to
# keep the original Python object, so that we can later pass it into Jinja.


class PreserveJSONResponse(JSONResponse):
    """A JSONResponse that remembers the original Python object."""

    def render(self, content: Any) -> bytes:
        # Store the Python object in self.original_data.
        self.original_data = content
        # Use the parent class to convert to JSON.
        return super().render(content)


app = FastAPI(default_response_class=PreserveJSONResponse)


# We define a custom route handler to hook into FastAPI's request/response
# handling. This is because we want to be able to automatically select a
# template based on the path operation function that handled the request.
# Apparently a simple middleware sadly doesn't have access to that information.


def get_template_render_route_class(template_dir: str) -> type:
    """Return APIRoute subclass that renders HTML templates from JSON.

    This is a function that returns a class, mainly because we'd like to be able
    to customize the template_dir, but we don't call __init__() on the class
    ourself, FastAPI does it.
    """

    class RenderRoute(APIRoute):

        # This method will be called on startup to get the actual handler.
        def get_route_handler(self) -> Callable:
            # Get the handler from the parent class.
            original = super().get_route_handler()

            # Set up Jinja to be able to render templates.
            jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
            )

            def is_hx(request: Request) -> bool:
                """Check whether the request is sent by HTMX."""
                # HTMX always sets this header, see
                # <https://htmx.org/docs/#request-headers>.
                return request.headers.get("HX-Request", "") == "true"

            def wants_html(request: Request) -> bool:
                """Check whether the client requested HTML."""
                # This is just a proof of concept, more solid `Accept` header
                # parsing would be required.
                return request.headers.get("Accept", "") == "text/html"

            def should_render(request: Request) -> bool:
                """Check whether this request should be rendered as HTML."""
                return is_hx(request) or wants_html(request)

            def get_template(endpoint: Callable | None) -> Template | None:
                """Get Jinja template instance for a given path operation."""
                if endpoint is None:
                    # We don't know the function that handled this request,
                    # therefore we can't select a corresponding template.
                    return None

                # Simply add `.html` to the function name and try to look this
                # up as a template file.
                try:
                    return jinja_env.get_template(f"{endpoint.__name__}.html")
                except TemplateNotFound:
                    return None

            # This is the actual function that is called on every request.
            async def route_handler(request: Request) -> Response:
                # Handle the request and get back a response.
                response = await original(request)

                if (
                    # rendering as HTML makes sense
                    should_render(request)
                    # the response is actually JSON that we can work with
                    and isinstance(response, PreserveJSONResponse)
                    # we have a template available
                    and (template := get_template(self.dependant.call))
                ):
                    # Render the Jinja template and return as HTML response.
                    return HTMLResponse(
                        template.render(
                            data=response.original_data,
                        )
                    )

                # If anything failed or the requirements were not met, return
                # the original response.
                return response

            # Provide FastAPI with the route handler.
            return route_handler

    return RenderRoute


app.router.route_class = get_template_render_route_class("templates")


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
