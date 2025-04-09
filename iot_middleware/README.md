# IoT Middleware Lab: MQTT with Arduino Nano ESP32

This lab demonstrates the use of MQTT protocol for IoT communication using an Arduino Nano ESP32.

## Overview

The lab is divided into two phases:
1. **Phase 1**: Unidirectional communication - Arduino publishes sensor data, Python subscribes and controls actuators
2. **Phase 2**: Bidirectional communication - Arduino publishes sensor data and subscribes to commands

## Implementation Options

You can complete this lab using one of three approaches:

1. **Physical Hardware**: Using actual Arduino Nano ESP32 and sensors
2. **Wokwi Simulation**: Online simulation of the hardware
3. **Python Emulator**: Software-only emulation of the Arduino node

### 1. Physical Hardware Requirements
- Arduino Nano ESP32
- DHT22 sensor
- LED
- Buzzer
- Jumper wires
- Breadboard

### 2. Wokwi Simulation
You can simulate this project online:

1. Go to [Wokwi](https://wokwi.com/)
2. Use the ready-made project: [SE322 IoT Middleware Lab](https://wokwi.com/projects/391533850618798081)
3. Or create a new project and replace the default files with:
   - `arduino/phase1_wokwi.ino` for the code
   - `arduino/diagram.json` for the hardware configuration

The simulation demonstrates:
- ESP32 connection to MQTT broker
- DHT22 sensor readings
- Real-time data publishing
- Alert system response

### 3. Python Emulator
If hardware or simulation isn't available, use the Python emulator:

```bash
# Activate the conda environment
conda activate se322

# Run the emulator
python python/arduino_emulator.py

# In another terminal, run the controller
python python/mqtt_controller.py
```

The emulator provides:
- Simulated temperature and humidity readings
- Interactive temperature control ('w' to warm up, 'c' to cool down)
- Real-time MQTT communication
- Visual feedback for alerts

## Setup Instructions

### Option 1: Physical Hardware Setup
1. Connect the DHT22 sensor:
   - DATA pin to GPIO15
   - VCC to 3.3V
   - GND to GND
2. Install Arduino libraries:
   - PubSubClient
   - DHTesp
   - WiFi library

### Option 2: Wokwi Setup
```json
{
  "version": 1,
  "author": "Anis Koubaa",
  "editor": "wokwi",
  "parts": [
    { "type": "wokwi-esp32-devkit-v1", "id": "esp", "top": -0.67, "left": -76, "attrs": {} },
    { "type": "wokwi-dht22", "id": "dht1", "top": -23.57, "left": 113, "attrs": {} }
  ],
  "connections": [
    [ "esp:TX0", "$serialMonitor:RX", "", [] ],
    [ "esp:RX0", "$serialMonitor:TX", "", [] ],
    [ "dht1:GND", "esp:GND.1", "black", [ "v0" ] ],
    [ "dht1:VCC", "esp:3V3", "red", [ "v0" ] ],
    [ "dht1:SDA", "esp:D15", "green", [ "v0" ] ]
  ]
}
```

### Option 3: Python Environment Setup
1. Create and activate the environment:
   ```bash
   conda env create -f environment.yml
   conda activate se322
   ```
2. If you have issues, you can also install manually:
   ```bash
   conda create -n se322 python=3.12
   conda activate se322
   pip install "paho-mqtt>=2.0.0"
   ```

## Instructions

### Phase 1: Unidirectional MQTT (25 minutes)
Choose one of these approaches:

1. **Physical Hardware**:
   - Open `arduino/phase1_wokwi.ino` in Arduino IDE
   - Update WiFi credentials
   - Upload to your Nano ESP32

2. **Wokwi Simulation**:
   - Create new project
   - Upload provided code and diagram
   - Start simulation

3. **Python Emulator**:
   - Run `python/arduino_emulator.py`
   - Use 'w' and 'c' to simulate temperature changes

Then run the controller:
```bash
python python/mqtt_controller.py
```

### Phase 2: Bidirectional MQTT (20 minutes)
Follow the same approach as Phase 1, but:
- For hardware/Wokwi: Use `phase2_bidirectional.ino`
- For emulator: It already supports bidirectional communication

Test the system:
- Monitor the output
- Increase temperature above 30°C
- Watch for "ALERT_ON" responses

## How It Works

### Phase 1
- Node (hardware/simulation/emulator) publishes to `home/temp` topic
- Python controller subscribes and processes data
- Controller publishes commands to `home/cmd`

### Phase 2
- Node also subscribes to `home/cmd` topic
- Full bidirectional communication established
- Alerts triggered based on temperature

## Troubleshooting

### Physical Hardware
- Check WiFi credentials
- Verify wiring connections
- Monitor Serial output

### Wokwi Simulation
- Ensure correct broker address
- Check diagram.json syntax
- Verify pin connections

### Python Emulator
- Confirm MQTT broker accessibility
- Check both terminals (emulator and controller)
- Try manual temperature controls

Happy experimenting! 🚀💡
