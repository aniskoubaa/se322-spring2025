#!/usr/bin/env python
"""
Message Sniffer - Eavesdropping Attack Simulation

This script demonstrates how an attacker can passively listen to messages 
sent over an unencrypted RabbitMQ connection.

Educational purposes only - demonstrates why encryption is important.
"""

import json
import sys
import os
import time
from colorama import init, Fore, Style

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
from security_utils import decrypt_message

# Initialize colorama for colored terminal output
init()

# Connect to RabbitMQ using CloudAMQP credentials
print(f"{Fore.RED}[ATTACK SIMULATION] {Fore.YELLOW}Connecting to RabbitMQ to sniff messages...{Style.RESET_ALL}")
try:
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    print(f"{Fore.GREEN}[ATTACK SIMULATION] Connected successfully!{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[ATTACK SIMULATION] Connection failed: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Create queues and bind to all exchanges to intercept messages
print(f"{Fore.YELLOW}[ATTACK SIMULATION] Setting up sniffers on all exchanges...{Style.RESET_ALL}")

# List of exchanges to monitor (both secure and insecure)
exchanges = [
    {'name': 'sensors.fanout', 'type': 'fanout', 'routing_key': ''},
    {'name': 'sensors.direct', 'type': 'direct', 'routing_key': 'alerts'},
    {'name': 'sensors.topic', 'type': 'topic', 'routing_key': '#'},
    {'name': 'sensors.secure.fanout', 'type': 'fanout', 'routing_key': ''},
    {'name': 'sensors.secure.direct', 'type': 'direct', 'routing_key': 'alerts'},
    {'name': 'sensors.secure.topic', 'type': 'topic', 'routing_key': '#'},
]

# Declare all exchanges and bind queues
for exchange in exchanges:
    try:
        # Declare the exchange
        channel.exchange_declare(exchange=exchange['name'], exchange_type=exchange['type'])
        
        # Create a queue for this exchange
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Bind the queue to the exchange
        channel.queue_bind(
            exchange=exchange['name'],
            queue=queue_name,
            routing_key=exchange['routing_key']
        )
        
        print(f"{Fore.GREEN}[ATTACK SIMULATION] Listening on exchange: {exchange['name']}{Style.RESET_ALL}")
        
        # Set up a consumer on this queue
        def create_callback(exchange_name):
            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    
                    # Check if the message is encrypted
                    if isinstance(data, dict) and data.get('is_encrypted', False):
                        print(f"{Fore.RED}[ATTACK SIMULATION] Intercepted ENCRYPTED message on {exchange_name}:")
                        print(f"{Fore.RED}[ATTACK SIMULATION] Cannot read contents - encryption protects the data!{Style.RESET_ALL}")
                        
                        # Attempt to decrypt with known key (this would fail in a real-world scenario)
                        try:
                            print(f"{Fore.RED}[ATTACK SIMULATION] Attempting to decrypt (for demo purposes)...")
                            decrypted = decrypt_message(data)
                            print(f"{Fore.GREEN}[ATTACK SIMULATION] Decryption successful (using built-in key):")
                            print(f"{Fore.GREEN}{json.dumps(decrypted, indent=2)}{Style.RESET_ALL}")
                            
                            # Demonstrate what the attacker can do with this information
                            if "soil_moisture" in decrypted:
                                print(f"{Fore.RED}[ATTACK SIMULATION] Extracted sensitive soil moisture value: {decrypted['soil_moisture']}")
                                print(f"{Fore.RED}[ATTACK SIMULATION] Could use this to determine irrigation patterns or crop health{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}[ATTACK SIMULATION] Decryption failed: {e}{Style.RESET_ALL}")
                        
                    else:
                        # For unencrypted messages, show what information is leaked
                        print(f"{Fore.YELLOW}[ATTACK SIMULATION] Intercepted UNENCRYPTED message on {exchange_name}:{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}{json.dumps(data, indent=2)}{Style.RESET_ALL}")
                        
                        # Demonstrate the risk by highlighting sensitive data
                        if "temperature" in data:
                            print(f"{Fore.RED}[ATTACK SIMULATION] Extracted temperature: {data['temperature']} °C{Style.RESET_ALL}")
                        if "soil_moisture" in data:
                            print(f"{Fore.RED}[ATTACK SIMULATION] Extracted soil moisture: {data['soil_moisture']}{Style.RESET_ALL}")
                        if "timestamp" in data:
                            print(f"{Fore.RED}[ATTACK SIMULATION] Extracted timestamp: {data['timestamp']}{Style.RESET_ALL}")
                            print(f"{Fore.RED}[ATTACK SIMULATION] This reveals when sensors are active{Style.RESET_ALL}")
                        
                        if "device_id" in data:
                            print(f"{Fore.RED}[ATTACK SIMULATION] Extracted device ID: {data['device_id']}{Style.RESET_ALL}")
                            
                        # Check for signatures
                        if "signature" in data:
                            print(f"{Fore.YELLOW}[ATTACK SIMULATION] Message is signed - harder to modify but contents are still visible{Style.RESET_ALL}")
                        
                except json.JSONDecodeError:
                    print(f"{Fore.RED}[ATTACK SIMULATION] Intercepted non-JSON message: {body}{Style.RESET_ALL}")
                
                print(f"{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}")
                
            return callback
        
        # Start consuming messages from this queue
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=create_callback(exchange['name']),
            auto_ack=True
        )
        
    except Exception as e:
        print(f"{Fore.RED}[ATTACK SIMULATION] Error setting up listener for {exchange['name']}: {e}{Style.RESET_ALL}")

print(f"{Fore.GREEN}[ATTACK SIMULATION] Message sniffer active - listening for messages...{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Press Ctrl+C to exit{Style.RESET_ALL}")

try:
    # Start consuming messages
    channel.start_consuming()
except KeyboardInterrupt:
    print(f"{Fore.RED}[ATTACK SIMULATION] Stopping message sniffer{Style.RESET_ALL}")
    channel.stop_consuming()
    
connection.close() 