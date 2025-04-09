import pika
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get severity filter from command line
severities = sys.argv[1:] if len(sys.argv) > 1 else ["info", "warning", "error", "critical"]
if not severities:
    print("Usage: python direct_exchange_subscriber.py [info] [warning] [error] [critical]")
    print("No severities specified, subscribing to all")
    severities = ["info", "warning", "error", "critical"]

print(f" [*] Subscribing to severity levels: {', '.join(severities)}")

# Connection parameters
url = "amqps://ouglwzrd:c_hpaHyMLopcTGtxDytHJzhSkfYVlC70@jaragua.lmq.cloudamqp.com/ouglwzrd"
# Alternative using environment variables
# url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')}"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Declare a direct exchange
exchange_name = "direct_exchange"
channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

# Create a temporary queue with a random name
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange for each severity level
for severity in severities:
    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name,
        routing_key=severity
    )
    print(f" [*] Bound to '{severity}' severity")

print(" [*] Waiting for messages. To exit press CTRL+C")

# Callback function
def callback(ch, method, properties, body):
    severity = method.routing_key
    message = body.decode()
    print(f" [x] Received '{severity}': {message}")
    # Acknowledge message (manual acknowledgment)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consume messages with manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

# Start consuming
channel.start_consuming() 