import asyncio

import uvicorn
from blacksheep import Application, Request, Response, StreamedContent
from blacksheep.client import ClientSession
from blacksheep.client.pool import ClientConnectionPools
from blacksheep.headers import Headers

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


def get_content_length(headers: Headers) -> int:
    content_length_header = headers.get_first(b"content-length")
    return int(content_length_header) if content_length_header else -1


def _get_proxied_request(request: Request) -> Request:
    """
    Gets a Request for the destination server, from a request of a source client.

    Note: the code should probably set X-Forwarded-* headers, and related headers.
    This is left as an exercise!
    """

    async def read_request_stream():
        async for chunk in request.stream():
            yield chunk

    content_length = get_content_length(request.headers)
    content_type = request.headers.get_first(b"Content-Type")
    content = (
        None
        if content_type is None
        else StreamedContent(
            content_type or b"application/octet-stream",
            read_request_stream,
            content_length,
        )
    )
    headers = [
        (key, value)
        for key, value in request.headers
        if key.lower()
        not in {
            b"content-type",
            b"content-length",
            b"transfer-encoding",
        }
    ]
    new_request = Request(
        request.method,
        request.url.value,
        headers,
    )

    return new_request if content is None else new_request.with_content(content)


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

    content_type = response.headers.get_first(b"Content-Type")
    response_headers = [
        (key, value)
        for key, value in response.headers
        if key.lower()
        not in {
            b"date",
            b"server",
            b"content-type",
            b"content-length",
            b"transfer-encoding",
        }
    ]

    content_length = get_content_length(response.headers)

    content = (
        StreamedContent(
            content_type or b"application/octet-stream",
            response_content_reader,
            content_length,
        )
        if content_type
        else None
    )

    return Response(
        response.status,
        response_headers,
        content=content,
    )


@app.route("*", methods="HEAD OPTIONS GET PATCH POST PUT DELETE".split())
async def proxy_all(request: Request, http_client: ClientSession) -> Response:
    proxied_request = _get_proxied_request(request)
    response = await http_client.send(proxied_request)
    return _get_proxied_response(response)


uvicorn.run(app, host="localhost", port=44555, lifespan="on")  # , http="h11"
