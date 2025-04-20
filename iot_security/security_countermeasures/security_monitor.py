#!/usr/bin/env python
"""
Security Monitor

This tool monitors for suspicious activities and logs security events.
It demonstrates how to detect various security threats in an IoT system.
"""

import json
import sys
import os
import time
import threading
from datetime import datetime
from colorama import init, Fore, Style

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
from security_utils import verify_signature, is_message_recent

# Initialize colorama for colored terminal output
init()

# Security log file
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                       'data', 'security_events.log')

# Connect to RabbitMQ using CloudAMQP credentials
print(f"{Fore.BLUE}[SECURITY MONITOR] {Fore.CYAN}Connecting to RabbitMQ...{Style.RESET_ALL}")
try:
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    print(f"{Fore.GREEN}[SECURITY MONITOR] Connected successfully!{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[SECURITY MONITOR] Connection failed: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Declare and listen to all exchanges to detect tampering
exchanges = [
    {'name': 'sensors.fanout', 'type': 'fanout', 'routing_key': '', 'secure': False},
    {'name': 'sensors.direct', 'type': 'direct', 'routing_key': '#', 'secure': False},
    {'name': 'sensors.topic', 'type': 'topic', 'routing_key': '#', 'secure': False},
    {'name': 'sensors.secure.fanout', 'type': 'fanout', 'routing_key': '', 'secure': True},
    {'name': 'sensors.secure.direct', 'type': 'direct', 'routing_key': '#', 'secure': True},
    {'name': 'sensors.secure.topic', 'type': 'topic', 'routing_key': '#', 'secure': True},
    # Also listen for mitm exchanges
    {'name': 'mitm.fanout', 'type': 'fanout', 'routing_key': '', 'secure': False},
    {'name': 'mitm.direct', 'type': 'direct', 'routing_key': '#', 'secure': False},
]

# Dictionary to store message history for anomaly detection
message_history = {
    'farm_sensor_01': {
        'last_values': [],
        'last_timestamp': 0,
        'message_count': 0
    }
}

# List of detected security events
security_events = []

def log_security_event(event_type, details):
    """Log a security event to file and console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create event object
    event = {
        'timestamp': timestamp,
        'event_type': event_type,
        'details': details
    }
    
    # Add to events list
    security_events.append(event)
    
    # Log to console
    print(f"{Fore.RED}[SECURITY EVENT] {event_type}: {details}{Style.RESET_ALL}")
    
    # Log to file
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"{timestamp} - {event_type}: {details}\n")
    except Exception as e:
        print(f"{Fore.RED}[SECURITY MONITOR] Error writing to log file: {e}{Style.RESET_ALL}")

def check_for_tampering(message, device_id):
    """Check if message values have been tampered with."""
    if device_id not in message_history:
        message_history[device_id] = {
            'last_values': [],
            'last_timestamp': 0,
            'message_count': 0
        }
    
    device_history = message_history[device_id]
    
    # First few messages, just store history
    if device_history['message_count'] < 3:
        if 'temperature' in message:
            device_history['last_values'].append({
                'temperature': message['temperature'],
                'timestamp': message.get('timestamp', time.time())
            })
        device_history['message_count'] += 1
        return False
    
    # Check for suspicious changes in values
    if 'temperature' in message:
        temp = message['temperature']
        
        # Calculate average and standard deviation of previous values
        prev_temps = [item['temperature'] for item in device_history['last_values']]
        avg_temp = sum(prev_temps) / len(prev_temps)
        
        # Check for rapid, unusual change
        if abs(temp - avg_temp) > 10:
            details = f"Suspicious temperature change detected: {avg_temp} -> {temp}"
            log_security_event('ANOMALY_DETECTION', details)
            return True
        
        # Update history (keep last 3 values)
        device_history['last_values'].append({
            'temperature': temp,
            'timestamp': message.get('timestamp', time.time())
        })
        if len(device_history['last_values']) > 3:
            device_history['last_values'].pop(0)
    
    # Check for timestamp anomalies
    if 'timestamp' in message:
        # Check if timestamp is in the future
        if message['timestamp'] > time.time() + 5:  # Allow 5 seconds clock skew
            details = f"Message with future timestamp received: {message['timestamp']}"
            log_security_event('TIMESTAMP_ANOMALY', details)
            return True
        
        # Check for timestamp going backward by more than allowed skew
        if device_history['last_timestamp'] > 0 and message['timestamp'] < device_history['last_timestamp'] - 5:
            details = f"Message with past timestamp received: {message['timestamp']} (prev: {device_history['last_timestamp']})"
            log_security_event('TIMESTAMP_ANOMALY', details)
            return True
        
        device_history['last_timestamp'] = message['timestamp']
    
    device_history['message_count'] += 1
    return False

def create_callback(exchange_info):
    """Create a callback function for each exchange."""
    def callback(ch, method, properties, body):
        try:
            # Parse the message
            data = json.loads(body)
            
            # Check if this is a secure exchange
            is_secure = exchange_info['secure']
            exchange_name = exchange_info['name']
            
            # Special check for mitm exchanges
            if exchange_name.startswith('mitm.'):
                details = f"Detected message on MITM exchange: {exchange_name}"
                log_security_event('MITM_ATTACK_DETECTED', details)
                return
            
            # Basic logging
            print(f"{Fore.BLUE}[SECURITY MONITOR] Received message on {exchange_name}")
            
            # Check for suspicious activities
            # 1. Check for unsigned messages on secure exchanges
            if is_secure and 'signature' not in data:
                details = f"Unsigned message on secure exchange {exchange_name}"
                log_security_event('UNSIGNED_MESSAGE', details)
            
            # 2. Check signature validity for signed messages
            if 'signature' in data:
                is_valid = verify_signature(data)
                if not is_valid:
                    details = f"Invalid signature detected on {exchange_name}"
                    log_security_event('INVALID_SIGNATURE', details)
            
            # 3. Check message recency for signed messages
            if 'signature' in data and 'timestamp' in data:
                is_recent = is_message_recent(data, max_age_seconds=60)
                if not is_recent:
                    details = f"Message replay detected on {exchange_name}: {data['timestamp']}"
                    log_security_event('MESSAGE_REPLAY', details)
            
            # 4. Check for value tampering
            if 'device_id' in data:
                was_tampered = check_for_tampering(data, data['device_id'])
                if was_tampered:
                    print(f"{Fore.YELLOW}[SECURITY MONITOR] Possible tampering detected for device {data['device_id']}{Style.RESET_ALL}")
            
            # 5. Check for unauthorized command
            if 'command' in data and 'device_id' in data:
                if data.get('device_id') != 'admin_device':
                    details = f"Unauthorized command detected from {data.get('device_id')}: {data.get('command')}"
                    log_security_event('UNAUTHORIZED_COMMAND', details)
                
                if 'signature' not in data or not verify_signature(data):
                    details = f"Unsigned or invalidly signed command detected: {data.get('command')}"
                    log_security_event('UNSIGNED_COMMAND', details)
            
        except json.JSONDecodeError:
            print(f"{Fore.RED}[SECURITY MONITOR] Could not parse message as JSON: {body}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[SECURITY MONITOR] Error processing message: {e}{Style.RESET_ALL}")
    
    return callback

# Start consuming messages from all exchanges
for exchange_info in exchanges:
    try:
        # Declare the exchange
        channel.exchange_declare(exchange=exchange_info['name'], exchange_type=exchange_info['type'])
        
        # Create a queue for this exchange
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Bind the queue to the exchange
        channel.queue_bind(
            exchange=exchange_info['name'],
            queue=queue_name,
            routing_key=exchange_info['routing_key']
        )
        
        print(f"{Fore.GREEN}[SECURITY MONITOR] Monitoring {exchange_info['name']} exchange{Style.RESET_ALL}")
        
        # Start consuming messages from this queue
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=create_callback(exchange_info),
            auto_ack=True
        )
        
    except Exception as e:
        print(f"{Fore.RED}[SECURITY MONITOR] Error setting up monitoring for {exchange_info['name']}: {e}{Style.RESET_ALL}")

# Function to periodically show security stats
def show_security_stats():
    while True:
        time.sleep(30)
        # Print summary of security events
        if security_events:
            print(f"{Fore.CYAN}[SECURITY MONITOR] Security Events Summary: {len(security_events)} events detected{Style.RESET_ALL}")
            # Count events by type
            event_counts = {}
            for event in security_events:
                event_type = event['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            for event_type, count in event_counts.items():
                print(f"{Fore.CYAN}  - {event_type}: {count} occurrences{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[SECURITY MONITOR] No security events detected in the last interval{Style.RESET_ALL}")

# Start the stats thread
stats_thread = threading.Thread(target=show_security_stats)
stats_thread.daemon = True
stats_thread.start()

print(f"{Fore.GREEN}[SECURITY MONITOR] Security monitoring active{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Press Ctrl+C to exit{Style.RESET_ALL}")

try:
    # Start consuming messages
    channel.start_consuming()
except KeyboardInterrupt:
    print(f"{Fore.BLUE}[SECURITY MONITOR] Stopping security monitor{Style.RESET_ALL}")
    channel.stop_consuming()
    
connection.close() 