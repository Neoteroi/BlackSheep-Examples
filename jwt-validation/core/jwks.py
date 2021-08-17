import base64
import json
import urllib.request
from typing import List, TypedDict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from core.errors import FailedRequestError


class JWK(TypedDict):
    n: str
    e: str


class JWKS(TypedDict):
    keys: List[JWK]


def _ensure_bytes(key):
    if isinstance(key, str):
        key = key.encode("utf-8")
    return key


def _decode_value(val):
    decoded = base64.urlsafe_b64decode(_ensure_bytes(val) + b"==")
    return int.from_bytes(decoded, "big")


def _ensure_jwk_properties(jwk, *names):
    for name in names:
        if name not in jwk:
            raise ValueError(f"Expected a JWK defining a {name} property.")


def rsa_pem_from_jwk(jwk: JWK) -> bytes:
    _ensure_jwk_properties(jwk, "n", "e")
    return (
        RSAPublicNumbers(n=_decode_value(jwk["n"]), e=_decode_value(jwk["e"]))
        .public_key(default_backend())
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _read_json_data(url: str):
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise FailedRequestError(response)

        return json.loads(response.read())


def _read_openid_configuration(authority: str):
    return _read_json_data(authority.rstrip("/") + "/.well-known/openid-configuration")


def read_jwks_from_authority(authority: str) -> JWKS:
    openid_config = _read_openid_configuration(authority)

    if "jwks_uri" not in openid_config:
        raise ValueError("Expected a `jwks_uri` property in the OpenID Configuration")

    return _read_json_data(openid_config["jwks_uri"])
