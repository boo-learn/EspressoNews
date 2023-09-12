import json
import logging

from shared.rabbitmq import Subscriber, QueuesType
from shared.config import RABBIT_HOST


class MailingListener:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.listener = Subscriber(host=RABBIT_HOST, queue=QueuesType[self.queue_name])

    def start_listening(self):
        self.listener.run()


class MailingLogicHandler:
    def __init__(self, connection, queue_name):
        self.connection = connection
        self.channel = self.connection.channel()
        self.queue_name = queue_name

    def start_listening(self):
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.handle_message, auto_ack=True)
        self.channel.start_consuming()

    def handle_message(self, channel, method, properties, body):
        try:
            message = json.loads(body)
            user_id = message.get("user_id")
            data = message.get("data")

            # Вызываем функцию в зависимости от типа сообщения
            if message["message_type"] == "collect_news":
                self.collect_news(user_id, data)
            elif message["message_type"] == "send_message":
                self.send_message(user_id, data)
            else:
                logging.warning(f"Unknown message type: {message['message_type']}")

        except Exception as e:
            logging.error(f"Error handling message: {str(e)}")

    def collect_news(self, user_id, data):
        # Логика обработки сообщения "collect_news"
        logging.info(f"Collecting news for user {user_id}")
        # Дополнительные действия...

    def send_message(self, user_id, data):
        # Логика отправки сообщения пользователю
        logging.info(f"Sending message to user {user_id}")
        # Дополнительные действия...