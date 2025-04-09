import pika
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get binding keys from command line arguments
binding_keys = sys.argv[1:] if len(sys.argv) > 1 else ["#"]  # Default: subscribe to all
if not binding_keys:
    print("Usage: python topic_exchange_subscriber.py [binding_key]...")
    print("Examples:")
    print("  python topic_exchange_subscriber.py \"#\"                     # All messages")
    print("  python topic_exchange_subscriber.py \"*.*.alert\"             # All alerts")
    print("  python topic_exchange_subscriber.py \"sensor.#\"              # All sensor data")
    print("  python topic_exchange_subscriber.py \"*.livingroom.*\"        # All events in living room")
    print("  python topic_exchange_subscriber.py \"sensor.*.data\"         # Sensor data from all locations")
    print("No binding keys specified, subscribing to all messages")

print(f" [*] Subscribing with binding keys: {', '.join(binding_keys)}")

# Connection parameters
url = "amqps://ouglwzrd:c_hpaHyMLopcTGtxDytHJzhSkfYVlC70@jaragua.lmq.cloudamqp.com/ouglwzrd"
# Alternative using environment variables
# url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')}"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Declare a topic exchange
exchange_name = "topic_exchange"
channel.exchange_declare(exchange=exchange_name, exchange_type="topic")

# Create a temporary queue with a random name
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange with each binding key
for binding_key in binding_keys:
    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name,
        routing_key=binding_key
    )
    print(f" [*] Bound to '{binding_key}'")

print(" [*] Waiting for messages. To exit press CTRL+C")

# Callback function
def callback(ch, method, properties, body):
    routing_key = method.routing_key
    message = body.decode()
    print(f" [x] Received [{routing_key}]: {message}")

# Consume messages
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

# Start consuming
channel.start_consuming() 