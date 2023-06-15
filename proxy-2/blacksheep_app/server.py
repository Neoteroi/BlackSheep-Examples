"""
Example application to test a proxy implemented with BlackSheep.
This application handles requests from the proxy (defined in blacksheep_proxy).
"""
from pathlib import Path

import uvicorn
from blacksheep import Application, Request, json
from essentials.folders import ensure_folder

app = Application()

app.serve_files("./blacksheep_app/static")


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


@app.router.post("/upload")
async def upload_files(request: Request):
    files = await request.files()
    folder = "out"

    all_files = []
    ensure_folder(folder)

    for part in files:
        assert part.file_name is not None
        with open(Path(folder) / part.file_name.decode(), mode="wb") as output_file:
            output_file.write(part.data)
        all_files.append(part.file_name.decode())

    data = await request.form()

    return json(
        {
            "folder": folder,
            "data": {
                "fname": data["fname"],  # type: ignore
                "lname": data["lname"],  # type: ignore
            },
            "files": [{"name": file} for file in all_files],
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=44777, lifespan="on")  # , http="h11"
