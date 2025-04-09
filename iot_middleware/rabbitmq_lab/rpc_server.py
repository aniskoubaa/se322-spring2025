import pika
import os
import time
import json
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection parameters
url = "amqps://ouglwzrd:c_hpaHyMLopcTGtxDytHJzhSkfYVlC70@jaragua.lmq.cloudamqp.com/ouglwzrd"
# Alternative using environment variables
# url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')}"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Declare a queue for RPC requests
queue_name = "rpc_queue"
channel.queue_declare(queue=queue_name)

# Simple device temperature simulator functions
def get_device_temperature(device_id):
    """Simulate getting a device temperature"""
    # In a real system, this would query a device or database
    import random
    time.sleep(0.5)  # Simulate processing time
    return round(20 + random.random() * 15, 1)  # Return temperature between 20-35°C

def set_device_temperature(device_id, target_temp):
    """Simulate setting a device temperature"""
    time.sleep(0.7)  # Simulate processing time
    return {"success": True, "device_id": device_id, "target_temperature": target_temp}

# Callback to process RPC requests
def on_request(ch, method, props, body):
    try:
        # Parse the request
        request = json.loads(body)
        action = request.get("action")
        device_id = request.get("device_id")
        
        print(f" [.] Received {action} request for device {device_id}")
        
        # Process the request based on action
        if action == "get_temperature":
            result = get_device_temperature(device_id)
            response = {
                "success": True,
                "device_id": device_id,
                "temperature": result
            }
        elif action == "set_temperature":
            target_temp = request.get("target_temperature")
            result = set_device_temperature(device_id, target_temp)
            response = result
        else:
            response = {"success": False, "error": "Unknown action"}
    
    except Exception as e:
        response = {"success": False, "error": str(e)}
    
    # Send the response back to the client
    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f" [.] Sent response: {response}")

# Set up the consumer
channel.basic_qos(prefetch_count=1)  # Process only one message at a time
channel.basic_consume(queue=queue_name, on_message_callback=on_request)

print(" [x] RPC Server awaiting requests. To exit press CTRL+C")
channel.start_consuming() 