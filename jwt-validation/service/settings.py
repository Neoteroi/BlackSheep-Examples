from dataclasses import dataclass
from typing import Sequence


@dataclass
class AuthSettings:
    authority: str
    client_id: str
    valid_issuers: Sequence[str]
    valid_audiences: Sequence[str]


@dataclass
class Settings:
    auth: AuthSettings

    @classmethod
    def from_configuration(cls, configuration):
        return cls(auth=AuthSettings(**configuration.auth.values))
