from typing import Any

import pytest
from blacksheep.contents import Content
from blacksheep.testing import TestClient
from domain import CreateToDoInput, ToDo
from essentials.json import dumps


def json_content(data: Any) -> Content:
    return Content(
        b"application/json",
        dumps(data, separators=(",", ":")).encode("utf8"),
    )


@pytest.mark.asyncio
async def test_create_and_get_todo(test_client: TestClient) -> None:

    create_input = CreateToDoInput(
        title="Update documentation",
        description=("Update blacksheep's documentation to describe all new features."),
    )

    response = await test_client.post(
        "/api/todos",
        content=json_content(create_input),
    )

    assert response is not None

    data = await response.json()

    assert data is not None
    assert "id" in data

    todo_id = data["id"]
    response = await test_client.get(f"/api/todos/{todo_id}")

    assert response is not None
    data = await response.json()

    assert data is not None

    todo = ToDo(**data)

    assert todo.title == create_input.title
    assert todo.description == create_input.description
