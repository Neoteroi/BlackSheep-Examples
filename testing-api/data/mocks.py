from typing import Dict, List

from domain import ToDo, ToDosRepository
from rodi import Container


class MockedToDosRepository(ToDosRepository):
    def __init__(self) -> None:
        self._todos: Dict[int, ToDo] = {}

    async def get_todos(self) -> List[ToDo]:
        return list(self._todos.values())

    async def store_todo(self, item: ToDo) -> None:
        self._todos[item.id] = item

    async def delete_todo(self, item: ToDo) -> None:
        try:
            del self._todos[item.id]
        except KeyError:
            pass


def register_mocked_services(container: Container) -> None:
    container.add_scoped(ToDosRepository, MockedToDosRepository)
