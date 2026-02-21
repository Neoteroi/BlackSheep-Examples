from dataclasses import dataclass, field
import aiofiles
from blacksheep import Application, FromForm, FileBuffer, Request, FromFiles
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info

app = Application(show_error_details=True)

docs = OpenAPIHandler(info=Info(title="Example API", version="0.0.1"))
docs.bind_app(app)

app.serve_files("static", discovery=True, fallback_document="index.html")


async def _write_chunks(source, dest_path: str, chunk_size: int = 65536) -> None:
    async with aiofiles.open(dest_path, "wb") as out_file:
        while chunk := source.read(chunk_size):
            await out_file.write(chunk)


@dataclass
class InputExampleOptimal:
    username: str
    avatar: FileBuffer
    documents: list[FileBuffer] = field(default_factory=list)
    subscribe: bool = False


@app.router.post("/from-files")
async def from_files(files: FromFiles):
    for file in files.value:
        await file.save_to(f".out/{file.file_name.decode()}")
    return "OK"


@app.router.post("/upload")
async def create_profile(data: FromForm[InputExampleOptimal]):
    # This is just an example!
    value = data.value
    assert isinstance(value, InputExampleOptimal)
    assert isinstance(value.subscribe, bool)

    avatar = value.avatar
    await avatar.save_to(f".out/{avatar.file_name}")

    if value.documents:
        for document in value.documents:
            await document.save_to(f".out/{document.file_name}")

    return {
        "status": "created",
        "username": value.username,
        "subscribe": value.subscribe,
        "avatar_filename": avatar.file_name,
        "documents_count": len(value.documents) if value.documents else 0
    }



@app.router.post("/upload-text")
async def upload_text(request: Request):
    """
    Test multipart/form-data field post with long text.
    """
    file_size = 0

    async for part in request.multipart_stream():
        print(part.name)
        if part.file_name:
            file_size = await part.save_to(f".out/{part.file_name}")
        else:
            file_size = await part.save_to(f".out/document.txt")

    return {
        "status": "uploaded",
        "file_size": file_size
    }


@app.router.post("/upload-files-form-method")
async def upload_files_form_method_1(request: Request):
    data = await request.form()

    avatar = data['avatar'][0]
    await _write_chunks(avatar.file, f".out/{avatar.file_name.decode()}")

    for document in data["documents"]:
        await _write_chunks(document.file, f".out/{document.file_name.decode()}")
    return "OK"

@app.router.post("/upload-files-multipart-method")
async def upload_files_form_method_2(request: Request):
    parts = await request.multipart()

    for part in parts:
        if part.file_name:
            await _write_chunks(part.file, f".out/{part.file_name.decode()}")
        else:
            await _write_chunks(part.file, f".out/{part.name.decode()}")
    return "OK"


@app.router.post("/upload-files")
async def upload_files_streaming(request: Request):
    """
    Handle file uploads using streaming multipart parsing with StreamingFormPart.
    This is more memory-efficient for large files as it doesn't load
    the entire request body into memory at once.
    """
    uploaded_files = []
    file_count = 0
    total_size = 0

    # Stream multipart data without loading everything into memory
    async for part in request.multipart_stream():
        if part.file_name:
            # This is a file upload - use StreamingFormPart's save_to method
            file_name = part.file_name
            file_path = f".out/{file_name}"

            # Stream the file directly to disk
            file_size = await part.save_to(file_path)

            total_size += file_size
            file_count += 1

            uploaded_files.append({
                "field_name": part.name,
                "file_name": file_name,
                "content_type": part.content_type if part.content_type else "unknown",
                "size_bytes": file_size
            })
        else:
            # This is a regular form field (non-file)
            ...

    return {
        "status": "uploaded",
        "files_count": file_count,
        "total_size_bytes": total_size,
        "files": uploaded_files
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=44555)
