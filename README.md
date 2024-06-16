# notifications service

Consume incoming events from AMQP channel
and send messages described in events by email

## how-to
```bash
  docker compose up -d  # start amqp and mail server
  python app/event_consumer.py  # start consuming events from channel
```
