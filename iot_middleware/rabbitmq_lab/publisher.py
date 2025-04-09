import pika
import os

# LavinMQ connection parameters
url = "amqps://ouglwzrd:c_hpaHyMLopcTGtxDytHJzhSkfYVlC70@jaragua.lmq.cloudamqp.com/ouglwzrd"
#url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')} "
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Declare an exchange
exchange_name = "test_exchange"
channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")

# Publish a message
message = "Hello, LavinMQ!"
channel.basic_publish(exchange=exchange_name, routing_key="", body=message)

print(f" [x] Sent '{message}'")

connection.close()
