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

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the fanout exchange
channel.exchange_declare(exchange='sensors.fanout', exchange_type='fanout')

# Create a temporary queue with a random name
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange
channel.queue_bind(exchange='sensors.fanout', queue=queue_name)

print("Waiting for sensor data. To exit press CTRL+C")

def callback(ch, method, properties, body):
    try:
        # Parse the JSON message
        data = json.loads(body)
        timestamp = data.get("timestamp", 0)
        
        # Convert Unix timestamp to readable datetime
        datetime_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Print received data
        print(f"Received: {data}")
        
        # Log data to CSV file
        with open(data_file, "a") as f:
            f.write(f"{timestamp},{datetime_str},{data.get('temperature', '')},{data.get('humidity', '')},{data.get('soil_moisture', '')},{data.get('device_id', '')}\n")
            
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
    print("Stopping data logger")
    channel.stop_consuming()
    
connection.close() 