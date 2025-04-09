# 👨‍🏫 Instructor Notes: IoT Middleware Lab

This document provides guidance for instructors conducting the **IoT Middleware Lab** using **Arduino Nano ESP32** and **MQTT** 🌐📡.

## Implementation Options

The lab can be conducted using three different approaches, in order of preference:

1. **Physical Hardware** (Best for hands-on experience)
2. **Wokwi Simulation** (Good for remote teaching)
   - Ready-made project: [SE322 IoT Middleware Lab](https://wokwi.com/projects/391533850618798081)
   - Can be forked and modified for different scenarios
3. **Python Emulator** (Backup for network/hardware issues)

---

## ⏱️ Time Management *(Total: 45 minutes)*

### 🔁 Phase 1: *Unidirectional MQTT* (25 minutes)
- 🗣️ **5 min**: Introduction to unidirectional MQTT concepts  
- 📲 **15 min**: Setup and implementation
  - Hardware setup OR
  - Wokwi configuration OR
  - Python emulator setup
- 🐍 **5 min**: Testing and verification  

---

### 🔄 Phase 2: *Bidirectional MQTT* (20 minutes)
- 🔄 **5 min**: Explain *Pub/Sub* concepts for bidirectional MQTT  
- 🧪 **10 min**: Students update Arduino code and wire actuators (LED + buzzer)  
- ✅ **5 min**: Test and demonstrate full system functionality  

---

## ✅ Preparation Checklist

### 🧪 Before Lab
- 🔍 Test all **hardware components** beforehand  
- 💻 Ensure **Arduino IDE** is installed with **ESP32 board support**  
- 📚 Confirm required **Arduino libraries** are installed  
- 🌐 Verify access to `broker.hivemq.com` from the lab network  
- ⚙️ Prepare **conda environments** on lab machines if needed  

### 🧰 During Lab
- 🧩 Bring **spare components** (LEDs, resistors, sensors)  
- 🔌 Carry **USB adapters** for different port types  
- 🎥 Prepare a **working demo** to show expected outcomes  

---

## 🛠️ Common Issues & Solutions

- ❌ **WiFi Not Connecting**: Double-check SSID and password; ensure network is stable  
- 📦 **Missing Libraries**: Help students install `PubSubClient`, `DHT`, etc.  
- 🔌 **Hardware Bugs**: Check for incorrect wiring or faulty breadboard/sensor  
- 🚫 **MQTT Broker Down**: Use a **local MQTT broker** (e.g., Mosquitto) as backup  
- 🌡️ **Sensor Not Reading**: Try another DHT sensor or check voltage/pin configuration  

---

## 🚀 Extensions (If Students Finish Early)

1. 🎛️ Add a **potentiometer** to control the temperature threshold  
2. 🌈 Integrate more **sensors** (light/sound) and publish to new MQTT topics  
3. 📊 Build a **web dashboard** using JavaScript/HTML to display live MQTT data  
4. 🧾 Explore **QoS levels** or **retain messages** to extend MQTT logic  

---

## 📝 Assessment Criteria

- ✅ Correct **hardware wiring** and setup  
- 📡 Successful **sensor data publication** via MQTT  
- 🐍 Python script runs correctly and shows data  
- 🔁 Proper **bidirectional communication** functionality  
- 💬 Demonstrated **understanding of MQTT** concepts during discussions  

---

## 📝 Backup Plans

### Plan A: Physical Hardware
- Full hardware setup
- Real sensor readings
- Physical feedback

### Plan B: Wokwi Simulation
- Use provided project link
- Online simulation
- Virtual components
- Real-time feedback

### Plan C: Python Emulator
- Software-only solution
- Simulated readings
- Interactive control

## 📝 Post-Lab Activities

1. **Data Collection**
   - Save MQTT messages
   - Analyze temperature patterns
   - Review alert triggers

2. **Code Review**
   - Check error handling
   - Verify MQTT patterns
   - Assess code quality

3. **Documentation**
   - Update README if needed
   - Note common issues
   - Document improvements

## 📝 Additional Resources

1. **Documentation**
   - MQTT Protocol specs
   - ESP32 datasheets
   - DHT22 specifications

2. **Online Tools**
   - [Wokwi Project](https://wokwi.com/projects/391533850618798081)
   - MQTT Explorer
   - Wokwi documentation
   - Python MQTT client docs

3. **Reference Code**
   - Example projects
   - Testing scripts
   - Debug tools

Remember: Always have multiple backup options ready. The priority order is:
1. Physical Hardware
2. Wokwi Simulation (using provided project link)
3. Python Emulator

---
