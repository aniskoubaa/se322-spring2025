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

# Declare a topic exchange
exchange_name = "topic_exchange"
channel.exchange_declare(exchange=exchange_name, exchange_type="topic")

# Sample IoT device data with hierarchical routing keys
devices = ["sensor", "actuator", "camera"]
locations = ["livingroom", "kitchen", "bedroom", "bathroom"]
events = ["data", "status", "alert"]

# Send messages with different topic patterns
for i in range(15):
    # Generate a random topic
    device = random.choice(devices)
    location = random.choice(locations)
    event = random.choice(events)
    
    # Create routing key in format: device.location.event
    routing_key = f"{device}.{location}.{event}"
    
    # Create message content based on the routing key
    if event == "data":
        message = f"Reading: {random.randint(0, 100)}"
    elif event == "status":
        status = random.choice(["online", "offline", "standby"])
        message = f"Status: {status}"
    else:  # alert
        message = f"Alert: {random.choice(['motion detected', 'high temperature', 'low battery'])}"
    
    # Publish the message
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=message
    )
    
    print(f" [x] Sent {routing_key}: '{message}'")
    time.sleep(0.5)

connection.close()
print(" [x] Done sending messages") 