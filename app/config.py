import enum
import os
import dataclasses
import dotenv


class EnvEnum(enum.StrEnum):
    DEV = "dev"
    PROD = "prod"


@dataclasses.dataclass
class Config:
    AMQP_HOST: str
    AMQP_PORT: int
    AMQP_USERNAME: str
    AMQP_PASSWORD: str

    SMTP_HOST: str
    SMTP_PORT: int

    ENVIRONMENT: EnvEnum


def parse_config() -> Config:
    dotenv.load_dotenv(".env")
    return Config(
        AMQP_HOST=os.environ["AMQP_HOST"],
        AMQP_PORT=os.environ["AMQP_PORT"],
        AMQP_USERNAME=os.environ["AMQP_USERNAME"],
        AMQP_PASSWORD=os.environ["AMQP_PASSWORD"],
        SMTP_HOST=os.environ["SMTP_HOST"],
        SMTP_PORT=os.environ["SMTP_PORT"],
        ENVIRONMENT=os.environ["ENVIRONMENT"],
    )
