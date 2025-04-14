#!/usr/bin/env python
import pika
import random
import time
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare exchanges for different routing patterns
channel.exchange_declare(exchange='sensors.fanout', exchange_type='fanout')
channel.exchange_declare(exchange='sensors.direct', exchange_type='direct')
channel.exchange_declare(exchange='sensors.topic', exchange_type='topic')
channel.exchange_declare(exchange='sensors.headers', exchange_type='headers')

print("Starting IoT sensor emitter... Press CTRL+C to exit")

try:
    while True:
        # Generate random sensor data
        temperature = round(random.uniform(15, 40), 1)  # Temperature in °C
        humidity = round(random.uniform(20, 80), 1)     # Humidity in %
        soil_moisture = round(random.uniform(200, 800)) # Soil moisture (arbitrary units)
        
        # Create message payload
        timestamp = time.time()
        payload = {
            "timestamp": timestamp,
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture,
            "device_id": "farm_sensor_01"
        }
        
        message = json.dumps(payload)
        
        # Check for alert conditions
        alert = temperature > 35 or humidity < 30 or soil_moisture < 250
        
        # Publish to fanout exchange (broadcasts to all consumers)
        channel.basic_publish(
            exchange='sensors.fanout',
            routing_key='',
            body=message
        )
        
        # Publish to direct exchange (with routing key)
        if alert:
            channel.basic_publish(
                exchange='sensors.direct',
                routing_key='alerts',
                body=message
            )
        
        # Publish to topic exchange (with routing patterns)
        channel.basic_publish(
            exchange='sensors.topic',
            routing_key='sensor.temperature',
            body=json.dumps({"temperature": temperature, "timestamp": timestamp})
        )
        
        channel.basic_publish(
            exchange='sensors.topic',
            routing_key='sensor.humidity',
            body=json.dumps({"humidity": humidity, "timestamp": timestamp})
        )
        
        channel.basic_publish(
            exchange='sensors.topic',
            routing_key='sensor.soil',
            body=json.dumps({"soil_moisture": soil_moisture, "timestamp": timestamp})
        )
        
        # Publish to headers exchange
        channel.basic_publish(
            exchange='sensors.headers',
            routing_key='',
            properties=pika.BasicProperties(
                headers={'device_type': 'environment', 'location': 'field_1'}
            ),
            body=message
        )
        
        # Print what was sent
        print(f"Sent: {message}")
        
        # Wait for a few seconds before sending the next reading
        time.sleep(random.uniform(2, 5))

except KeyboardInterrupt:
    print("Stopping sensor emitter")
    connection.close() 