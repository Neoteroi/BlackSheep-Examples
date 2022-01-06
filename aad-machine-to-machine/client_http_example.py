"""
This module shows an example of how the client credentials flow with secret can be used
directly using an HTTP Client, for Azure Active Directory.
This should be used only in those scenario when legacy applications would not support
MSAL for Python.
"""
import os

import httpx
from dotenv import load_dotenv

# read .env file into environment variables
load_dotenv()


def ensure_success(response: httpx.Response) -> None:
    if response.status_code < 200 or response.status_code > 399:
        body = response.text
        raise ValueError(
            f"The response status does not indicate success {response.status_code}; "
            f"Response body: {body}"
        )


def get_access_token() -> str:
    response = httpx.post(
        os.environ["AAD_AUTHORITY"].rstrip("/") + "/oauth2/v2.0/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["APP_CLIENT_ID"],
            "client_secret": os.environ["APP_CLIENT_SECRET"],
            "scope": os.environ["APP_CLIENT_SCOPE"],
        },
    )
    ensure_success(response)
    data = response.json()
    assert "access_token" in data, "The response body must include an access token"
    return data["access_token"]


if __name__ == "__main__":
    print("Access token: " + get_access_token())
