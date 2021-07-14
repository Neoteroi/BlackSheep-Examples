import uvicorn
from blacksheep.messages import Response
from blacksheep.server import Application
from blacksheep.server.responses import html

from piccoloexample import APP, create_schema, populate_data, set_engine

app = Application()


@app.route("/")
def home() -> Response:
    return html(
        """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>BlackSheep - mount example</title>
</head>
<body>
    <h1>BlackSheep - mount example</h1>
    <ol>
        <li>Navigate to <a href="/admin">the Piccolo Admin login page</a></li>
        <li>Sign in using (username: piccolo, password: piccolo123)</li>
        <li>Read more about <a href="https://github.com/piccolo-orm/piccolo_admin">Piccolo Admin here</a></li>
    </ol>
</body>
</html>
"""
    )


app.mount("/admin", APP)


def configure():
    engine = "sqlite"
    persist = False
    set_engine("sqlite")

    create_schema(persist=persist)

    if not persist:
        populate_data(inflate=1, engine=engine)


@app.on_start
async def configure_sqlite(_):
    configure()


if __name__ == "__main__":

    configure()
    uvicorn.run(app, host="127.0.0.1", port=44777, log_level="debug")
