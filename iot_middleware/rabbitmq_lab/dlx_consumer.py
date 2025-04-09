import pika
import os
import time
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

# Get queue type from command line
if len(sys.argv) > 1 and sys.argv[1] == "dead-letter":
    queue_name = "dead_letter_queue"
    queue_type = "dead-letter"
else:
    queue_name = "main_processing_queue"
    queue_type = "main"

# Declare or verify the dead-letter exchange
if queue_type == "dead-letter":
    dlx_exchange = "dlx_exchange"
    channel.exchange_declare(exchange=dlx_exchange, exchange_type="direct")
    
    # Declare the dead-letter queue
    channel.queue_declare(queue=queue_name, durable=True)
    print(" [*] Monitoring dead-letter queue for failed/expired messages")
else:
    # Declare the main queue with dead-letter configuration
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            'x-dead-letter-exchange': "dlx_exchange",
            'x-dead-letter-routing-key': "expired",
            'x-message-ttl': 10000,  # message TTL: 10 seconds
        }
    )
    print(" [*] Monitoring main processing queue")

# Set QoS - only process one message at a time
channel.basic_qos(prefetch_count=1)

# Callback function for processing messages
def callback(ch, method, properties, body):
    message = body.decode()
    
    if queue_type == "dead-letter":
        # Processing dead-lettered messages
        print(f" [x] Dead-letter queue received: {message}")
        print(f" [i] This message was rejected, expired, or exceeded queue limits")
        
        # Always acknowledge dead-letter messages
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # Processing main queue messages
        print(f" [x] Main queue received: {message}")
        
        # Randomly reject some messages to demonstrate dead-lettering
        import random
        if "Will be processed normally" in message and random.random() < 0.3:
            print(" [!] Simulating processing failure (30% chance) - Rejecting message")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        else:
            # Process the message
            print(f" [.] Processing message: {message}")
            time.sleep(1)  # Simulate processing time
            print(" [✓] Successfully processed")
            ch.basic_ack(delivery_tag=method.delivery_tag)

print(f" [*] Waiting for messages on {queue_name}. To exit press CTRL+C")

# Consume messages
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False  # Manual acknowledgment
)

# Start consuming
channel.start_consuming() 