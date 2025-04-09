# RabbitMQ Parameters and Configuration Guide

This document explains the key parameters, configuration options, and functions used in the RabbitMQ lab scripts.

## Connection Parameters

### Basic Connection Setup
```python
url = "amqps://username:password@hostname/vhost"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
```

| Parameter | Description |
|-----------|-------------|
| `amqps://` | Protocol prefix for secure TLS connection (use `amqp://` for non-secure) |
| `username` | RabbitMQ user account name |
| `password` | Authentication password |
| `hostname` | Server hostname or IP address |
| `vhost` | Virtual host (logical partition within RabbitMQ) |

### Connection Parameters Using Environment Variables
```python
url = f"amqps://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}/{os.getenv('RABBITMQ_VHOST')}"
```

## Exchange Declaration

```python
channel.exchange_declare(
    exchange="exchange_name",    # Name of the exchange
    exchange_type="type",        # Type: fanout, direct, topic, headers
    durable=True,                # Survive broker restart
    auto_delete=False,           # Delete when no queues are bound
    internal=False,              # Only for internal use by other exchanges
    arguments=None               # Optional additional arguments
)
```

| Exchange Type | Description | Use Case |
|---------------|-------------|----------|
| `fanout` | Broadcasts messages to all bound queues | When all consumers need all messages |
| `direct` | Routes based on exact routing key match | When messages need to go to specific queues |
| `topic` | Routes based on pattern matching | When messages need selective routing |
| `headers` | Routes based on message header attributes | For complex routing needs not suited to routing keys |

## Queue Declaration

```python
result = channel.queue_declare(
    queue="queue_name",      # Name of the queue (empty for random name)
    durable=False,           # Survive broker restart
    exclusive=False,         # Used by only one connection and auto-delete
    auto_delete=False,       # Delete when last consumer unsubscribes
    arguments={              # Optional additional arguments
        'x-message-ttl': 60000,                # Message time-to-live (ms)
        'x-expires': 3600000,                  # Queue expiry when unused (ms)
        'x-max-length': 1000,                  # Maximum number of messages
        'x-max-length-bytes': 10485760,        # Maximum queue size in bytes
        'x-overflow': 'reject-publish',        # Action when queue full
        'x-dead-letter-exchange': 'dlx',       # Exchange for rejected/expired messages
        'x-dead-letter-routing-key': 'dlx-key' # Routing key for dead-letter messages
    }
)
queue_name = result.method.queue  # Get the queue name (useful for random names)
```

## Queue Binding

```python
channel.queue_bind(
    queue="queue_name",      # Queue to bind
    exchange="exchange_name", # Exchange to bind to
    routing_key="key",       # Routing key for binding (pattern for topic exchanges)
    arguments=None           # Optional arguments (used mainly for headers exchange)
)
```

### Headers Exchange Binding Arguments

```python
# Headers exchange binding with "all" match
channel.queue_bind(
    exchange="headers_exchange",
    queue=queue_name,
    arguments={
        "x-match": "all",           # "all" requires all headers to match
        "device_type": "sensor",    # Custom header to match
        "location": "indoor"        # Custom header to match
    }
)

# Headers exchange binding with "any" match
channel.queue_bind(
    exchange="headers_exchange",
    queue=queue_name,
    arguments={
        "x-match": "any",           # "any" requires at least one header to match
        "priority": "high",         # Custom header to match
        "location": "outdoor"       # Custom header to match
    }
)
```

## Publishing Messages

```python
channel.basic_publish(
    exchange="exchange_name",    # Exchange to publish to
    routing_key="key",           # Routing key (interpreted based on exchange type)
    body="message_content",      # Message body (as bytes or string)
    properties=pika.BasicProperties(
        delivery_mode=2,         # 2 = persistent (survive broker restart), 1 = transient
        content_type="text/plain", # MIME type of the message content
        content_encoding="utf-8",  # Encoding of the message content
        headers={"key": "value"},  # Custom headers for the message
        priority=0,              # Message priority (0-9)
        correlation_id="id",     # Used for correlating RPC responses with requests
        reply_to="callback_queue", # Queue to reply to (for RPC)
        expiration="60000",      # Message expiration time in milliseconds
        message_id="unique_id",  # Application-specific message identifier
        timestamp=int(time.time()), # Message timestamp
        type="message_type",     # Application-specific message type
        user_id="user",          # Creating user (validated by server)
        app_id="app_name",       # Creating application
        cluster_id="cluster"     # RabbitMQ cluster ID
    )
)
```

## Consuming Messages

### Basic Consumption Setup

```python
def callback(ch, method, properties, body):
    """Process received messages"""
    print(f" [x] Received {body.decode()}")
    # Process the message...
    
    # For manual acknowledgment
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Set quality of service (prefetch count)
channel.basic_qos(prefetch_count=1)  # Only send one message at a time

# Start consuming
channel.basic_consume(
    queue="queue_name",
    on_message_callback=callback,
    auto_ack=False  # False = manual acknowledgment
)

# Block and process messages
channel.start_consuming()
```

### Callback Parameters Explained

| Parameter | Description |
|-----------|-------------|
| `ch` | The channel object |
| `method` | Delivery information (includes delivery_tag, exchange, routing_key) |
| `properties` | Message properties (headers, content_type, etc.) |
| `body` | Message content (as bytes) |

## Message Acknowledgment

```python
# Acknowledge message (mark as successfully processed)
ch.basic_ack(delivery_tag=method.delivery_tag)

# Reject message and requeue
ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

# Reject message without requeuing (will go to dead-letter exchange if configured)
ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

# Negative acknowledgment (reject multiple messages)
ch.basic_nack(delivery_tag=method.delivery_tag, multiple=True, requeue=True)
```

## Quality of Service (QoS)

```python
channel.basic_qos(
    prefetch_size=0,      # Maximum pre-fetched message size in bytes (0 = no limit)
    prefetch_count=1,     # Maximum number of messages to pre-fetch
    global_qos=False      # Apply to entire channel (True) or just this consumer (False)
)
```

## Dead Letter Exchange Configuration

```python
# Declare dead letter exchange
channel.exchange_declare(exchange="dlx_exchange", exchange_type="direct")

# Declare queue for dead-lettered messages
channel.queue_declare(queue="dead_letter_queue", durable=True)
channel.queue_bind(exchange="dlx_exchange", queue="dead_letter_queue", routing_key="expired")

# Declare main queue with dead-letter configuration
channel.queue_declare(
    queue="main_queue",
    durable=True,
    arguments={
        'x-dead-letter-exchange': "dlx_exchange",     # DLX for rejected/expired messages
        'x-dead-letter-routing-key': "expired",       # Routing key for dead-lettered messages
        'x-message-ttl': 10000,                       # Time-to-live: 10 seconds
    }
)
```

## RPC Pattern Implementation

### Server Side

```python
# Declare RPC queue
channel.queue_declare(queue="rpc_queue")

# Process RPC request and send response
def on_request(ch, method, props, body):
    # Process the request
    response = process_request(body)
    
    # Send the response back to the client
    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,         # Client's callback queue
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id  # Same correlation ID from request
        ),
        body=response
    )
    
    # Acknowledge the request
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consume RPC requests
channel.basic_consume(queue="rpc_queue", on_message_callback=on_request)
```

### Client Side

```python
# Create callback queue
result = channel.queue_declare(queue="", exclusive=True)
callback_queue = result.method.queue

# Generate correlation ID
correlation_id = str(uuid.uuid4())

# Publish RPC request
channel.basic_publish(
    exchange="",
    routing_key="rpc_queue",
    properties=pika.BasicProperties(
        reply_to=callback_queue,         # Where to send the response
        correlation_id=correlation_id,   # To correlate response with request
    ),
    body=request_body
)

# Wait for response (simplified)
for method_frame, properties, body in channel.consume(callback_queue):
    if properties.correlation_id == correlation_id:
        # This is our response
        channel.basic_ack(method_frame.delivery_tag)
        channel.cancel()
        return body
```

## Common Error Handling Patterns

```python
try:
    # RabbitMQ operations
    channel.queue_declare(...)
    channel.basic_publish(...)
except pika.exceptions.AMQPConnectionError:
    # Handle connection errors
    reconnect()
except pika.exceptions.ChannelClosedByBroker as e:
    # Handle channel errors (e.g., queue or exchange doesn't exist)
    if e.reply_code == 404:  # Not Found
        # Create missing resources
    elif e.reply_code == 403:  # Access Refused
        # Handle permission issues
except Exception as e:
    # Handle other errors
    log_error(e)
```

## Connection Closing

```python
# Close the channel
channel.close()

# Close the connection
connection.close()
``` 