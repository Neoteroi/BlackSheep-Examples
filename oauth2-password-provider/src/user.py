# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
import os
from .db import User

from pydantic import UUID4

from .db import TOKEN_DB, USER_DB, Token


def hashpw(password: str):
    """Hash a password for storing."""

    salt = os.urandom(32)
    digest = hashlib.pbkdf2_hmac("sha512", password.encode("utf8"), salt, 1024)
    hashed_password = f"{salt.hex()}${digest.hex()}"
    return hashed_password


def checkpw(password: str, hashed_password: str):
    """Check a hashed password."""

    salt_hex, digest_hex = hashed_password.split("$")
    return (
        digest_hex
        == hashlib.pbkdf2_hmac(
            "sha512",
            password.encode("utf8"),
            bytes.fromhex(salt_hex),
            1024,
        ).hex()
    )


class UserDAL:
    def register(self, username: str, password: str):
        """Register a user.

        Save user to storage and return user data.
        """

        hashed_password = hashpw(password)
        new_user = User(username=username, password=hashed_password)
        USER_DB[username] = new_user
        return new_user.dict()

    async def get_authuser_by_username(self, username):
        """Get user by username."""

        return USER_DB.get(username)

    async def save_refresh_token(
        self,
        user_id: UUID4,
        jti: UUID4,
        session_id: UUID4,
        expired_at: datetime,
    ):
        """Save refresh token to storage."""

        TOKEN_DB[jti] = Token(
            id=jti,
            user_id=user_id,
            session_id=session_id,
            expired_at=expired_at,
        )

    async def get_user_by_refresh_token(
        self,
        user_id: UUID4,
        refresh_jti: UUID4,
        session_id: UUID4,
    ) -> User | None:
        """Get user by refresh token."""

        token = TOKEN_DB.get(refresh_jti)
        if not token:
            return None
        if token.expired_at < datetime.utcnow():
            return None
        if token.user_id != user_id:
            return None
        if token.session_id != session_id:
            return None

        user = USER_DB.get(user_id)
        if not user:
            return None

        return user

    async def revoke_refresh_token(self, user_id: UUID4):
        """Revoke all refresh tokens for user."""

        for token in TOKEN_DB.values():
            if token.user_id == user_id:
                del TOKEN_DB[token.id]

    async def remove_used_refresh_token(self, token_id: UUID4):
        """Remove used refresh token from storage."""

        del TOKEN_DB[token_id]
