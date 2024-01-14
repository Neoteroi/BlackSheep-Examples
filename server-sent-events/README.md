## Server-Sent events example

This example illustrates how to use built-in features for [Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) (SSE).

Note that, even though BlackSheep supports built-in features for SSE only since
version 2.0.6, previous versions of the web framework also could support SSE,
as they support response streaming.

Running the example:

1. create a Python virtual environment
2. install dependencies
3. run with `uvicorn server:app` to test with `uvicorn`, or
   `hypercorn server:app` to test with `hypercorn`
4. open the page in a web browser, you should see the message on the page
   updated every second, using information from the server

---

This example also shows how the `is_stopping` function can be used to detect
when the application server is shutting down.

```python
from blacksheep.server.application import is_stopping
```
