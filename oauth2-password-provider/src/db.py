# -*- coding: utf-8 -*-

from pydantic import UUID4, BaseModel, Field
from datetime import datetime


from uuid import uuid4


class User(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    username: str
    password: str = Field(exclude=True)
    active: bool = True

    class Config:
        exclude = {"password"}


class Token(BaseModel):
    id: UUID4
    user_id: UUID4
    session_id: UUID4
    expired_at: datetime


USER_DB: dict[str, User] = {}
TOKEN_DB: dict[UUID4, Token] = {}
