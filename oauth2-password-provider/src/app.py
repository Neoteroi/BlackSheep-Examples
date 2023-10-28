# -*- coding: utf-8 -*-

from blacksheep import Application
from blacksheep.server.responses import json
from blacksheep.server.authorization import allow_anonymous, auth
from blacksheep.server.bindings import FromJSON
from .db import User


from .password_auth import HMACAlgorithm, OAuth2PasswordSettings, use_oauth2_password
from .user import UserDAL

app = Application()
use_oauth2_password(
    app,
    OAuth2PasswordSettings(
        secret="secret",
        algorithm=HMACAlgorithm("HS256"),
        token_path="/api/token",
        refresh_path="/api/refresh",
        revoke_path="/api/revoke",
    ),
)


@allow_anonymous()
@app.router.get("/api/anonymous")
def anonymous():
    return json({"message": "Hello, anonymous!"})


@allow_anonymous()
@app.router.post("/api/register")
async def register(
    user_registration: FromJSON[User],
):
    """Register user."""
    username = user_registration.value.username
    password = user_registration.value.password

    user_dal = UserDAL()
    user = user_dal.register(username, password)

    return json(data=user)


@auth("authenticated")
@app.router.get("/api/protected")
async def protected():
    """Protected endpoint."""
    return json({"message": "Hello, authenticated user!"})
