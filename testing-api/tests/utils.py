from typing import Any
from blacksheep.contents import Content
from essentials.json import dumps


def json_content(data: Any) -> Content:
    return Content(
        b"application/json",
        dumps(data, separators=(",", ":")).encode("utf8"),
    )
