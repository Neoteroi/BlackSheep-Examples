import asyncio
import os
from collections.abc import AsyncIterable

from blacksheep import Application, Request, get
from blacksheep.server.process import is_stopping
from blacksheep.server.sse import ServerSentEvent

app = Application(show_error_details=True)
app.serve_files("static")


# Enable the signal handler to detect when the application is stopping.
os.environ["APP_SIGNAL_HANDLER"] = "1"


@get("/events")
async def events_handler(request: Request) -> AsyncIterable[ServerSentEvent]:
    i = 0

    while True:
        if await request.is_disconnected():
            print("The request is disconnected!")
            break

        if is_stopping():
            print("The application is stopping!")
            break

        i += 1
        yield ServerSentEvent({"message": f"Hello World {i}"})

        try:
            await asyncio.sleep(1)
        except asyncio.exceptions.CancelledError:
            break
