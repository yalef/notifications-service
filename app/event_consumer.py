import pika
import typing
import logging
import email_sender
import config
import json
import models
import protocols


def establish_connection(
    host: str,
    port: int,
    login: str = "guest",
    password: str = "guest",
) -> pika.BlockingConnection:
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(login, password),
        )
    )


class Consumer(protocols.ConsumerProtocol):
    def __init__(
        self,
        connection: pika.connection.Connection,
        cfg: config.Config,
        logger: logging.Logger,
    ):
        self.logger = logger
        self.channel = connection.channel()
        callback = self._build_callback(cfg.SMTP_HOST, cfg.SMTP_PORT)
        self.configure_channel(callback)

    def _build_callback(
        self,
        smtp_host: str,
        smtp_port: int,
    ) -> typing.Callable:
        """Build callback function with provided smtp creds."""
        logger = self.logger

        def callback(
            channel: pika.channel.Channel,
            method: pika.spec.Basic.Deliver,
            properties: pika.BasicProperties,
            body: str,
        ):
            """Send message to received address."""
            logger.info(
                f"Received {body} from "
                f"{method.exchange} - {method.routing_key}",
            )
            sender = email_sender.MessageSender(smtp_host, smtp_port)
            try:
                data = models.NotificationBody(**json.loads(body))
                sender.send(
                    message=data.message,
                    from_addr=data.from_addr,
                    to_addr=data.to_addr,
                    subject=data.subject,
                )
                self.logger.info(f"Message {body} sent")
            except TypeError:
                self.logger.error(
                    "Wrong arg passed to event body",
                    exc_info=True,
                )
                return
            finally:
                channel.basic_ack(delivery_tag=method.delivery_tag)

        return callback

    def configure_channel(
        self,
        callback: typing.Callable,
    ) -> None:
        exchange_name = "notifications"
        queue_name = "notification_queue"

        # add exchange point and queue
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type="direct",
        )
        self.channel.queue_declare(queue_name)

        # bind queue on certain exchange point
        self.channel.queue_bind(
            queue_name,
            exchange=exchange_name,
            routing_key="",
        )

        # define weights of consumer instances
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
        )
        self.logger.info("Consumer configured")

    def consume(self):
        self.channel.start_consuming()


def setup_logger(env: config.Config) -> logging.Logger:
    log_level = (
        logging.INFO
        if cfg.ENVIRONMENT == config.EnvEnum.DEV
        else logging.ERROR
    )
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)
    return logger


if __name__ == "__main__":
    cfg = config.parse_config()
    logger = setup_logger(cfg)
    with establish_connection(
        host=cfg.AMQP_HOST,
        port=cfg.AMQP_PORT,
        login=cfg.AMQP_USERNAME,
        password=cfg.AMQP_PASSWORD,
    ) as amqp_connection:
        logger.info("Connection established")
        consumer = Consumer(
            cfg=cfg,
            connection=amqp_connection,
            logger=logger,
        )
        consumer.consume()
