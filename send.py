import pika
import json


def publish_message(message, queue_name='timezone_conversion'):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    print(f" Sent {message}")
    connection.close()


if __name__ == '__main__':
    message = {
        'datetime': '2024-05-19 12:00:00',
        'source_timezone': 'America/New_York',
        'target_timezones': ['Europe/London', 'Asia/Tokyo', 'Australia/Sydney', 'America/Los_Angeles']
    }
    publish_message(message)
