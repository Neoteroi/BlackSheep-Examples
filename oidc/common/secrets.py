import os
from dataclasses import dataclass


@dataclass
class Secrets:
    auth0_client_secret: str
    okta_client_secret: str
    aad_client_secret: str

    @classmethod
    def from_env(cls):
        return cls(
            auth0_client_secret=os.environ["AUTH0_CLIENT_SECRET"],
            okta_client_secret=os.environ["OKTA_CLIENT_SECRET"],
            aad_client_secret=os.environ["AAD_CLIENT_SECRET"],
        )
