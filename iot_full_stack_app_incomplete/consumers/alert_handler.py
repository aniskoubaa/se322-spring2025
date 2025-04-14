#!/usr/bin/env python
import pika
import json
from datetime import datetime

# TODO: Connect to RabbitMQ


# TODO: Declare the direct exchange for alerts


# TODO: Create a queue for alerts


# TODO: Bind the queue to the exchange with the 'alerts' routing key


print("Alert handler started. Waiting for abnormal sensor values. To exit press CTRL+C")

# Define thresholds for alerts
THRESHOLDS = {
    "temperature": {"min": 0, "max": 35, "unit": "°C"},
    "humidity": {"min": 30, "max": 100, "unit": "%"},
    "soil_moisture": {"min": 250, "max": 800, "unit": "units"}
}

def callback(ch, method, properties, body):
    try:
        # TODO: Parse the JSON message
        
        
        # TODO: Get timestamp and format it
        
        
        # Check all values against thresholds
        alerts = []
        
        # TODO: Check temperature
        
        
        # TODO: Check humidity
        
        
        # TODO: Check soil moisture
        
        
        # TODO: Print alerts if any were found
        
        
    except json.JSONDecodeError:
        print(f"Error: Could not parse message as JSON: {body}")
    except Exception as e:
        print(f"Error processing alert: {e}")

# TODO: Start consuming messages


# Start consuming
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping alert handler")
    channel.stop_consuming()
    
connection.close() 