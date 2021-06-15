from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class ToDo(BaseModel):
    id: int
    title: str
    description: str


class CreateToDoInput(BaseModel):
    title: str
    description: str


class ToDosRepository(ABC):
    @abstractmethod
    async def get_todos(self) -> List[ToDo]:
        ...

    @abstractmethod
    async def store_todo(self, item: ToDo) -> None:
        ...

    @abstractmethod
    async def delete_todo(self, item: ToDo) -> None:
        ...
