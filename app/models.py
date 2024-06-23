import dataclasses


@dataclasses.dataclass(frozen=True)
class NotificationBody:
    message: str
    from_addr: str
    to_addr: str
    subject: str
