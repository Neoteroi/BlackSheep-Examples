import json
import urllib.request
from http.client import HTTPResponse


class FailedRequestError(Exception):
    def __init__(self, response: HTTPResponse) -> None:
        super().__init__(
            f"Response status does not indicate success: {response.status}"
        )
        self.status = response.status
        self.data = response.read()


def _read_json_data(url: str):
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise FailedRequestError(response)

        return json.loads(response.read())


def read_openid_configuration(authority: str):
    return _read_json_data(authority.rstrip("/") + "/.well-known/openid-configuration")


def read_jwks(authority: str):
    openid_config = read_openid_configuration(authority)

    if "jwks_uri" not in openid_config:
        raise ValueError("Expected a `jwks_uri` property in the OpenID Configuration")

    return _read_json_data(openid_config["jwks_uri"])


if __name__ == "__main__":
    print(
        json.dumps(
            read_jwks(
                "https://login.microsoftonline.com/robertoprevatogmail.onmicrosoft.com"
            ),
            indent=4,
        )
    )
