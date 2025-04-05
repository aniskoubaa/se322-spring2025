# IoT Middleware Lab: MQTT with Arduino Nano ESP32

This lab demonstrates the use of MQTT protocol for IoT communication using an Arduino Nano ESP32.

## Overview

The lab is divided into two phases:
1. **Phase 1**: Unidirectional communication - Arduino publishes sensor data, Python subscribes and controls actuators
2. **Phase 2**: Bidirectional communication - Arduino publishes sensor data and subscribes to commands

## Requirements

### Hardware
- Arduino Nano ESP32
- DHT11 or DHT22 sensor
- LED
- Buzzer
- Jumper wires
- Breadboard

### Software
- Arduino IDE with ESP32 board manager
- Python with conda environment
- MQTT Explorer (optional for testing)

## Setup

### Arduino Setup
1. Connect the DHT sensor to GPIO2
2. Connect the LED to GPIO13 (with appropriate resistor)
3. Connect the buzzer to GPIO5
4. Install the following libraries in Arduino IDE:
   - PubSubClient
   - DHT sensor library
   - WiFi library (usually included with ESP32 board)

For detailed wiring instructions, see the [Circuit Diagram](./circuit_diagram.md).

### Python Setup
1. Create the conda environment:
   ```bash
   conda env create -f environment.yml
   ```
2. Activate the environment:
   ```bash
   conda activate se322
   ```

## Instructions

### Phase 1: Unidirectional MQTT (25 minutes)
1. Open `arduino/phase1_publish_only.ino` in Arduino IDE
2. Update the WiFi SSID and password
3. Upload the code to your Nano ESP32
4. Run the Python script:
   ```bash
   conda activate se322
   python python/mqtt_controller.py
   ```
5. Observe the temperature and humidity data in the Python console

### Phase 2: Bidirectional MQTT (20 minutes)
1. Open `arduino/phase2_bidirectional.ino` in Arduino IDE
2. Update the WiFi SSID and password
3. Upload the code to your Nano ESP32
4. Run the Python script (same as Phase 1)
5. Test the system:
   - Monitor the serial output of the Arduino
   - Warm the sensor to see if temperature rises above 30°C
   - Observe the LED and buzzer activate when "ALERT_ON" is received

## How It Works

### Phase 1
- Arduino publishes temperature and humidity to `home/temp` topic
- Python subscribes to `home/temp` and processes data
- Python publishes commands to `home/cmd` but Arduino doesn't respond yet

### Phase 2
- Arduino publishes temperature and humidity to `home/temp` topic
- Arduino also subscribes to `home/cmd` topic and controls actuators
- Python subscribes to `home/temp` and publishes commands to `home/cmd`
- Full bidirectional communication is established

## Troubleshooting

- Make sure your WiFi credentials are correct
- Check Serial Monitor for debugging information
- Ensure all connections are secure
- Verify the broker address is accessible (`broker.hivemq.com`) 