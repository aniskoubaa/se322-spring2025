# 🔒 IoT Security for Agriculture Monitoring App

This project extends the IoT Full Stack Agriculture Monitoring App by adding security features to protect against common IoT attacks. It demonstrates both attack vectors and security countermeasures in a simple educational context.

## 🎯 Objectives

1. Demonstrate common IoT security vulnerabilities:
   - **🕵️ Eavesdropping**: Sniffing unencrypted RabbitMQ messages
   - **🔄 Man-in-the-Middle (MITM)**: Intercepting and modifying messages
   - **🤖 Spoofing**: Sending fake sensor data or pump commands
   - **🧨 Data Theft**: Unauthorized access to sensitive soil data

2. Implement security countermeasures:
   - **🔐 Encryption**: Protecting message confidentiality
   - **🔒 TLS**: Securing communication channels
   - **🔑 Authentication**: Verifying device identity
   - **🛡️ Input Validation**: Preventing injection attacks
   - **🔍 Message Integrity**: Ensuring data hasn't been tampered with

## 📊 System Architecture

![IoT Farm Sensor Data Flow with Security](assets/iot_security_architecture.png)

## 🧩 System Components

### 🌐 Original Components (with security enhancements)
- **📡 Secure Sensor Simulator**: Generates signed/encrypted sensor data
- **🔄 Secure Consumers**: Validates and processes authentic messages
- **📱 Secure Dashboard**: Shows data integrity status and security alerts

### 🔴 Attack Simulations
- **🕵️ Message Sniffer**: Passive interception of unencrypted messages
- **🎭 Message Spoofer**: Sends unauthorized/false commands and readings
- **🔄 MITM Attacker**: Modifies messages in transit

### 🟢 Security Countermeasures
- **🔒 TLS Configuration**: For encrypted message transport
- **🔑 Message Signing**: For data authenticity verification
- **🛡️ Input Validation**: Guards against injection attacks
- **📝 Audit Logging**: Tracks security events

## 🔧 Installation

1. **📥 Clone the repository**

2. **📦 Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **🔑 Set up RabbitMQ connection:**
   Make sure the `.env` file has your CloudAMQP credentials

## 🏃‍♂️ Running the Demonstration

We've created a demo script to easily run all components:
```
chmod +x run_demo.sh
./run_demo.sh
```

**What happens when you run `run_demo.sh`:**

The script provides an interactive menu with the following options:
1. **Start Secure IoT System**: Launches the secure sensor emitter, web data server, and opens the dashboard
2. **Run Attack Simulations**: Starts the various attack tools (sniffer, spoofer, MITM)
3. **Start Security Monitor**: Launches the security monitoring system to detect and log attacks
4. **View Security Logs**: Displays captured security events and attack attempts
5. **Check Running Processes**: Shows which components are currently active
6. **Stop All Processes**: Terminates all running components
7. **Exit**: Exits the script

The script handles the starting and stopping of components, maintains logs, and provides clear status updates. You can run different scenarios by selecting the appropriate menu options in sequence.

## 🔴 Attack Demonstrations: Understanding the Threats First

> **Important**: To fully demonstrate the attacks, you need both the IoT system and the attack tools running simultaneously. Use option 1 from the demo script to start the secure IoT system first, then use option 2 to run attack simulations.

Before implementing security countermeasures, it's crucial to understand the threats. Run these demonstrations to see how attackers can exploit an unsecured IoT system:

### Manual Setup (Terminal-by-Terminal)

To manually run the demonstration without using the script, open multiple terminal windows:

**Terminal 1: Start the Secure IoT System**
```
# Start the secure sensor emitter
python sensors/secure_sensor_emitter.py
```

**Terminal 2: Start the Web Data Server**
```
# Start the secure web data server
python consumers/secure_web_data_server.py
```

**Terminal 3: Run the Eavesdropper (Message Sniffer)**
```
# Start the message sniffer to see all messages passing through the system
python attack_simulation/message_sniffer.py
```

**Terminal 4: Run the Impersonator (Message Spoofer)**
```
# Start the message spoofer to inject fake data
python attack_simulation/message_spoofer.py
```

**Terminal 5: Run the Interceptor (MITM Attacker)**
```
# Start the man-in-the-middle attacker to modify legitimate messages
python attack_simulation/mitm_attacker.py
```

**Terminal 6: Start the Security Monitor**
```
# Start the security monitor to detect attacks
python security_countermeasures/security_monitor.py
```

**Browser: Open the Dashboard**
```
# Open this file in your web browser
dashboard/index.html
```

### Individual Attack Details

### 1. The Eavesdropper (Message Sniffer)
```
python attack_simulation/message_sniffer.py
```
**What it does:** Passively listens to all RabbitMQ messages, extracting:
- Temperature, humidity, and soil moisture readings
- Sensor IDs and timestamps
- Command messages intended for actuators

**Implementation:** Uses RabbitMQ client to bind to all exchanges and queues, logging all messages that pass through the system. In an unsecured system, all this data is transmitted in plaintext.

### 2. The Impersonator (Message Spoofer)
```
python attack_simulation/message_spoofer.py
```
**What it does:**
- Sends fake sensor data to trigger false alerts
- Generates falsified pump activation commands
- Attempts to forge signatures for authenticated exchanges

**Implementation:** Creates fraudulent messages matching valid message formats but with tampered values. Without signature verification, these messages are indistinguishable from legitimate ones.

### 3. The Interceptor (MITM Attacker)
```
python attack_simulation/mitm_attacker.py
```
**What it does:**
- Intercepts legitimate messages
- Modifies values (e.g., changing temperature readings)
- Forwards modified messages to the intended recipient

**Implementation:** Creates a "bridge" between original exchanges and custom exchanges, modifying messages as they pass through. Without integrity checks, recipients cannot detect these modifications.

## 🟢 Security Countermeasures: Seeing the Difference

Now run the secure system alongside the attacks to see how security measures prevent these exploits:

### 1. Secure IoT System
```
python sensors/secure_sensor_emitter.py
python consumers/secure_web_data_server.py
python security_countermeasures/security_monitor.py
```

**Open dashboard:** `dashboard/index.html`

### 2. Key Security Features Implemented

**Message Signing (Authenticity):**
```python
# From security_utils.py
def sign_message(message, device_id):
    # Create digital signature using HMAC-SHA256
    signature = hmac.new(device_key, message_str.encode('utf-8'), hashlib.sha256).hexdigest()
    message_copy["signature"] = signature
    return message_copy
```

**Encryption (Confidentiality):**
```python
# From security_utils.py
def encrypt_message(message_dict):
    # AES-256-CBC encryption with random IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    # ... encryption logic ...
    return encrypted_message
```

**Timestamp Verification (Anti-Replay):**
```python
# From security_utils.py
def is_message_recent(signed_message, max_age_seconds=60):
    # Prevent replay attacks by checking message age
    message_age = current_time - timestamp
    return message_age <= max_age_seconds
```

**Anomaly Detection (Intrusion Detection):**
```python
# From security_countermeasures/security_monitor.py
def check_for_tampering(message, device_id):
    # Detect suspicious patterns, unusual value changes
    if abs(temp - avg_temp) > 10:
        log_security_event('ANOMALY_DETECTION', details)
```

## 🔍 Demonstration Results

When you run both the attack simulations and secure system:

1. **Eavesdropper:** Can see unencrypted messages but cannot read encrypted ones
2. **Impersonator:** Forged messages are rejected by signature verification
3. **Interceptor:** Modified messages fail integrity checks
4. **Security Monitor:** Detects and logs all attack attempts

The dashboard will display security status, showing which messages are authenticated and verified vs. potential security breaches.

## 🔐 Security Implementation Details

1. **Message Encryption**: Using AES-256 for payload encryption
2. **Digital Signatures**: HMAC-SHA256 for message authentication
3. **TLS**: Configured for RabbitMQ connections
4. **Input Validation**: JSON schema validation for all messages
5. **Access Control**: Basic authentication for critical operations

## 📚 Educational Resources

- [OWASP IoT Top 10](https://owasp.org/www-project-internet-of-things-top-10/)
- [NIST IoT Security](https://www.nist.gov/programs-projects/nist-cybersecurity-iot-program)
- [IoT Security Foundation](https://www.iotsecurityfoundation.org/) 