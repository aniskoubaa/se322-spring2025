# IoT Security Project - Student Guide

This guide will help you run and understand the IoT Security demonstration for SE322.

## Introduction

This project extends our IoT Agriculture Monitoring application with security features and demonstrates:
1. How attackers can exploit security vulnerabilities in IoT systems
2. How to implement countermeasures to protect against these attacks

## Project Structure

```
iot_security/
├── assets/                  # Architecture diagrams and images
├── attack_simulation/       # Attack demonstration scripts
│   ├── message_sniffer.py   # Eavesdropping attack
│   ├── message_spoofer.py   # Spoofing attack
│   └── mitm_attacker.py     # Man-in-the-Middle attack
├── consumers/               # Consumer applications
│   ├── secure_web_data_server.py  # Secure web server with verification
│   └── ...                  # Other consumer scripts
├── dashboard/               # Dashboard web interface
│   ├── index.html           # Dashboard webpage with security status
│   └── app.js               # Dashboard JavaScript
├── data/                    # Data storage
├── security_countermeasures/
│   └── security_monitor.py  # Security monitoring and alerting
├── sensors/
│   └── secure_sensor_emitter.py  # Secure sensor with signing/encryption
├── security_utils.py        # Security utility functions
├── utils.py                 # General utility functions
├── requirements.txt         # Python dependencies
└── run_demo.sh              # Script to run demonstration components
```

## Setup Instructions

1. Make sure you have Python installed (3.8+ recommended)

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure RabbitMQ:
   Make sure you have filled out the `.env` file with your CloudAMQP credentials:
   ```
   RABBITMQ_PASSWORD=your_password
   RABBITMQ_HOST=your_host.cloudamqp.com
   RABBITMQ_PORT=5672
   RABBITMQ_VHOST=your_vhost
   RABBITMQ_USER=your_username
   ```

## Running the Demonstration

We've provided a shell script that makes it easy to run the demonstrations:

```bash
# Make the script executable if needed
chmod +x run_demo.sh

# Run the demo script
./run_demo.sh
```

The script provides a menu to:
1. Start the secure IoT system (sensor + web server)
2. Run attack simulations
3. Run security monitoring
4. View logs
5. Show running processes
6. Kill all demo processes
7. Open the dashboard in browser

## Security Features to Study

### 1. Message Signing (in `security_utils.py`)
- Study the `sign_message()` and `verify_signature()` functions
- Understand how HMAC-SHA256 is used to verify message integrity and authenticity

### 2. Encryption (in `security_utils.py`)
- Study the `encrypt_message()` and `decrypt_message()` functions
- Understand how AES-256-CBC encryption is implemented

### 3. Timestamp Verification (in `security_utils.py`)
- Study the `is_message_recent()` function
- Understand how this prevents replay attacks

### 4. Anomaly Detection (in `security_countermeasures/security_monitor.py`)
- Study the `check_for_tampering()` function
- Understand how it detects unusual patterns in sensor data

## Attack Demonstrations

### 1. Eavesdropping Attack
Run the message sniffer and observe:
- How unencrypted messages can be easily intercepted
- How encrypted messages protect confidentiality

### 2. Spoofing Attack
Run the message spoofer and observe:
- How attackers can send false data to trigger incorrect actions
- How message signing prevents acceptance of spoofed messages

### 3. MITM Attack
Run the MITM attacker and observe:
- How attackers can intercept and modify messages in transit
- How encryption and message signing prevent successful tampering

## Exercises

### Exercise 1: Analyze Attack Logs
1. Run the attacks and security monitor
2. Look at the logs in the `logs/` directory
3. Identify which attacks were successful and which were prevented

### Exercise 2: Security Enhancement
Identify a security weakness in the current implementation and suggest an improvement. Consider:
- Key management improvements
- Adding additional authentication methods
- Implementing access control

### Exercise 3: Security Trade-offs
Analyze the trade-offs between security and performance:
- How does adding encryption affect message processing time?
- How does requiring signatures affect system responsiveness?
- What happens if authentication fails?

## Resources for Further Learning

- [OWASP IoT Top 10](https://owasp.org/www-project-internet-of-things-top-10/)
- [NIST IoT Security](https://www.nist.gov/programs-projects/nist-cybersecurity-iot-program)
- [IoT Security Foundation](https://www.iotsecurityfoundation.org/)
- [Cryptography in Python](https://cryptography.io/en/latest/)

## Troubleshooting

### Common Issues

1. **Cannot connect to RabbitMQ**
   - Check your internet connection
   - Verify your CloudAMQP credentials in the `.env` file
   - Make sure your CloudAMQP free tier limits haven't been exceeded

2. **Dashboard not showing data**
   - Make sure the secure web server is running
   - Check the web server logs for errors
   - Verify the dashboard is connecting to the correct URL (http://localhost:5001)

3. **Security monitor not detecting attacks**
   - Make sure both the attack simulation and security monitor are running
   - Check logs to see if the monitor is properly connected to the right exchanges

### Getting Help

If you're having trouble with the demonstration, try:
1. Checking the log files in the `logs/` directory
2. Looking at the standard output of the running processes
3. Asking your instructor or TA for assistance 