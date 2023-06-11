import asyncio

import uvicorn
from blacksheep import Application, Content, Request, Response, StreamedContent
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


@app.route("*", methods="HEAD OPTIONS GET PATCH POST PUT DELETE".split())
async def proxy_all(request: Request, http_client: ClientSession) -> Response:
    content_type = request.headers.get_first(b"Content-Type")

    # TODO: what if there is no content type?
    length = 0

    async def gen():
        nonlocal length
        async for chunk in request.stream():
            yield chunk
            length += len(chunk)
        print("Proxied length", length)

    source_content_length = int(request.headers.get_first(b"Content-Length") or 0)
    print("Original length", source_content_length)
    # Note:
    # original length and proxied length are correct
    content = StreamedContent(content_type or b"application/octet-stream", gen)
    # content.length = source_content_length
    headers = [
        (key, value)
        for key, value in request.headers
        if key.lower() != b"content-length"
    ]
    headers.append((b"transfer-encoding", b"chunked"))
    proxied_request = Request(
        request.method,
        request.url.value,
        headers,
    ).with_content(content)
    response = await http_client.send(proxied_request)

    # we need to wait for the response content, too!
    async def response_content_reader():
        async for chunk in response.stream():
            yield chunk
        yield b""

    content_type = response.headers.get_first(b"Content-Type")
    response_headers = [
        (key, value)
        for key, value in request.headers
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

    data = await response.read()  # TODO: this is not good! This way we read the whole
    # response body in memory, to proxy. A better approach is to keep using asynchronous
    # generators
    return Response(
        response.status,
        response_headers,
        content=Content(content_type or b"application/octet-stream", data),  # type: ignore
    )


uvicorn.run(app, host="localhost", port=44555, lifespan="on")
