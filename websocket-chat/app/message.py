import dataclasses


@dataclasses.dataclass
class Message:
    author: str
    text: str
    timestamp: str

    def asdict(self):
        return dataclasses.asdict(self)
