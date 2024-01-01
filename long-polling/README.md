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

To test a client that disconnects, refresh a browser tab, then send a message from an active tab. 
The console should display messages like this one:

```bash
INFO:     127.0.0.1:40834 - "POST /publish HTTP/1.1" 200 OK
🔥🔥🔥 Request is disconnected!
🔥🔥🔥 Request is disconnected!
🔥🔥🔥 Request is disconnected!
🔥🔥🔥 Request is disconnected!
🔥🔥🔥 Request is disconnected!
INFO:     127.0.0.1:40832 - "GET /subscribe?random=0.16177484986012614 HTTP/1.1" 200 OK
INFO:     127.0.0.1:40882 - "GET /subscribe?random=0.08956117949704501 HTTP/1.1" 200 OK
INFO:     127.0.0.1:40882 - "GET /subscribe?random=0.08956117949704501 HTTP/1.1" 200 OK
INFO:     127.0.0.1:40832 - "GET /subscribe?random=0.16177484986012614 HTTP/1.1" 200 OK
```
