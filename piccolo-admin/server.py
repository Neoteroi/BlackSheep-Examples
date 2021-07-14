import uvicorn
from blacksheep.server import Application

from piccoloexample import APP, create_schema, populate_data, set_engine

app = Application()


@app.route("/")
def home() -> str:
    return "Hello, World!"


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
