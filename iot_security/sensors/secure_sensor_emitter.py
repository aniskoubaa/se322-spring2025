#!/usr/bin/env python
import random
import time
import json
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
from security_utils import sign_message, encrypt_message
import pika

# Device ID for this sensor
DEVICE_ID = "farm_sensor_01"

# Connect to RabbitMQ using CloudAMQP credentials
connection = get_rabbitmq_connection()
channel = connection.channel()

# Declare exchanges for different routing patterns
channel.exchange_declare(exchange='sensors.fanout', exchange_type='fanout')
channel.exchange_declare(exchange='sensors.direct', exchange_type='direct')
channel.exchange_declare(exchange='sensors.topic', exchange_type='topic')
channel.exchange_declare(exchange='sensors.headers', exchange_type='headers')

# Declare secure exchanges with the same patterns
channel.exchange_declare(exchange='sensors.secure.fanout', exchange_type='fanout')
channel.exchange_declare(exchange='sensors.secure.direct', exchange_type='direct')
channel.exchange_declare(exchange='sensors.secure.topic', exchange_type='topic')
channel.exchange_declare(exchange='sensors.secure.headers', exchange_type='headers')

print("Starting secure IoT sensor emitter... Press CTRL+C to exit")

def generate_sensor_data():
    """Generate random sensor data."""
    temperature = round(random.uniform(15, 40), 1)  # Temperature in °C
    humidity = round(random.uniform(20, 80), 1)     # Humidity in %
    soil_moisture = round(random.uniform(200, 800)) # Soil moisture (arbitrary units)
    
    # Create message payload
    timestamp = time.time()
    data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "device_id": DEVICE_ID
    }
    
    return data, temperature > 35 or humidity < 30 or soil_moisture < 250

try:
    while True:
        # Generate random sensor data
        payload, is_alert = generate_sensor_data()
        
        # Create regular JSON message (insecure)
        regular_message = json.dumps(payload)
        
        # Create signed message (secure)
        signed_payload = sign_message(payload, DEVICE_ID)
        signed_message = json.dumps(signed_payload)
        
        # Create encrypted+signed message (most secure)
        encrypted_payload = encrypt_message(signed_payload)
        encrypted_message = json.dumps(encrypted_payload)
        
        # ---------- INSECURE PUBLISHING ----------
        # Publish to regular fanout exchange (broadcasts to all consumers)
        channel.basic_publish(
            exchange='sensors.fanout',
            routing_key='',
            body=regular_message
        )
        
        # Regular direct exchange for alerts
        if is_alert:
            channel.basic_publish(
                exchange='sensors.direct',
                routing_key='alerts',
                body=regular_message
            )
        
        # ---------- SECURE PUBLISHING ----------
        # Publish signed data to secure fanout exchange
        channel.basic_publish(
            exchange='sensors.secure.fanout',
            routing_key='',
            body=signed_message
        )
        
        # Secure direct exchange for alerts
        if is_alert:
            channel.basic_publish(
                exchange='sensors.secure.direct',
                routing_key='alerts',
                body=signed_message
            )
        
        # Secure topic exchange with encrypted + signed message for high security
        channel.basic_publish(
            exchange='sensors.secure.topic',
            routing_key='secure.sensor.all',
            body=encrypted_message
        )
        
        # Print what was sent
        print(f"Sent regular data: {regular_message}")
        print(f"Sent secure data with signature")
        print(f"Sent encrypted data to high-security consumers")
        
        # Wait before sending the next reading
        time.sleep(random.uniform(2, 5))

except KeyboardInterrupt:
    print("Stopping secure sensor emitter")
    connection.close() 