#!/usr/bin/env python
import json
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import time
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
import pika

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

# Check if values are in alert range
def check_alerts(data):
    alerts = []
    
    # Check temperature
    if "temperature" in data:
        temp = data["temperature"]
        if temp > THRESHOLDS["temperature"]["max"]:
            alerts.append(f"HIGH TEMPERATURE: {temp}{THRESHOLDS['temperature']['unit']}")
        elif temp < THRESHOLDS["temperature"]["min"]:
            alerts.append(f"LOW TEMPERATURE: {temp}{THRESHOLDS['temperature']['unit']}")
    
    # Check humidity
    if "humidity" in data:
        humid = data["humidity"]
        if humid < THRESHOLDS["humidity"]["min"]:
            alerts.append(f"LOW HUMIDITY: {humid}{THRESHOLDS['humidity']['unit']}")
        elif humid > THRESHOLDS["humidity"]["max"]:
            alerts.append(f"HIGH HUMIDITY: {humid}{THRESHOLDS['humidity']['unit']}")
    
    # Check soil moisture
    if "soil_moisture" in data:
        moisture = data["soil_moisture"]
        if moisture < THRESHOLDS["soil_moisture"]["min"]:
            alerts.append(f"LOW SOIL MOISTURE: {moisture}{THRESHOLDS['soil_moisture']['unit']}")
        elif moisture > THRESHOLDS["soil_moisture"]["max"]:
            alerts.append(f"HIGH SOIL MOISTURE: {moisture}{THRESHOLDS['soil_moisture']['unit']}")
    
    return alerts


# Function to handle RabbitMQ connection
def start_rabbitmq_consumer():
    try:
        # Connect to RabbitMQ using CloudAMQP credentials
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare the fanout exchange
        channel.exchange_declare(exchange='sensors.fanout', exchange_type='fanout')
        
        # Create a temporary queue
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Bind the queue to the exchange
        channel.queue_bind(exchange='sensors.fanout', queue=queue_name)
        
        print("Web data server started. Waiting for sensor data...")
        
        # Define callback function for received messages
        def callback(ch, method, properties, body):
            try:
                # Parse the JSON message
                data = json.loads(body)
                print(type(data))#dict
                
                # Update the latest data
                global latest_data
                latest_data.update(data)
                
                # Calculate alerts
                latest_data["alerts"] = check_alerts(data)
                
                print(f"Received data for web: {data}")
                
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
        
        # Start consuming in a blocking way
        channel.start_consuming()
    
    except Exception as e:
        print(f"RabbitMQ consumer error: {e}")
        time.sleep(5)  # Wait before reconnecting
        start_rabbitmq_consumer()  # Try to reconnect

# API route to get the latest data
@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    return jsonify(latest_data)

# Start RabbitMQ consumer in a separate thread
rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer)
rabbitmq_thread.daemon = True  # Thread will exit when the main program exits
rabbitmq_thread.start()

# Run the Flask app
if __name__ == '__main__':
    # Change port from 5000 to 5001 to avoid conflicts
    app.run(host='0.0.0.0', port=5001, debug=True) 