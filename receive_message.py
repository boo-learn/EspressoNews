from shared.rabbitmq import create_rabbitmq_connection


def on_message(channel, method_frame, header_frame, body):
    print(f" [x] Received {body}")


def receive():
    connection = create_rabbitmq_connection()
    channel = connection.channel()
    queue_name = "queue1"
    channel.basic_consume(queue_name, on_message)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception as e:
        channel.stop_consuming()
        print("Ошибка:\n", e)


if __name__ == "__main__":
    receive()
