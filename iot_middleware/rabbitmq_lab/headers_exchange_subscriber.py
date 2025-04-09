import pika
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection parameters
url = "amqps://ouglwzrd:c_hpaHyMLopcTGtxDytHJzhSkfYVlC70@jaragua.lmq.cloudamqp.com/ouglwzrd"
# Alternative using environment variables
# url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')}"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Declare a headers exchange
exchange_name = "headers_exchange"
channel.exchange_declare(exchange=exchange_name, exchange_type="headers")

# Create a temporary queue with a random name
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Define message binding headers
# By default, listen for indoor sensor messages unless specified in command line
bind_headers = {}
match_type = "all"  # options: "all" (x-match=all) or "any" (x-match=any)

# Get binding parameters from command line
if len(sys.argv) > 1:
    # Parse command line arguments: key1=value1 key2=value2 ...
    for arg in sys.argv[1:]:
        if arg.startswith("x-match="):
            match_type = arg.split("=")[1]
            continue
            
        if "=" in arg:
            key, value = arg.split("=", 1)
            bind_headers[key] = value

# If no headers specified, use default filter
if not bind_headers:
    bind_headers = {"device_type": "sensor", "location": "indoor"}
    print("No header matches specified, using default: indoor sensors")
    print("Usage: python headers_exchange_subscriber.py [x-match=all|any] [key1=value1] [key2=value2] ...")
    print("Examples:")
    print("  python headers_exchange_subscriber.py device_type=sensor")
    print("  python headers_exchange_subscriber.py x-match=any location=indoor priority=high")
    print("  python headers_exchange_subscriber.py x-match=all device_type=gateway data_format=json")

# Print binding information
print(f" [*] Binding with headers: {bind_headers}")
print(f" [*] Match type: {match_type} ({'all headers must match' if match_type == 'all' else 'any header must match'})")

# Bind the queue to the exchange with the specified headers
channel.queue_bind(
    exchange=exchange_name,
    queue=queue_name,
    arguments={"x-match": match_type, **bind_headers}
)

print(" [*] Waiting for messages. To exit press CTRL+C")

# Callback function
def callback(ch, method, properties, body):
    print(f" [x] Received message with headers: {properties.headers}")
    print(f"     Body: {body.decode()}")

# Consume messages
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

# Start consuming
channel.start_consuming() 