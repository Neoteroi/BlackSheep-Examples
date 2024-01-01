import asyncio
import signal
from dataclasses import dataclass

from blacksheep import Application, Request, get, json, no_content, ok, post, text

app = Application()
app.serve_files("static")


@dataclass
class MessageInput:
    text: str


@dataclass(slots=True)
class ActiveRequest:
    request: Request
    task: asyncio.Task
    queue: asyncio.Queue


class MessageManager:
    def __init__(self) -> None:
        self.closing = False
        self._active_requests: list[ActiveRequest] = []
        self._timeout: float = 60

    async def subscribe(self, request: Request):
        if self.closing:
            return text("")

        request_queue = asyncio.Queue()
        task = asyncio.create_task(self.wait_for_message(request, request_queue))
        active_request = ActiveRequest(request, task, request_queue)
        self._active_requests.append(active_request)

        try:
            response = await task
        except asyncio.CancelledError:
            # Tasks are cancelled when the application stops
            print("Task cancelled...")
            return no_content()
        else:
            return response
        finally:
            try:
                self._active_requests.remove(active_request)
            except ValueError:
                # All is good, the item was already removed
                pass

    async def wait_for_message(self, request, queue):
        try:
            async with asyncio.timeout(self._timeout):
                message = await queue.get()

                # Note: here it is possible to check if the request is
                # disconnected using: if await request.is_disconnected()
                #
                # This can be useful to avoid consuming operations from this point,
                # or to cancel tasks.
                if await request.is_disconnected():
                    print("🔥🔥🔥 Request is disconnected!")
                    return
                return text(message)
        except TimeoutError:
            # Waited for the timeout period, now closing a Long-Polling request.
            # The client must create a new request.
            return text("")

    async def add_message(self, message):
        for item in self._active_requests:
            await item.queue.put(message)

    def cancel_all_tasks(self):
        self.closing = True  # Stop processing new requests
        for item in self._active_requests:
            item.task.cancel()

    def __len__(self):
        return len(self._active_requests)


manager = MessageManager()


async def periodic_check():
    """
    Periodically checks if active long-polling requests are disconnected, and cancels
    them if needed.
    """
    while True:
        await asyncio.sleep(5)  # Example: check every 5 seconds

        print("Checking active connections...")

        for item in manager._active_requests:
            request = item.request
            if await request.is_disconnected():
                print(f"Request {id(request)} is disconnected, cancelling its task...")
                item.task.cancel()


@app.on_start
async def start_periodic_check():
    asyncio.create_task(periodic_check())


@app.on_start
async def on_start(_):
    # See the conversation here:
    # https://github.com/encode/uvicorn/issues/1579#issuecomment-1419635974
    default_sigint_handler = signal.getsignal(signal.SIGINT)

    def terminate_now(signum, frame):
        # clean up:
        print(f"Cancelling the tasks ({len(manager)})...")
        manager.cancel_all_tasks()
        default_sigint_handler(signum, frame)  # type: ignore

    signal.signal(signal.SIGINT, terminate_now)


@get("/subscribe")
async def on_subscribe(request):
    return await manager.subscribe(request)


@get("/stats")
def get_stats():
    return json({"active_requests": len(manager._active_requests)})


@post("/publish")
async def publish_message(data: MessageInput):
    await manager.add_message(data.text)
    return ok()
