"""
Example application to test a proxy implemented with BlackSheep.
"""
from essentials.folders import ensure_folder
from flask import Flask, jsonify, request
from markupsafe import escape

# https://flask.palletsprojects.com/en/1.1.x/server/#server
app = Flask(__name__, static_url_path="", static_folder="static")


@app.route("/hello-world")
def hello_world():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!", 200, {"Content-Type": "text/plain"}


# https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files

    assert bool(files)

    folder = "out"

    ensure_folder(folder)
    all_files = files.getlist("files")

    for part in all_files:
        part.save(f"./{folder}/{part.filename}")

    return jsonify(
        {
            "folder": folder,
            "data": request.form,
            "files": [{"name": file.filename} for file in all_files],
        }
    )


@app.route("/picture.jpg")
def serve_picture():
    return app.send_static_file("pexels-photo-126407.jpeg")


if __name__ == "__main__":
    app.run(host="localhost", port=44777, debug=True)
