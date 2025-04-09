# RabbitMQ Lab Exercises

This document provides step-by-step lab exercises to help you understand RabbitMQ concepts through hands-on practice. Complete these exercises to gain practical experience with different RabbitMQ patterns.

## Setup Prerequisites

Before starting the exercises:

1. Make sure Python 3.6+ is installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Verify the CloudAMQP credentials in the .env file are correct

## Exercise 1: Basic Publish/Subscribe

**Objective**: Understand the basic publish/subscribe pattern with fanout exchanges.

### Steps:

1. Open two terminal windows.
2. In the first terminal, run the subscriber:
   ```
   python subscriber.py
   ```
3. In the second terminal, run the publisher:
   ```
   python publisher.py
   ```
4. Observe that the subscriber receives the message.
5. Open a third terminal and run another subscriber:
   ```
   python subscriber.py
   ```
6. Run the publisher again and observe that both subscribers receive the message.

### Questions:
- Why do all subscribers receive the same message?
- What happens if you start a subscriber after the message is published?
- What would happen if you stopped the RabbitMQ server between publishing and subscribing?

## Exercise 2: Direct Exchange - Severity Filtering

**Objective**: Learn how to route messages based on severity levels.

### Steps:

1. Open three terminal windows.
2. In the first terminal, subscribe to error and warning messages:
   ```
   python direct_exchange_subscriber.py error warning
   ```
3. In the second terminal, subscribe to info messages:
   ```
   python direct_exchange_subscriber.py info
   ```
4. In the third terminal, run the publisher:
   ```
   python direct_exchange_publisher.py
   ```
5. Observe which messages are received by each subscriber.

### Questions:
- Why does each subscriber only receive specific messages?
- What would happen if a subscriber didn't specify any severity level?
- How would you modify the code to route messages based on both severity and a department name?

## Exercise 3: Topic Exchange - Pattern Matching

**Objective**: Understand pattern-based routing with wildcards.

### Steps:

1. Open three terminal windows.
2. In the first terminal, subscribe to all alerts:
   ```
   python topic_exchange_subscriber.py "*.*.alert"
   ```
3. In the second terminal, subscribe to all kitchen events:
   ```
   python topic_exchange_subscriber.py "*.kitchen.*"
   ```
4. In the third terminal, run the publisher:
   ```
   python topic_exchange_publisher.py
   ```
5. Observe the message distribution patterns.

### Questions:
- What's the difference between `*` and `#` wildcards?
- How would you subscribe to all messages from sensors regardless of location and event type?
- Design a topic pattern for an IoT system that monitors temperature, humidity, and motion in different rooms.

## Exercise 4: Headers Exchange - Attribute-Based Routing

**Objective**: Learn how to route messages based on header attributes.

### Steps:

1. Open three terminal windows.
2. In the first terminal, subscribe to indoor device messages:
   ```
   python headers_exchange_subscriber.py location=indoor
   ```
3. In the second terminal, subscribe to any high priority message or sensor message:
   ```
   python headers_exchange_subscriber.py x-match=any priority=high device_type=sensor
   ```
4. In the third terminal, run the publisher:
   ```
   python headers_exchange_publisher.py
   ```
5. Observe which messages are routed to each subscriber.

### Challenge:
- Modify the headers_exchange_subscriber.py to bind with `x-match=all` and multiple headers.
- Compare the behavior between `x-match=all` and `x-match=any`.

## Exercise 5: RPC Pattern Implementation

**Objective**: Understand the request-response pattern using RabbitMQ.

### Steps:

1. Open two terminal windows.
2. In the first terminal, start the RPC server:
   ```
   python rpc_server.py
   ```
3. In the second terminal, run the RPC client to get a device temperature:
   ```
   python rpc_client.py get device_001
   ```
4. Run the client again to set a device temperature:
   ```
   python rpc_client.py set device_002 25.5
   ```

### Questions:
- How does the correlation ID help in matching responses with requests?
- What happens if the server is not running when the client makes a request?
- How would you implement a timeout mechanism in RPC communication?

## Exercise 6: Message Durability and Acknowledgment

**Objective**: Learn how to ensure message delivery even in failure scenarios.

### Steps:

1. Open two terminal windows.
2. In the first terminal, start the durable consumer:
   ```
   python durable_consumer.py
   ```
3. In the second terminal, run the durable publisher:
   ```
   python durable_publisher.py
   ```
4. Observe the acknowledgment process.
5. Stop the consumer with Ctrl+C before it processes all messages.
6. Start the consumer again and observe that it continues processing unacknowledged messages.

### Questions:
- What is the difference between auto_ack=True and auto_ack=False?
- How does setting delivery_mode=2 affect message persistence?
- What happens to messages if the RabbitMQ server restarts?

## Exercise 7: Dead Letter Exchange

**Objective**: Understand how to handle failed message processing and message expiration.

### Steps:

1. Open three terminal windows.
2. In the first terminal, start the main queue consumer:
   ```
   python dlx_consumer.py
   ```
3. In the second terminal, start the dead-letter queue consumer:
   ```
   python dlx_consumer.py dead-letter
   ```
4. In the third terminal, run the publisher:
   ```
   python dlx_publisher.py
   ```
5. Observe which messages go to the main consumer and which get redirected to the dead-letter queue.

### Questions:
- What are the three main reasons messages can go to a dead-letter queue?
- How can time-to-live (TTL) settings be configured at the queue and message levels?
- How would you use dead-letter exchanges in a real IoT system?

## Challenge Exercises

### Challenge 1: Multi-step IoT Data Pipeline

Create a multi-step data processing pipeline for IoT sensor data:

1. Create a producer script that simulates temperature and humidity readings
2. Create an "ingest" service that validates and enriches the data
3. Create an "analytics" service that processes valid readings
4. Create an "alert" service that detects anomalies
5. Use different exchange types for different parts of the pipeline

### Challenge 2: IoT Device Command and Control

Implement a command-and-control system for IoT devices:

1. Create a command center (publisher) that sends commands to devices
2. Create multiple device simulators (subscribers) that react to commands
3. Implement a response mechanism for devices to report status
4. Add error handling for failed command execution
5. Support both broadcast commands and targeted commands

### Challenge 3: IoT System With Message Prioritization

Extend one of the examples to support message prioritization:

1. Modify a publisher to assign different priorities to messages
2. Implement a consumer that processes high-priority messages first
3. Add persistent message storage for critical messages
4. Implement a retry mechanism for failed message processing
5. Add logging to track message flows through the system

## Submission Guidelines

For each exercise, document:

1. Your observations while running the scripts
2. Answers to the exercise questions
3. Any modifications you made to the code
4. Screenshots showing the exchange of messages
5. A brief explanation of what you learned 