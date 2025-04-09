import pika
import os
import time
import random
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

# Sample message types with different headers
message_types = [
    {
        "headers": {"device_type": "sensor", "location": "indoor", "priority": "high"},
        "body": "High priority indoor sensor reading"
    },
    {
        "headers": {"device_type": "sensor", "location": "outdoor", "priority": "low"},
        "body": "Low priority outdoor sensor reading"
    },
    {
        "headers": {"device_type": "actuator", "location": "indoor", "priority": "high"},
        "body": "High priority indoor actuator command"
    },
    {
        "headers": {"device_type": "gateway", "location": "indoor", "data_format": "json"},
        "body": '{"temperature": 23.5, "humidity": 45}'
    },
    {
        "headers": {"device_type": "gateway", "location": "outdoor", "data_format": "binary"},
        "body": "Binary data payload simulation"
    }
]

# Send messages with different headers
for _ in range(10):
    # Pick a random message type
    message = random.choice(message_types)
    
    # Publish the message with headers
    channel.basic_publish(
        exchange=exchange_name,
        routing_key="",  # not used for headers exchange
        properties=pika.BasicProperties(
            headers=message["headers"]
        ),
        body=message["body"]
    )
    
    print(f" [x] Sent message with headers: {message['headers']}")
    print(f"     Body: {message['body']}")
    time.sleep(0.5)

connection.close()
print(" [x] Done sending messages") 