import pathlib

from blacksheep import Application, WebSocket, WebSocketDisconnectError
from blacksheep.server.responses import redirect
from .connection import ConnectionManager

APP_PATH = pathlib.Path(__file__).parent / 'static'

app = Application()
app.serve_files(APP_PATH, root_path='app')

manager = ConnectionManager()


@app.router.ws('/ws/{client_id}')
async def ws(websocket: WebSocket, client_id: str):
    conn = await manager.connect(websocket, client_id)

    try:
        while True:
            await manager.manage(conn)
    except WebSocketDisconnectError:
        await manager.disconnect(conn)


@app.router.get('/')
def index():
    return redirect('/app')
