from shared.rabbitmq import create_rabbitmq_connection


def send(message: str = "Test message"):
    connection = create_rabbitmq_connection()
    channel = connection.channel()
    queue_name = "queue1"
    # channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=f'{message} for {queue_name}')
    print("message send")
    connection.close()


if __name__ == "__main__":
    send()