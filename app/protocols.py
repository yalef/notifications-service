import typing


class ConsumerProtocol(typing.Protocol):

    def configure_channel(
        self,
        callback: typing.Callable,
    ) -> None:
        pass

    def consume(self) -> None:
        pass
