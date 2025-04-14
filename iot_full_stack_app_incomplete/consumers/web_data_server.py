#!/usr/bin/env python
import pika
import json
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import time

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for the latest sensor data
latest_data = {
    "timestamp": 0,
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 0,
    "alerts": []
}

# Define thresholds for alerts (same as in alert_handler.py)
THRESHOLDS = {
    "temperature": {"min": 0, "max": 35, "unit": "°C"},
    "humidity": {"min": 30, "max": 100, "unit": "%"},
    "soil_moisture": {"min": 250, "max": 800, "unit": "units"}
}

# TODO: Implement function to check if values are in alert range


# Function to handle RabbitMQ connection
def start_rabbitmq_consumer():
    try:
        # TODO: Connect to RabbitMQ
        
        
        # TODO: Declare the fanout exchange
        
        
        # TODO: Create a temporary queue and bind it to the exchange
        
        
        print("Web data server started. Waiting for sensor data...")
        
        # Define callback function for received messages
        def callback(ch, method, properties, body):
            try:
                # TODO: Parse the JSON message
                
                
                # TODO: Update the latest data
                
                
                # TODO: Calculate alerts
                
                
                print(f"Received data for web: {data}")
                
            except json.JSONDecodeError:
                print(f"Error: Could not parse message as JSON: {body}")
            except Exception as e:
                print(f"Error processing message: {e}")
        
        # TODO: Start consuming messages
        
        
        # Start consuming in a blocking way
        channel.start_consuming()
    
    except Exception as e:
        print(f"RabbitMQ consumer error: {e}")
        time.sleep(5)  # Wait before reconnecting
        start_rabbitmq_consumer()  # Try to reconnect

# TODO: Create API route to get the latest data


# Start RabbitMQ consumer in a separate thread
rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer)
rabbitmq_thread.daemon = True  # Thread will exit when the main program exits
rabbitmq_thread.start()

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 