#!/usr/bin/env python
import json
from datetime import datetime
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection

# Connect to RabbitMQ using CloudAMQP credentials
connection = get_rabbitmq_connection()
channel = connection.channel()

# Declare the topic exchange
channel.exchange_declare(exchange='sensors.topic', exchange_type='topic')

# Create a queue for analyzing topics
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange with different routing patterns using wildcards
# * (star) substitutes exactly one word
# # (hash) substitutes zero or more words
channel.queue_bind(
    exchange='sensors.topic',
    queue=queue_name,
    routing_key='sensor.*'  # This matches sensor.temperature, sensor.humidity, sensor.soil, etc.
)

# You could also use something like 'sensor.#' to match sensor.temperature.farm1, etc.

print("Topic analyzer started. Demonstrating topic exchange with wildcards.")
print("Subscribed to pattern: sensor.*")
print("To exit press CTRL+C")

def callback(ch, method, properties, body):
    try:
        # Parse the JSON message
        data = json.loads(body)
        
        # Get timestamp and format it
        timestamp = data.get("timestamp", 0)
        datetime_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract the specific sensor type from the routing key
        sensor_type = method.routing_key.split('.')[-1]
        
        # Print the data with routing key information
        print(f"\n[TOPIC: {method.routing_key}]")
        print(f"Time: {datetime_str}")
        
        # Format output based on sensor type
        if sensor_type == 'temperature' and 'temperature' in data:
            print(f"Temperature: {data['temperature']}°C")
        elif sensor_type == 'humidity' and 'humidity' in data:
            print(f"Humidity: {data['humidity']}%")
        elif sensor_type == 'soil' and 'soil_moisture' in data:
            print(f"Soil Moisture: {data['soil_moisture']} units")
        else:
            print(f"Data: {data}")
        
        print("-" * 40)
        
    except json.JSONDecodeError:
        print(f"Error: Could not parse message as JSON: {body}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Start consuming messages
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

# Start consuming
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping topic analyzer")
    channel.stop_consuming()
    
connection.close() 