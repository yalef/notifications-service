import pika
import typing
import logging
import email_sender
import config
import json


class Consumer:
    def __init__(
        self,
        cfg: config.Config,
        logger: logging.Logger,
    ):
        self.logger = logger
        self.channel = self._establish_connection(
            host=cfg.AMQP_HOST,
            port=cfg.AMQP_PORT,
            login=cfg.AMQP_USERNAME,
            password=cfg.AMQP_PASSWORD,
        )
        callback = self._build_callback(cfg.SMTP_HOST, cfg.SMTP_PORT)
        self._configure_channel(self.channel, callback)

    def _establish_connection(
        self,
        host: str,
        port: int,
        login: str = "guest",
        password: str = "guest",
    ) -> pika.channel.Channel:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(login, password),
            )
        )
        self.logger.info(f"Connected to {host}:{port}")
        return connection.channel()

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
            data = json.loads(body)
            sender.send(
                message=data["message"],
                from_addr=data["from"],
                to_addr=data["to"],
                subject=data["subject"],
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)

        return callback

    def _configure_channel(
        self, channel: pika.channel.Channel, callback: typing.Callable
    ) -> None:
        exchange_name = "notifications"
        queue_name = "notification_queue"

        # add exchange point and queue
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type="direct",
        )
        channel.queue_declare(queue_name)

        # bind queue on certain exchange point
        channel.queue_bind(
            queue_name,
            exchange=exchange_name,
            routing_key="",
        )

        # define weights of consumer instances
        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
        )
        self.logger.info("Consumer configured")

    def consume(self):
        self.channel.start_consuming()


if __name__ == "__main__":
    cfg = config.parse_config()

    log_level = (
        logging.INFO
        if cfg.ENVIRONMENT == config.EnvEnum.DEV
        else logging.ERROR
    )
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)

    consumer = Consumer(
        cfg=cfg,
        logger=logger,
    )
    consumer.consume()
