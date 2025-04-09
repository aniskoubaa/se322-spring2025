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

# Declare a random queue (non-durable, auto-delete)
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange
channel.queue_bind(exchange=exchange_name, queue=queue_name)

print(" [*] Waiting for messages. To exit press CTRL+C")

# Callback function
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

# Consume messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
