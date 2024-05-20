import pika
import pytz
import json
from datetime import datetime


def convert_timezone(datetime_str, source_timezone_str, target_timezone_str):
    datetime_str = datetime_str.strip()
    source_timezone_str = source_timezone_str.strip()
    target_timezone_str = target_timezone_str.strip()

    naive_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    source_timezone = pytz.timezone(source_timezone_str)
    target_timezone = pytz.timezone(target_timezone_str)

    localized_datetime = source_timezone.localize(naive_datetime)
    converted_datetime = localized_datetime.astimezone(target_timezone)

    return converted_datetime.strftime('%Y-%m-%d %H:%M:%S')


def o_message(channel, method, properties, body):
    data = json.loads(body)
    datetime_str = data.get('datetime')
    source_timezone = data.get('source_timezone')
    target_timezones = data.get('target_timezones')

    if not datetime_str or not source_timezone or not target_timezones:
        print('Missing timezones')
        return

    try:
        results = {}
        for target_timezone in target_timezones:
            converted_datetime = convert_timezone(datetime_str, source_timezone, target_timezone)
            results[target_timezone] = converted_datetime
            print(f"Original time in {source_timezone}: {datetime_str}")
            print(f"Converted time to {target_timezone}: {converted_datetime}")

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error converting: {e}")


def opening_cs(queue_name='timezone_conversion'):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=o_message,
        auto_ack=False)

    print('Waiting for requests. To exit: CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    opening_cs()
