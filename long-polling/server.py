import asyncio
import signal
from dataclasses import dataclass

from blacksheep import Application, Request, get, json, no_content, ok, post, text

app = Application()
app.serve_files("static")


@dataclass
class MessageInput:
    text: str


class MessageManager:
    def __init__(self) -> None:
        self.closing = False
        self._queues: list[asyncio.Queue] = []
        self._tasks: list[asyncio.Task] = []
        self._timeout: float = 60

    async def subscribe(self, request: Request):
        if self.closing:
            return text("")

        request_queue = asyncio.Queue()
        self._queues.append(request_queue)
        task = asyncio.create_task(self.wait_for_message(request_queue))
        self._tasks.append(task)

        try:
            response = await task
        except asyncio.CancelledError:
            # Tasks are cancelled when the application stops
            print("Task cancelled...")
            return no_content()
        else:
            return response
        finally:
            self._queues.remove(request_queue)
            self._tasks.remove(task)

    async def wait_for_message(self, queue):
        try:
            async with asyncio.timeout(self._timeout):
                message = await queue.get()
                return text(message)
        except TimeoutError:
            # Waited for the timeout period, now closing a Long-Polling request.
            # The client must create a new request.
            return text("")

    async def add_message(self, message):
        for queue in self._queues:
            await queue.put(message)

    def cancel_all_tasks(self):
        self.closing = True  # Stop processing new requests
        for queue in self._queues:
            queue.put_nowait("")


manager = MessageManager()


@app.on_start
async def on_start(_):
    # See the conversation here:
    # https://github.com/encode/uvicorn/issues/1579#issuecomment-1419635974
    default_sigint_handler = signal.getsignal(signal.SIGINT)

    def terminate_now(signum, frame):
        # clean up:
        print("Cancelling the tasks...")
        manager.cancel_all_tasks()
        default_sigint_handler(signum, frame)  # type: ignore

    signal.signal(signal.SIGINT, terminate_now)


@get("/subscribe")
async def on_subscribe(request):
    return await manager.subscribe(request)


@get("/stats")
def get_stats():
    return json({"tasks": len(manager._tasks)})


@post("/publish")
async def publish_message(data: MessageInput):
    await manager.add_message(data.text)
    return ok()
