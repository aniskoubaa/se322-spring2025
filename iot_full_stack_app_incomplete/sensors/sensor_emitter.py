#!/usr/bin/env python
import pika
import random
import time
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# TODO: Declare exchanges for different routing patterns
# Hint: We need fanout, direct, topic, and headers exchanges


print("Starting IoT sensor emitter... Press CTRL+C to exit")

try:
    while True:
        # TODO: Generate random sensor data
        # Hint: We need temperature (15-40°C), humidity (20-80%), soil_moisture (200-800)

        
        # Create message payload
        timestamp = time.time()
        payload = {
            "timestamp": timestamp,
            # TODO: Add generated sensor data to payload
            
            "device_id": "farm_sensor_01"
        }
        
        message = json.dumps(payload)
        
        # TODO: Check for alert conditions
        # Hint: Alert if temperature > 35 or humidity < 30 or soil_moisture < 250
        
        
        # TODO: Publish to fanout exchange (broadcasts to all consumers)
        
        
        # TODO: Publish to direct exchange (with routing key) only if there's an alert
        
        
        # TODO: Publish to topic exchange with different routing patterns
        # Hint: Use routing keys like 'sensor.temperature', 'sensor.humidity', etc.
        
        
        # TODO: Publish to headers exchange
        # Hint: Use headers like device_type=environment, location=field_1
        
        
        # Print what was sent
        print(f"Sent: {message}")
        
        # Wait for a few seconds before sending the next reading
        time.sleep(random.uniform(2, 5))

except KeyboardInterrupt:
    print("Stopping sensor emitter")
    connection.close() 