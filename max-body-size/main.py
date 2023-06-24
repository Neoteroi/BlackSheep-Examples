"""
This example illustrates how the maximum body size from a client can be validated inside
a request handler, efficiently processing chunks in memory.

At the time of this writing, blacksheep does not support configuring a maximum body size
globally, nor configuring a maximum body size for specific request handlers that would
validate the request body size also when trying to read the whole request content as
JSON, text, form data.

The following methods:
    text = await request.text()
    data = await request.json()
    data = await request.form()

all cause the whole request body to be read.
"""
from pathlib import Path

from blacksheep import Application, Request, json
from blacksheep.exceptions import BadRequest, HTTPException
from essentials.folders import ensure_folder


class MaxBodyExceededError(HTTPException):
    def __init__(self, max_size: int):
        super().__init__(413, "The request body exceeds the maximum size.")
        self.max_size = max_size


async def read_stream(request: Request, max_body_size: int = 1500000):
    """
    Reads a request stream, up to a maximum body length (default to 1.5 MB).
    """
    current_length = 0
    async for chunk in request.stream():
        current_length += len(chunk)

        if max_body_size > -1 and current_length > max_body_size:
            raise MaxBodyExceededError(max_body_size)

        yield chunk


app = Application(show_error_details=True)


@app.exception_handler(413)
async def handle_max_body_size(app, request, exc: MaxBodyExceededError):
    return json({"error": "Maximum body size exceeded", "max_size": exc.max_size})


app.serve_files("static")

app.use_cors(
    allow_methods="POST",
    allow_origins="*",
    max_age=300,
)


ensure_folder("out")


@app.router.post("/upload-file")
async def file_uploader(request: Request):
    file_name = request.get_first_header(b"File-Name")
    if not file_name:
        raise BadRequest("Missing file name.")

    file_name = file_name.decode()
    file_path = Path("out") / file_name

    try:
        with open(file_path, mode="wb") as example_file:
            async for chunk in read_stream(request):
                example_file.write(chunk)
    except MaxBodyExceededError:
        file_path.unlink()
        raise

    return {"status": "OK", "uploaded_file": file_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=44555, lifespan="on")
