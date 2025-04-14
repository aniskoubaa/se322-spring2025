#!/usr/bin/env python
import pika
import json
from datetime import datetime

# TODO: Connect to RabbitMQ


# TODO: Declare the topic exchange


# TODO: Create a queue for analyzing topics


# TODO: Bind the queue to the exchange with wildcards
# Hint: Use routing_key='sensor.*' to match sensor.temperature, sensor.humidity, etc.
# * (star) substitutes exactly one word
# # (hash) substitutes zero or more words


print("Topic analyzer started. Demonstrating topic exchange with wildcards.")
print("Subscribed to pattern: sensor.*")
print("To exit press CTRL+C")

def callback(ch, method, properties, body):
    try:
        # TODO: Parse the JSON message
        
        
        # TODO: Get timestamp and format it
        
        
        # TODO: Extract the specific sensor type from the routing key
        # Hint: Use routing_key.split('.')[-1] to get the last part of sensor.temperature
        
        
        # TODO: Print the data with routing key information
        
        
        # TODO: Format output based on sensor type
        # Hint: Check if sensor_type is 'temperature', 'humidity', or 'soil'
        
        pass
    except json.JSONDecodeError:
        print(f"Error: Could not parse message as JSON: {body}")
    except Exception as e:
        print(f"Error processing message: {e}")

# TODO: Start consuming messages


# Start consuming
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping topic analyzer")
    channel.stop_consuming()
    
connection.close() 