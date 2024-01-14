import asyncio
from collections.abc import AsyncIterable

from blacksheep import Application, get
from blacksheep.server.application import is_stopping
from blacksheep.server.sse import ServerSentEvent, ServerEventsResponse

app = Application(show_error_details=True)
app.serve_files("static")


async def events_provider() -> AsyncIterable[ServerSentEvent]:
    i = 0

    while True:
        if is_stopping():
            print("The application is stopping!")
            break

        i += 1
        yield ServerSentEvent({"message": f"Hello World {i}"})

        try:
            await asyncio.sleep(1)
        except asyncio.exceptions.CancelledError:
            break


@get("/events")
def on_subscribe():
    return ServerEventsResponse(events_provider)
