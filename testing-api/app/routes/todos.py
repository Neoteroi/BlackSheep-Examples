# /app/routes/todos.py

from typing import Dict, List, Optional

from blacksheep.server.responses import not_found
from domain import CreateToDoInput, ToDo

from .router import delete, get, post

_MOCKED: Dict[int, ToDo] = {
    1: ToDo(
        id=1,
        title="BlackSheep Documentation",
        description="Update the documentation with information about the new features.",
    ),
    2: ToDo(
        id=2,
        title="Transfer the documentation",
        description="Transfer the documentation from Azure DevOps to GitHub.",
    ),
    3: ToDo(
        id=3,
        title="Mow the grass",
        description="Like in title.",
    ),
}


@get("/api/todos")
async def get_todos() -> List[ToDo]:
    return list(_MOCKED.values())


@get("/api/todos/{todo_id}")
async def get_todo(todo_id: int) -> Optional[ToDo]:
    try:
        return _MOCKED[todo_id]
    except KeyError:
        return not_found()


@post("/api/todos")
async def create_todo(data: CreateToDoInput) -> ToDo:
    item = ToDo(id=len(_MOCKED) + 1, title=data.title, description=data.description)
    _MOCKED[item.id] = item
    return item


@delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: int) -> None:
    try:
        del _MOCKED[todo_id]
    except KeyError:
        pass
