import os
from multiprocessing import Process
from time import sleep
from urllib.parse import urljoin

import pytest
import requests
import uvicorn
from server import app


class ClientSession(requests.Session):
    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        return super().request(method, urljoin(self.base_url, url), *args, **kwargs)


def get_sleep_time():
    # when starting a server process,
    # a longer sleep time is necessary on Windows
    if os.name == "nt":
        return 1.5
    return 0.5


server_host = "127.0.0.1"
server_port = 44555


@pytest.fixture(scope="session")
def client_session():
    return ClientSession(f"http://{server_host}:{server_port}")


def _start_server():
    uvicorn.run(app, host=server_host, port=server_port, log_level="debug")


@pytest.fixture(scope="session", autouse=True)
def server():
    server_process = Process(target=_start_server)
    server_process.start()
    sleep(get_sleep_time())

    if not server_process.is_alive():
        raise TypeError("The server process did not start!")

    yield 1

    sleep(1.2)
    server_process.terminate()


@pytest.mark.asyncio
async def test_get(client_session):
    response = client_session.get("/api/todos/1")

    assert response.status_code == 200
