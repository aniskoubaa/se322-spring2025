# RabbitMQ Visual Conceptual Guide

This document provides visual representations (using ASCII art) of the key RabbitMQ concepts to help understand how the different exchange types work.

## Basic Message Flow

```
+------------+     +------------+     +----------+     +------------+
| Publisher  |---->|  Exchange  |---->|  Queue   |---->| Consumer   |
+------------+     +------------+     +----------+     +------------+
                        |
                        |             +----------+     +------------+
                        +------------>|  Queue   |---->| Consumer   |
                                      +----------+     +------------+
```

## Exchange Types

### 1. Fanout Exchange

Broadcasts to all queues regardless of routing key.

```
                          +----------+     +------------+
                    +---->|  Queue A |---->| Consumer 1 |
                    |     +----------+     +------------+
+------------+      |
| Publisher  |------+     +----------+     +------------+
+------------+      |     |  Queue B |---->| Consumer 2 |
       |            +---->+----------+     +------------+
       v            |
+-------------+     |     +----------+     +------------+
| Fanout      |-----+---->|  Queue C |---->| Consumer 3 |
| Exchange    |           +----------+     +------------+
+-------------+
```

### 2. Direct Exchange

Routes based on exact routing key matching.

```
                                 Routing Key: "error"
                               +----------------------------+
                               |                            |
                               v                            |
+------------+     +-------------+     +----------+     +------------+
| Publisher  |---->|   Direct    |---->| Queue A  |---->| Consumer 1 |
| (error)    |     |  Exchange   |     | (error)  |     |            |
+------------+     +-------------+     +----------+     +------------+
                          |
+------------+            | Routing Key: "info"
| Publisher  |            |            +----------+     +------------+
| (info)     |------------+----------->| Queue B  |---->| Consumer 2 |
+------------+                         | (info)   |     |            |
                                       +----------+     +------------+
+------------+            | Routing Key: "warning"
| Publisher  |            |            +----------+     +------------+
| (warning)  |------------+----------->| Queue C  |---->| Consumer 3 |
+------------+                         | (warning)|     |            |
                                       +----------+     +------------+
```

### 3. Topic Exchange

Routes based on pattern matching with wildcards.
- `*` matches exactly one word
- `#` matches zero or more words

```
Publishers:                      Topic Exchange:        Binding Keys:          Consumers:

+------------+                                          "*.error"
| "app.error"|                                      +----------------+      +------------+
+------------+---+                                  |                |      |            |
                 |                                  v                |      v            |
+------------+   |   +---------------+       +----------+       +------------+
| "sys.error"|---+-->|    Topic     |------>| Queue A  |------>| Consumer 1 |
+------------+   |   |   Exchange   |       +----------+       +------------+
                 |   +---------------+
+------------+   |         |                 +----------+       +------------+
| "app.info" |---+         |                 |          |       |            |
+------------+             +---------------->| Queue B  |------>| Consumer 2 |
                           | "app.#"         |          |       |            |
+------------+             |                 +----------+       +------------+
| "sys.info" |-------------+
+------------+                              "sys.#"
                                        +----------------+      +------------+
                                        |                |      |            |
                                        v                |      v            |
                                  +----------+       +------------+
                                  | Queue C  |------>| Consumer 3 |
                                  +----------+       +------------+
```

### 4. Headers Exchange

Routes based on message header attributes rather than routing keys.

```
+------------+     +---------------+
| Publisher  |---->|   Headers     |
| Headers:   |     |   Exchange    |
| type=log   |     +---------------+
| source=app |            |
| level=info |            |
+------------+            |
                          |
                          |   x-match=all                 +------------+
                          |   type=log                    |            |
                          +------------------------+----->| Consumer 1 |
                          |   source=app           |      |            |
                          |                        |      +------------+
                          |                  +----------+
                          |                  | Queue A  |
                          |                  +----------+
                          |
                          |   x-match=any                 +------------+
                          |   level=error                 |            |
                          +------------------------+----->| Consumer 2 |
                              level=warn           |      |            |
                                             +----------+ +------------+
                                             | Queue B  |
                                             +----------+
```

## RPC (Request-Response) Pattern

```
+------------+                                                  +------------+
| RPC Client |                                                  | RPC Server |
+------------+                                                  +------------+
      |                                                               |
      | 1. Create callback queue                                      |
      |-------.                                                       |
      |       |                                                       |
      |<------'                                                       |
      |                                                               |
      | 2. Send request with reply_to and correlation_id              |
      |-------------------------------------------------------------->|
      |                                       +--------------------+  |
      |                                       | Process request    |  |
      |                                       |                    |  |
      |                                       |                    |  |
      |                                       +--------------------+  |
      |                                                               |
      |                           3. Send response with correlation_id|
      |<--------------------------------------------------------------|
      |                                                               |
      | 4. Match response by correlation_id                           |
      |-------.                                                       |
      |       |                                                       |
      |<------'                                                       |
```

## Message Acknowledgment and Delivery

```
+------------+     +------------+     +----------+     +------------+
| Publisher  |---->|  Exchange  |---->|  Queue   |---->| Consumer   |
+------------+     +------------+     +----------+     +------------+
                                          |                  |
                                          |                  |
                                          |<-Manual ACK------+
                                          |                  |
        Message remains in queue          |                  |
        until acknowledged                 |  Processing     |
                                          |                  |
                                          |                  |
```

## Dead Letter Exchange Pattern

```
+------------+     +---------------+     +--------------+     +------------+
| Publisher  |---->| Main Exchange |---->| Main Queue   |---->| Consumer   |
+------------+     +---------------+     +--------------+     +------------+
                                               |
                                               | Message rejected
                                               | Message expired
                                               | Queue length exceeded
                                               v
                                         +---------------+     +--------------+     +------------+
                                         | Dead Letter   |---->| DL Queue     |---->| DL Consumer|
                                         | Exchange      |     |              |     |            |
                                         +---------------+     +--------------+     +------------+
``` 