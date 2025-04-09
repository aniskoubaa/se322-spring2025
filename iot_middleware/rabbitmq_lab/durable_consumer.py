import pika
import os
import time
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

# Declare the same durable queue
queue_name = "durable_queue"
channel.queue_declare(queue=queue_name, durable=True)

# Set QoS - only process one message at a time
# This prevents RabbitMQ from overwhelming this consumer
channel.basic_qos(prefetch_count=1)

# Simulate message processing
def process_message(message):
    """Simulate message processing with artificial delay"""
    print(f" [.] Processing message: {message}")
    # Simulate work with delay
    time.sleep(2)
    print(f" [✓] Done processing: {message}")
    return True

# Callback function with manual acknowledgment
def callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Received: {message}")
    print(f" [i] Message properties: priority={properties.priority}, type={properties.content_type}")
    
    # Process the message
    success = process_message(message)
    
    if success:
        # Acknowledge successful processing
        print(" [✓] Acknowledging message")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # Negative acknowledgment if processing failed
        # Message will be requeued
        print(" [!] Failed processing, rejecting message (will be requeued)")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

print(" [*] Waiting for messages. To exit press CTRL+C")

# Consume messages with manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False  # Manual acknowledgment
)

# Start consuming
channel.start_consuming() 