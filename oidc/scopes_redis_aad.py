"""
In this example the default Cookie handler is used to store user
context in a cookie (the id_token), and an access token and refresh token that
were obtained during the sign-in are stored in a Redis server.

In this case, to refresh a token from the client side, it's sufficient a POST request to
/refresh-token (by default), or the configured refresh_token_path.

async function refreshToken() {
    await fetch('/refresh-token', {
        method: "POST"
    });
}
"""
import redis.asyncio as redis
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import (
    CookiesOpenIDTokensHandler,
    OpenIDSettings,
    use_openid_connect,
)
from dotenv import load_dotenv

from common.redis import RedisTokensStore
from common.routes import register_routes
from common.secrets import Secrets

load_dotenv()
secrets = Secrets.from_env()
app = Application(show_error_details=True)


# AAD with custom scope
handler = use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://login.microsoftonline.com/b62b317a-19c2-40c0-8650-2d9672324ac4/v2.0/",
        client_id="499adb65-5e26-459e-bc35-b3e1b5f71a9d",
        client_secret=secrets.aad_client_secret,
        scope="openid profile offline_access email "
        "api://65d21481-4f1a-4731-9508-ad965cb4d59f/example",
    ),
)


@app.lifespan
async def configure_redis():
    """
    Configure an async Redis client, and dispose its connections when the application
    stops.
    See:
    https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
    """
    connection = redis.Redis()
    print(f"Ping successful: {await connection.ping()}")

    app.services.register(redis.Redis, instance=connection)

    # configure the tokens store of the authentication handler
    assert isinstance(handler.auth_handler, CookiesOpenIDTokensHandler)
    handler.auth_handler.tokens_store = RedisTokensStore(redis.Redis())

    yield connection

    print("Disposing the Redis connection pool...")
    await connection.close()


register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
