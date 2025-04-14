#!/usr/bin/env python
import pika
import json
import os
from datetime import datetime

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Create or open data log file (CSV format)
data_file = os.path.join("data", "sensor_data.csv")
file_exists = os.path.isfile(data_file)

with open(data_file, "a") as f:
    # Write CSV header if file is new
    if not file_exists:
        f.write("timestamp,datetime,temperature,humidity,soil_moisture,device_id\n")

# TODO: Connect to RabbitMQ


# TODO: Declare the fanout exchange


# TODO: Create a temporary queue with a random name


# TODO: Bind the queue to the exchange


print("Waiting for sensor data. To exit press CTRL+C")

def callback(ch, method, properties, body):
    try:
        # TODO: Parse the JSON message
        
        
        # TODO: Convert Unix timestamp to readable datetime
        
        
        # Print received data
        print(f"Received: {data}")
        
        # TODO: Log data to CSV file
        
            
    except json.JSONDecodeError:
        print(f"Error: Could not parse message as JSON: {body}")
    except Exception as e:
        print(f"Error processing message: {e}")

# TODO: Start consuming messages


# Start consuming
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping data logger")
    channel.stop_consuming()
    
connection.close() 