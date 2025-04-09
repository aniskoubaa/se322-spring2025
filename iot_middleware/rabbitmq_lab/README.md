# RabbitMQ Lab for IoT Middleware

This lab provides hands-on examples to understand RabbitMQ, a popular message broker in IoT middleware applications.

## Prerequisites

- Python 3.6+
- `pika` library (`pip install pika`)

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

## Lab Examples

- **Basic Pub/Sub**: Simple fanout publisher and subscriber
- **Direct Exchange**: Message routing based on exact routing keys
- **Topic Exchange**: Message filtering using pattern matching
- **RPC Pattern**: Request-response pattern implementation
- **Message Acknowledgment**: Ensuring reliable message delivery
- **Message Persistence**: Surviving broker restarts
- **Dead Letter Exchange**: Handling failed message deliveries

## How to Run Examples

Each example has separate publisher and subscriber scripts:

1. Start the subscriber in one terminal: `python <example_name>_subscriber.py`
2. Run the publisher in another terminal: `python <example_name>_publisher.py`

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

## Additional Resources

- [RabbitMQ Official Documentation](https://www.rabbitmq.com/documentation.html)
- [Pika Python Client Documentation](https://pika.readthedocs.io/)
- [CloudAMQP Knowledge Base](https://www.cloudamqp.com/docs/index.html) 