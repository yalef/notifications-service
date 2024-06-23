import pika
import json
import sys


connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        "localhost",
        port=5672,
        credentials=pika.PlainCredentials(
            username="guest",
            password="guest",
        ),
    ),
)
print("Connection success")
channel = connection.channel()

channel.exchange_declare(exchange="notifications", exchange_type="direct")
msg = " ".join(sys.argv[1:])
channel.basic_publish(
    exchange="notifications",
    routing_key="",
    body=json.dumps(
        {
            "message": msg,
            "from_addr": "notificationservice@mail.com",
            "to_addr": "vadimvaselkov@gmail.com",
            "subject": "Test message",
        },
    ),
    properties=pika.BasicProperties(expiration="300000"),
)
print("Sent")
connection.close()
