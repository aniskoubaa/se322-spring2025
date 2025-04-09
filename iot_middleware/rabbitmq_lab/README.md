# RabbitMQ Lab for IoT Middleware

This lab provides hands-on examples to understand RabbitMQ, a popular message broker in IoT middleware applications.

## Prerequisites

- Python 3.6+
- `pika` library (`pip install pika`)
- `python-dotenv` library for environment variable management

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Use the provided CloudAMQP credentials or set up your own RabbitMQ instance

## Exchange Types in RabbitMQ

RabbitMQ supports several exchange types, each with different routing behaviors:

### 1. Fanout Exchange
Messages are broadcast to all bound queues regardless of routing keys. Useful for broadcasting messages to multiple subscribers (pub/sub pattern).

### 2. Direct Exchange
Messages are routed to queues based on exact routing key matching. Useful for direct point-to-point communication.

### 3. Topic Exchange
Messages are routed to queues based on wildcard pattern matching of routing keys. Useful for selective message filtering.

### 4. Headers Exchange
Messages are routed based on header attributes instead of routing keys. Useful for complex routing requirements.

## Detailed Lab Examples

### Basic Pub/Sub: Simple Fanout Example
**Files**: `publisher.py`, `subscriber.py`  
**Purpose**: Demonstrates the simplest form of message publishing and consumption using a fanout exchange.  
**Learning Objectives**:
- Understand basic RabbitMQ connection setup
- Learn how to declare exchanges and queues
- See how messages are broadcast to all subscribers with fanout exchanges
- Run multiple subscribers to observe how all receive the same messages

**Usage**:
```
# Terminal 1
python subscriber.py

# Terminal 2 (optionally run multiple subscribers)
python subscriber.py

# Terminal 3
python publisher.py
```

### Direct Exchange: Severity-Based Routing
**Files**: `direct_exchange_publisher.py`, `direct_exchange_subscriber.py`  
**Purpose**: Demonstrates routing messages to specific consumers based on message severity levels.  
**Learning Objectives**:
- Understand how direct exchanges route messages based on exact routing key matching
- Learn how to bind queues with specific routing keys
- See how consumers can selectively receive messages based on routing keys
- Experiment with message filtering based on severity levels

**Usage**:
```
# Terminal 1 (receive only warning and error messages)
python direct_exchange_subscriber.py warning error

# Terminal 2 (receive only critical messages)
python direct_exchange_subscriber.py critical

# Terminal 3
python direct_exchange_publisher.py
```

### Topic Exchange: Hierarchical Routing
**Files**: `topic_exchange_publisher.py`, `topic_exchange_subscriber.py`  
**Purpose**: Demonstrates pattern-based routing using wildcards for IoT device messages.  
**Learning Objectives**:
- Understand the topic exchange pattern-matching rules
- Learn how to use wildcards (*, #) in routing patterns
- See how to implement hierarchical message filtering
- Apply topic-based routing to IoT scenarios (device type, location, event type)

**Usage**:
```
# Terminal 1 (receive all alerts from any device in any location)
python topic_exchange_subscriber.py "*.*.alert"

# Terminal 2 (receive all messages from sensors)
python topic_exchange_subscriber.py "sensor.#"

# Terminal 3 (receive all messages from the living room)
python topic_exchange_subscriber.py "*.livingroom.*"

# Terminal 4
python topic_exchange_publisher.py
```

### Headers Exchange: Attribute-Based Routing
**Files**: `headers_exchange_publisher.py`, `headers_exchange_subscriber.py`  
**Purpose**: Demonstrates routing based on message attributes rather than routing keys.  
**Learning Objectives**:
- Understand how headers exchanges work with message attributes
- Learn to use "all" or "any" matching strategies for headers
- See how to implement complex routing rules without using routing keys
- Implement device type and priority-based message routing

**Usage**:
```
# Terminal 1 (match all indoor devices)
python headers_exchange_subscriber.py location=indoor

# Terminal 2 (match any high priority message OR any gateway message)
python headers_exchange_subscriber.py x-match=any priority=high device_type=gateway

# Terminal 3
python headers_exchange_publisher.py
```

### RPC Pattern: Request-Response Communication
**Files**: `rpc_server.py`, `rpc_client.py`  
**Purpose**: Implements the request-response pattern for IoT device control.  
**Learning Objectives**:
- Understand how to implement RPC (Remote Procedure Call) pattern in RabbitMQ
- Learn how to correlate requests and responses using correlation IDs
- See how to create client-server architectures with message brokers
- Implement timeouts and error handling in RPC communications

**Usage**:
```
# Terminal 1
python rpc_server.py

# Terminal 2
python rpc_client.py get device_001
python rpc_client.py set device_002 25.5
```

### Message Durability: Persistent Messaging
**Files**: `durable_publisher.py`, `durable_consumer.py`  
**Purpose**: Demonstrates how to ensure messages survive broker restarts.  
**Learning Objectives**:
- Understand the concept of message persistence
- Learn how to create durable queues
- See how to mark messages as persistent
- Implement proper message acknowledgment for reliability

**Usage**:
```
# Terminal 1
python durable_consumer.py

# Terminal 2
python durable_publisher.py
```

### Dead Letter Exchange: Handling Failed Messages
**Files**: `dlx_publisher.py`, `dlx_consumer.py`  
**Purpose**: Shows how to handle message processing failures and message expiration.  
**Learning Objectives**:
- Understand dead letter exchanges and their purpose
- Learn how to configure message TTL (time-to-live)
- See how rejected or expired messages are routed to a dead letter queue
- Implement error handling strategies for failed message processing

**Usage**:
```
# Terminal 1 (main queue consumer)
python dlx_consumer.py

# Terminal 2 (dead letter queue consumer)
python dlx_consumer.py dead-letter

# Terminal 3
python dlx_publisher.py
```

## Message Flow in RabbitMQ

1. **Producer** sends messages to an **Exchange**
2. **Exchange** routes messages to one or more **Queues** based on:
   - Exchange type (fanout, direct, topic, headers)
   - Routing rules (routing keys, patterns, headers)
3. **Consumers** receive messages from **Queues**

## Performance Considerations

- Use `basic_qos` to control consumer workload (prevents overwhelming consumers)
- Balance between throughput and reliability by choosing appropriate acknowledgment strategies
- Configure message TTL and queue limits to prevent resource exhaustion
- Consider clustering for high availability in production environments

## Common IoT Use Cases

- **Sensor Data Broadcasting**: Using fanout exchanges to distribute sensor readings
- **Command Routing**: Using direct exchanges to send commands to specific devices
- **Event Filtering**: Using topic exchanges to filter events by category/severity
- **Device Health Monitoring**: Using RPC for device health checks
- **Firmware Updates**: Using persistent messages for reliable firmware delivery

## Security Considerations

- Always use TLS connections (amqps://) in production
- Use unique credentials for each application/device
- Implement proper access controls using RabbitMQ's user management
- Consider using VHost separation for multi-tenant applications

## Additional Resources

- [RabbitMQ Official Documentation](https://www.rabbitmq.com/documentation.html)
- [Pika Python Client Documentation](https://pika.readthedocs.io/)
- [CloudAMQP Knowledge Base](https://www.cloudamqp.com/docs/index.html) 