import asyncio
from dataclasses import dataclass
import signal

from blacksheep import Application, Request, get, no_content, ok, post, text, json

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
            print("Task cancelled...")
            return no_content()
        else:
            return response
        finally:
            self._queues.remove(request_queue)
            self._tasks.remove(task)

    async def wait_for_message(self, queue):
        message = await queue.get()
        return text(message)

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


@app.on_stop
async def on_stop(application: Application) -> None:
    try:
        manager.cancel_all_tasks()
    except:
        pass


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
