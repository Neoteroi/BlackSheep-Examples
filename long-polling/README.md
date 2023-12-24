# Long-polling example

This example shows an example of long-polling implemented with BlackSheep.

The JavaScript and front-end part of this example was adopted from:
[https://javascript.info/long-polling](https://javascript.info/long-polling).

## Trying the example

1. Create a Python virtual environment
2. Install depedencies (`pip install blacksheep uvicorn`)
3. Run the server with `uvicorn server:app`
4. Open the web site in several browser tabs to see the effect of long-polling
5. Submit messages in a browser tab: see how messages are immediately visible
   in all tabs, thanks to long-polling
6. Read the source code in `server.py` to see how long-polling is achieved using
   `asyncio.Queue`, and how `signal.getsignal(signal.SIGINT)` is used in the
   `@app.on_start` event handler.
7. The `/subscribe` method is used to subscribe for long-polling.
8. The `/publish` method is used to publish a message to all subscribers.

## How to test a disconnection

To test a client that disconnects, use for example a Python client with a short
timeout:

```python
import asyncio
from blacksheep.client import ClientSession

async def client_example():
    # Note: request_timeout 5 seconds below causes the client to close the
    # connection after 5 seconds
    async with ClientSession(request_timeout=5) as client:
        response = await client.get("http://localhost:8000/subscribe")

        assert response is not None
        text = await response.text()
        print(text)


asyncio.run(client_example())

```
