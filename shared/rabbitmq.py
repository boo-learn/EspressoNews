import pika


def create_rabbitmq_connection():
    connection_params = pika.ConnectionParameters(host='localhost')
    return pika.BlockingConnection(connection_params)
