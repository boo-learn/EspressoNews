import json
from shared.rabbitmq import create_rabbitmq_connection
from tasks import subscribe, unsubscribe


def callback(ch, method, properties, body):
    message = json.loads(body)
    action = message.get('action')
    user_id = message.get('user_id')
    channel_id = message.get('channel_id')

    if action == 'subscribe':
        subscribe.delay(user_id, channel_id)
    elif action == 'unsubscribe':
        unsubscribe.delay(user_id, channel_id)


def main():
    connection = create_rabbitmq_connection()
    channel = connection.channel()

    channel.queue_declare(queue='subscriptions')

    channel.basic_consume(queue='subscriptions', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    main()
