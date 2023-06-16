import pika


def create_rabbitmq_connection():
    # amqp: // rabbit_user: rabbit_password @ host:port / vhost
    host = "localhost"
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    return connection
