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

# Declare the dead-letter exchange
dlx_exchange = "dlx_exchange"
channel.exchange_declare(exchange=dlx_exchange, exchange_type="direct")

# Declare a queue for dead-lettered messages
dl_queue = "dead_letter_queue"
channel.queue_declare(queue=dl_queue, durable=True)
channel.queue_bind(exchange=dlx_exchange, queue=dl_queue, routing_key="expired")

# Declare main queue with dead-letter configuration
main_queue = "main_processing_queue"
channel.queue_declare(
    queue=main_queue,
    durable=True,
    arguments={
        # Send to DLX when messages are rejected, expired, or max length reached
        'x-dead-letter-exchange': dlx_exchange,  
        'x-dead-letter-routing-key': 'expired',
        'x-message-ttl': 10000,  # message TTL: 10 seconds
    }
)

# Send messages to the main queue
for i in range(5):
    # Some messages will be processed normally
    message = f"Regular message #{i} - Will be processed normally"
    
    # Set message properties
    channel.basic_publish(
        exchange="",
        routing_key=main_queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    
    print(f" [x] Sent message to main queue: '{message}'")
    time.sleep(0.5)

# Send additional messages with short TTL to demonstrate expiration
for i in range(2):
    message = f"Short-lived message #{i} - Will expire in 5 seconds"
    
    # Set message properties with short TTL
    channel.basic_publish(
        exchange="",
        routing_key=main_queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            expiration="5000",  # Override queue TTL with 5 seconds for this message
        )
    )
    
    print(f" [x] Sent short-lived message: '{message}'")
    time.sleep(0.5)

print(" [x] All messages sent")
connection.close() 