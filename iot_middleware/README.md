Sure! Here's your `README.md` rewritten with relevant emojis to enhance clarity and engagement:

---

# 🌐 IoT Middleware Lab: MQTT with Arduino Nano ESP32

This lab demonstrates the use of the **MQTT protocol** for IoT communication using an **Arduino Nano ESP32** 🧠📶.

---

## 🧭 Overview

The lab is divided into **two phases**:

1. 🔁 **Phase 1**: *Unidirectional communication* – Arduino 📡 publishes sensor data, Python 🐍 subscribes and controls actuators
2. 🔄 **Phase 2**: *Bidirectional communication* – Arduino both publishes sensor data and subscribes to commands 🧠

---

## 🧰 Requirements

### 🔌 Hardware
- 🖲️ Arduino Nano ESP32  
- 🌡️ DHT11 or DHT22 sensor  
- 💡 LED  
- 📢 Buzzer  
- 🔗 Jumper wires  
- 🔳 Breadboard  

### 💻 Software
- 💡 Arduino IDE with ESP32 board manager  
- 🐍 Python with conda environment  
- 🔍 MQTT Explorer *(optional for testing)*

---

## ⚙️ Setup

### 🔧 Arduino Setup
1. Connect the **DHT sensor** to **GPIO2**
2. Connect the **LED** to **GPIO13** (use an appropriate resistor)
3. Connect the **buzzer** to **GPIO5**
4. Install the following libraries in the Arduino IDE:
   - 📦 `PubSubClient`
   - 🌡️ `DHT sensor library`
   - 📶 `WiFi` library *(usually included with ESP32 board)*

📄 For wiring details, see the [**Circuit Diagram**](./circuit_diagram.md)

---

### 🐍 Python Setup
1. Create the conda environment:
   ```bash
   conda env create -f environment.yml
   ```
2. Activate the environment:
   ```bash
   conda activate se322
   ```

---

## 🚦 Instructions

### 🔁 Phase 1: *Unidirectional MQTT* (⏱️ 25 minutes)
1. Open `arduino/phase1_publish_only.ino` in Arduino IDE
2. Update WiFi SSID and password 🔐
3. Upload the sketch to your **Nano ESP32** 📥
4. Run the Python script:
   ```bash
   conda activate se322
   python python/mqtt_controller.py
   ```
5. 🖥️ Watch temperature and humidity data in the Python console

---

### 🔄 Phase 2: *Bidirectional MQTT* (⏱️ 20 minutes)
1. Open `arduino/phase2_bidirectional.ino` in Arduino IDE
2. Update WiFi SSID and password 🔐
3. Upload the sketch to your **Nano ESP32**
4. Run the **same** Python script as in Phase 1
5. 🧪 Test the system:
   - Watch the **Arduino serial monitor** 🖨️
   - Warm the sensor 🌡️ to raise temperature above **30°C**
   - ✅ LED 💡 and Buzzer 📢 should activate when `"ALERT_ON"` is received

---

## 🔍 How It Works

### 📡 Phase 1
- Arduino **publishes** to `home/temp` topic
- Python **subscribes** to `home/temp` and processes the data
- Python can **publish** to `home/cmd`, but Arduino does **not react** (yet!)

### 🔁 Phase 2
- Arduino continues publishing to `home/temp`
- Arduino also **subscribes** to `home/cmd`
- Python **publishes** commands to `home/cmd`
- ✅ Full **bidirectional communication** is established

---

## 🛠️ Troubleshooting

- 📶 Double-check your **WiFi credentials**
- 🖥️ Use the **Serial Monitor** for debug output
- 🔌 Make sure all **hardware connections** are secure
- 🌍 Verify that the MQTT broker `broker.hivemq.com` is reachable

---

Happy experimenting! 🚀💡

---
