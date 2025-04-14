#!/usr/bin/env python
import pika
import json
from datetime import datetime

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the direct exchange for alerts
channel.exchange_declare(exchange='sensors.direct', exchange_type='direct')

# Create a queue for alerts
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange with the 'alerts' routing key
channel.queue_bind(
    exchange='sensors.direct',
    queue=queue_name,
    routing_key='alerts'
)

print("Alert handler started. Waiting for abnormal sensor values. To exit press CTRL+C")

# Define thresholds for alerts
THRESHOLDS = {
    "temperature": {"min": 0, "max": 35, "unit": "°C"},
    "humidity": {"min": 30, "max": 100, "unit": "%"},
    "soil_moisture": {"min": 250, "max": 800, "unit": "units"}
}

def callback(ch, method, properties, body):
    try:
        # Parse the JSON message
        data = json.loads(body)
        
        # Get timestamp and format it
        timestamp = data.get("timestamp", 0)
        datetime_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Check all values against thresholds
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
        
        # Print alerts if any were found
        if alerts:
            print("\n" + "!" * 50)
            print(f"ALERT at {datetime_str}:")
            for alert in alerts:
                print(f"* {alert}")
            print("!" * 50 + "\n")
        
    except json.JSONDecodeError:
        print(f"Error: Could not parse message as JSON: {body}")
    except Exception as e:
        print(f"Error processing alert: {e}")

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
    print("Stopping alert handler")
    channel.stop_consuming()
    
connection.close() 