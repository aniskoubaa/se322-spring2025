# 🌱 IoT Full Stack Agriculture Monitoring App

A simple educational IoT system that simulates environmental sensor data for agriculture and transmits it using RabbitMQ. Data is visualized in a lightweight HTML/JavaScript dashboard.

## 📊 System Architecture

![IoT Farm Sensor Data Flow with RabbitMQ](assets/iot_architecture.png)

## 🧩 System Components

1. **📡 Sensor Simulator**
   - Generates random data for temperature, humidity, and soil moisture
   - Publishes data to RabbitMQ using different exchange types

2. **🔄 Consumers**
   - 📊 Data Logger: Saves all sensor data to a CSV file
   - ⚠️ Alert Handler: Monitors for abnormal values and prints alerts
   - 🌐 Web Data Server: Forwards data to the dashboard via a Flask API
   - 📊 Topic Analyzer: Demonstrates topic exchange wildcards to subscribe to multiple related topics

3. **📱 Dashboard**
   - Simple HTML/JavaScript webpage that displays sensor values and alerts
   - Updates automatically every 2 seconds

## 📋 Prerequisites

- 🐍 Python 3.6+
- 🐰 RabbitMQ Server or CloudAMQP account
- 🌐 Web browser

## 🔧 Installation

1. **📥 Clone the repository**

2. **📦 Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **🔑 Set up RabbitMQ connection:**
   
   For CloudAMQP:
   - Make sure the `.env` file has your CloudAMQP credentials:
     ```
     RABBITMQ_PASSWORD=your_password
     RABBITMQ_HOST=your_host.cloudamqp.com
     RABBITMQ_PORT=5672
     RABBITMQ_VHOST=your_vhost
     RABBITMQ_USER=your_username
     ```

   For Local RabbitMQ:
   - Install and start RabbitMQ server
   - Update the `utils.py` file to use local connection parameters

## 🏃‍♂️ Running the Application

1. **▶️ Start the components in separate terminal windows:**

   Start the web data server:
   ```
   cd se322-spring2025/iot_full_stack_app
   python consumers/web_data_server.py
   ```

   Start the data logger:
   ```
   cd se322-spring2025/iot_full_stack_app
   python consumers/data_logger.py
   ```

   Start the alert handler:
   ```
   cd se322-spring2025/iot_full_stack_app
   python consumers/alert_handler.py
   ```

   Start the topic analyzer:
   ```
   cd se322-spring2025/iot_full_stack_app
   python consumers/topic_analyzer.py
   ```

   Start the sensor emitter:
   ```
   cd se322-spring2025/iot_full_stack_app
   python sensors/sensor_emitter.py
   ```

2. **🖥️ Open the dashboard:**
   Open the file `dashboard/index.html` in your web browser.

## 🔄 Exchange Types Demonstrated

- **📢 Fanout Exchange**: Broadcasts sensor data to all bound queues
- **🎯 Direct Exchange**: Sends alerts based on routing key
- **📋 Topic Exchange**: Routes data by sensor type with wildcards (e.g., sensor.*)
- **🏷️ Headers Exchange**: Routes based on message headers

## ⚠️ Alert Thresholds

- 🌡️ Temperature: Alert if > 35°C
- 💧 Humidity: Alert if < 30%
- 🌱 Soil Moisture: Alert if < 250 units

## 📁 Project Structure

```
iot_full_stack_app/
├── consumers/
│   ├── alert_handler.py
│   ├── data_logger.py
│   ├── topic_analyzer.py
│   └── web_data_server.py
├── dashboard/
│   ├── app.js
│   └── index.html
├── sensors/
│   └── sensor_emitter.py
├── data/
│   └── sensor_data.csv (created when running)
├── assets/
│   └── iot_architecture.png
├── .env
├── utils.py
├── requirements.txt
└── README.md
``` 