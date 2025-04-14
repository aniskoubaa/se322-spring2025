import os
import pika
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_rabbitmq_connection():
    """
    Create a connection to RabbitMQ using CloudAMQP credentials from .env file.
    """
    # Get RabbitMQ connection parameters from environment variables
    rabbitmq_host = os.getenv('RABBITMQ_HOST')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    rabbitmq_user = os.getenv('RABBITMQ_USER')
    rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
    rabbitmq_vhost = os.getenv('RABBITMQ_VHOST')
    
    # Create credentials and connection parameters
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host=rabbitmq_vhost,
        credentials=credentials
    )
    
    # Establish connection
    connection = pika.BlockingConnection(parameters)
    return connection 