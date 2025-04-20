#!/usr/bin/env python
import json
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
from security_utils import verify_signature, decrypt_message, is_message_recent
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
    "alerts": [],
    "security_status": {
        "is_authenticated": False,
        "last_verified_timestamp": 0,
        "message_integrity": "unknown"
    }
}

# Define thresholds for alerts
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

# Function to handle RabbitMQ connection and secure message processing
def start_rabbitmq_consumer():
    try:
        # Connect to RabbitMQ using CloudAMQP credentials
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare the secure fanout exchange
        channel.exchange_declare(exchange='sensors.secure.fanout', exchange_type='fanout')
        
        # Create a temporary queue for secure messages
        result = channel.queue_declare(queue='', exclusive=True)
        secure_queue_name = result.method.queue
        
        # Bind the queue to the secure exchange
        channel.queue_bind(exchange='sensors.secure.fanout', queue=secure_queue_name)
        
        # Also declare the insecure exchange for demonstration
        channel.exchange_declare(exchange='sensors.fanout', exchange_type='fanout')
        
        # Create a temporary queue for insecure messages
        result = channel.queue_declare(queue='', exclusive=True)
        insecure_queue_name = result.method.queue
        
        # Bind the queue to the insecure exchange
        channel.queue_bind(exchange='sensors.fanout', queue=insecure_queue_name)
        
        # Declare the secure topic exchange for encrypted messages
        channel.exchange_declare(exchange='sensors.secure.topic', exchange_type='topic')
        
        # Create a queue for encrypted messages
        result = channel.queue_declare(queue='', exclusive=True)
        encrypted_queue_name = result.method.queue
        
        # Bind the queue to the secure topic exchange
        channel.queue_bind(
            exchange='sensors.secure.topic',
            queue=encrypted_queue_name,
            routing_key='secure.sensor.all'
        )
        
        print("Secure web data server started. Waiting for sensor data...")
        
        # Define callback function for secure signed messages
        def secure_callback(ch, method, properties, body):
            try:
                # Parse the JSON message
                data = json.loads(body)
                
                # Verify the message signature
                is_valid = verify_signature(data)
                is_recent = is_message_recent(data, max_age_seconds=60)
                
                if is_valid and is_recent:
                    # Update the latest data
                    global latest_data
                    latest_data.update({
                        "timestamp": data["timestamp"],
                        "temperature": data["temperature"],
                        "humidity": data["humidity"],
                        "soil_moisture": data["soil_moisture"],
                        "device_id": data["device_id"],
                        "security_status": {
                            "is_authenticated": True,
                            "last_verified_timestamp": time.time(),
                            "message_integrity": "verified"
                        }
                    })
                    
                    # Calculate alerts
                    latest_data["alerts"] = check_alerts(data)
                    
                    print(f"Received authenticated data: {data}")
                else:
                    print(f"Warning: Received message with invalid signature or outdated timestamp")
                    latest_data["security_status"]["message_integrity"] = "invalid"
                    
                    # For educational purposes, we'll log the attempt
                    security_alert = "SECURITY ALERT: Invalid signature detected"
                    if not is_recent:
                        security_alert = "SECURITY ALERT: Message replay attempt detected"
                    
                    latest_data["alerts"].append(security_alert)
                
            except json.JSONDecodeError:
                print(f"Error: Could not parse message as JSON: {body}")
            except Exception as e:
                print(f"Error processing secure message: {e}")
        
        # Define callback function for insecure messages
        def insecure_callback(ch, method, properties, body):
            try:
                # Parse the JSON message
                data = json.loads(body)
                
                # For the insecure channel, we'll accept the data but mark it as unauthenticated
                print(f"Received unauthenticated data: {data}")
                
                # Only update data if we don't have authenticated data
                global latest_data
                if latest_data["security_status"]["is_authenticated"] == False:
                    latest_data.update({
                        "timestamp": data["timestamp"],
                        "temperature": data["temperature"],
                        "humidity": data["humidity"],
                        "soil_moisture": data["soil_moisture"],
                        "device_id": data.get("device_id", "unknown"),
                        "security_status": {
                            "is_authenticated": False,
                            "last_verified_timestamp": 0,
                            "message_integrity": "unverified"
                        }
                    })
                    
                    # Calculate alerts
                    latest_data["alerts"] = check_alerts(data)
                
            except json.JSONDecodeError:
                print(f"Error: Could not parse message as JSON: {body}")
            except Exception as e:
                print(f"Error processing insecure message: {e}")
        
        # Define callback function for encrypted messages
        def encrypted_callback(ch, method, properties, body):
            try:
                # Parse the JSON message
                encrypted_data = json.loads(body)
                
                # Check if it's actually encrypted
                if not encrypted_data.get("is_encrypted", False):
                    print("Received unencrypted message on encrypted channel - ignoring")
                    return
                
                # Decrypt the message
                try:
                    decrypted_data = decrypt_message(encrypted_data)
                    
                    # Verify the decrypted message signature
                    is_valid = verify_signature(decrypted_data)
                    is_recent = is_message_recent(decrypted_data, max_age_seconds=60)
                    
                    if is_valid and is_recent:
                        # Update the latest data
                        global latest_data
                        latest_data.update({
                            "timestamp": decrypted_data["timestamp"],
                            "temperature": decrypted_data["temperature"],
                            "humidity": decrypted_data["humidity"],
                            "soil_moisture": decrypted_data["soil_moisture"],
                            "device_id": decrypted_data["device_id"],
                            "security_status": {
                                "is_authenticated": True,
                                "last_verified_timestamp": time.time(),
                                "message_integrity": "verified_encrypted"
                            }
                        })
                        
                        # Calculate alerts
                        latest_data["alerts"] = check_alerts(decrypted_data)
                        
                        print(f"Received authenticated and encrypted data")
                    else:
                        print(f"Warning: Decrypted message has invalid signature or is outdated")
                        
                except Exception as e:
                    print(f"Error decrypting message: {e}")
                    latest_data["security_status"]["message_integrity"] = "decryption_failed"
                    latest_data["alerts"].append("SECURITY ALERT: Decryption failed, possible tampering")
                
            except json.JSONDecodeError:
                print(f"Error: Could not parse encrypted message as JSON: {body}")
            except Exception as e:
                print(f"Error processing encrypted message: {e}")
        
        # Start consuming secure messages
        channel.basic_consume(
            queue=secure_queue_name,
            on_message_callback=secure_callback,
            auto_ack=True
        )
        
        # Start consuming insecure messages
        channel.basic_consume(
            queue=insecure_queue_name,
            on_message_callback=insecure_callback,
            auto_ack=True
        )
        
        # Start consuming encrypted messages
        channel.basic_consume(
            queue=encrypted_queue_name,
            on_message_callback=encrypted_callback,
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

# API route for admin access (demonstration purposes)
@app.route('/api/admin/reset-security', methods=['POST'])
def reset_security():
    auth_token = request.headers.get('Authorization')
    
    # Very simple authorization demo - in a real system, use proper authentication
    if auth_token != 'Bearer admin_secret_token':
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid or missing authorization token'
        }), 401
    
    # Reset security status
    latest_data['security_status'] = {
        "is_authenticated": False,
        "last_verified_timestamp": 0,
        "message_integrity": "reset"
    }
    
    return jsonify({
        'success': True,
        'message': 'Security status reset successfully'
    })

# Start RabbitMQ consumer in a separate thread
rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer)
rabbitmq_thread.daemon = True  # Thread will exit when the main program exits
rabbitmq_thread.start()

# Run the Flask app
if __name__ == '__main__':
    # Change port from 5000 to 5001 to avoid conflicts
    app.run(host='0.0.0.0', port=5001, debug=True) 