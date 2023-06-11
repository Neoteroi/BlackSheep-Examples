import asyncio

import uvicorn
from blacksheep import Application, Request, Response, StreamedContent
from blacksheep.client import ClientSession
from blacksheep.client.pool import ClientConnectionPools

app = Application(show_error_details=True)


@app.lifespan
async def register_http_client():
    async with ClientSession(
        # This is the URL of the application to which we are proxying,
        # set this value in the request handler if you want to support dynamic proxies
        base_url="http://localhost:44777",
        pools=ClientConnectionPools(asyncio.get_running_loop()),
    ) as client:
        print("HTTP client created and registered as singleton")
        app.services.add_instance(client)
        yield

    print("HTTP client disposed")


def _get_proxied_request(request: Request) -> Request:
    """
    Gets a Request for the destination server, from a request of a source client.

    Note: the code should probably set X-Forwarded-* headers, and related headers.
    This is left as an exercise!
    """
    content_type = request.headers.get_first(b"Content-Type")

    async def read_request_stream():
        async for chunk in request.stream():
            yield chunk

    content = StreamedContent(
        content_type or b"application/octet-stream", read_request_stream
    )
    headers = [
        (key, value)
        for key, value in request.headers
        if key.lower() != b"content-length"
    ]
    headers.append((b"transfer-encoding", b"chunked"))
    return Request(
        request.method,
        request.url.value,
        headers,
    ).with_content(content)


def _get_proxied_response(response: Response) -> Response:
    """
    Gets a Response for the source client, from a Response obtained from the back-end
    for which requests are proxied.
    """

    # The above line completes when the original server sends the headers, but
    # we need to wait for the response content, too!
    async def response_content_reader():
        async for chunk in response.stream():
            yield chunk
        yield b""

    content_type = response.headers.get_first(b"Content-Type")
    response_headers = [
        (key, value)
        for key, value in response.headers
        if key.lower() not in {b"date", b"server", b"content-length", b"content-length"}
    ]
    response_headers.append((b"transfer-encoding", b"chunked"))

    return Response(
        response.status,
        response_headers,
        content=StreamedContent(
            content_type or b"application/octet-stream", response_content_reader
        ),
    )


@app.route("*", methods="HEAD OPTIONS GET PATCH POST PUT DELETE".split())
async def proxy_all(request: Request, http_client: ClientSession) -> Response:
    proxied_request = _get_proxied_request(request)
    response = await http_client.send(proxied_request)
    return _get_proxied_response(response)


uvicorn.run(app, host="localhost", port=44555, lifespan="on")
