import pika
import os
import uuid
import json
import time
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection parameters
url = "amqps://ouglwzrd:c_hpaHyMLopcTGtxDytHJzhSkfYVlC70@jaragua.lmq.cloudamqp.com/ouglwzrd"
# Alternative using environment variables
# url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')}"
params = pika.URLParameters(url)

class DeviceRpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        # Create callback queue
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        
        # Set up consumer for responses
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        """Callback when we get a response"""
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, request):
        """Make an RPC request"""
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        # Send the request
        self.channel.basic_publish(
            exchange="",
            routing_key="rpc_queue",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(request)
        )
        
        # Wait for the response
        timeout = 5  # seconds
        start_time = time.time()
        
        while self.response is None:
            # Process data events to trigger callback
            self.connection.process_data_events()
            
            # Check for timeout
            if time.time() - start_time > timeout:
                return {"success": False, "error": "Request timed out"}
            
            time.sleep(0.1)
        
        return self.response
    
    def close(self):
        """Close the connection"""
        self.connection.close()

# Example usage
if __name__ == "__main__":
    # Create RPC client
    device_client = DeviceRpcClient()
    
    # Get command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python rpc_client.py get <device_id>")
        print("  python rpc_client.py set <device_id> <temperature>")
        print("\nUsing default: get device_001")
        command = "get"
        device_id = "device_001"
    else:
        command = sys.argv[1].lower()
        device_id = sys.argv[2] if len(sys.argv) > 2 else "device_001"
    
    try:
        # Make RPC calls based on command
        if command == "get":
            print(f" [x] Requesting temperature for device {device_id}")
            request = {
                "action": "get_temperature",
                "device_id": device_id
            }
            response = device_client.call(request)
            
            if response.get("success"):
                print(f" [.] Device {device_id} temperature: {response.get('temperature')}°C")
            else:
                print(f" [!] Error: {response.get('error')}")
                
        elif command == "set":
            if len(sys.argv) < 4:
                print("Error: Missing temperature value")
                print("Usage: python rpc_client.py set <device_id> <temperature>")
                sys.exit(1)
                
            target_temp = float(sys.argv[3])
            print(f" [x] Setting temperature for device {device_id} to {target_temp}°C")
            
            request = {
                "action": "set_temperature",
                "device_id": device_id,
                "target_temperature": target_temp
            }
            response = device_client.call(request)
            
            if response.get("success"):
                print(f" [.] Successfully set temperature to {target_temp}°C")
            else:
                print(f" [!] Error: {response.get('error')}")
                
        else:
            print(f"Unknown command: {command}")
            print("Available commands: get, set")
    
    finally:
        # Close the connection
        device_client.close() 