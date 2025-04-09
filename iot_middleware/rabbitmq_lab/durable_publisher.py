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

# Declare a durable queue
queue_name = "durable_queue"
channel.queue_declare(queue=queue_name, durable=True)

# Send a series of important messages that should survive broker restarts
for i in range(5):
    message = f"Critical message #{i} - Should persist even if broker restarts"
    
    # Mark message as persistent - delivery_mode=2
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            priority=10,      # Higher priority
            timestamp=int(time.time()),
            content_type="text/plain",
            headers={"message_type": "critical"}
        )
    )
    
    print(f" [x] Sent persistent message: '{message}'")
    time.sleep(0.5)

print(" [x] All critical messages sent")
connection.close() 