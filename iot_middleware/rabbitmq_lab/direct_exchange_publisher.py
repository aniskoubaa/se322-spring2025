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

# Declare a direct exchange
exchange_name = "direct_exchange"
channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

# Available severity levels
severities = ["info", "warning", "error", "critical"]

# Send messages with different severity levels
for i in range(10):
    # Pick a random severity
    severity = random.choice(severities)
    message = f"Message #{i}: This is a {severity} level message"
    
    # Use severity as routing key
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=severity,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    
    print(f" [x] Sent '{severity}': '{message}'")
    time.sleep(0.5)

connection.close()
print(" [x] Done sending messages") 