#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random
import json
from datetime import datetime

class ArduinoEmulator:
    def __init__(self):
        # MQTT Settings
        self.broker = "broker.emqx.io"
        self.port = 1883
        self.temp_topic = "home/temp"
        self.cmd_topic = "home/cmd"
        
        # Simulated sensor settings
        self.base_temperature = 25.0  # Base temperature in Celsius
        self.base_humidity = 50.0     # Base humidity in %
        self.temp_variation = 2.0     # Maximum temperature variation
        self.humid_variation = 5.0    # Maximum humidity variation
        
        # Initialize MQTT client with protocol version 5
        client_id = f"ArduinoEmulator-{random.randint(1000, 9999)}"
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Connect to broker
        print(f"Connecting to MQTT broker {self.broker}...")
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect to broker: {e}")
            raise

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print("Connected to MQTT broker!")
            # Subscribe to command topic for Phase 2
            self.client.subscribe(self.cmd_topic)
        else:
            print(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback when message is received (for Phase 2)"""
        try:
            command = msg.payload.decode()
            print(f"Received command: {command}")
            if command == "ALERT_ON":
                print("🔔 Alert ON - Would activate buzzer and LED")
            elif command == "ALERT_OFF":
                print("🔕 Alert OFF - Would deactivate buzzer and LED")
        except Exception as e:
            print(f"Error processing message: {e}")

    def generate_sensor_data(self):
        """Generate simulated sensor readings"""
        # Add some random variation to base values
        temperature = self.base_temperature + random.uniform(-self.temp_variation, self.temp_variation)
        humidity = self.base_humidity + random.uniform(-self.humid_variation, self.humid_variation)
        
        # Ensure values are within realistic ranges
        temperature = round(max(min(temperature, 50.0), -10.0), 1)
        humidity = round(max(min(humidity, 100.0), 0.0), 1)
        
        return temperature, humidity

    def simulate_manual_temperature_change(self, change):
        """Manually adjust base temperature (for testing alerts)"""
        self.base_temperature += change
        print(f"Base temperature adjusted to: {self.base_temperature}°C")

    def run(self):
        """Main loop to emulate Arduino behavior"""
        print("\nArduino Emulator Running!")
        print("Commands:")
        print("  Press Ctrl+C to exit")
        print("  Press 'w' + Enter to warm up sensor")
        print("  Press 'c' + Enter to cool down sensor")
        print("\nPublishing sensor data every 5 seconds...\n")
        
        try:
            while True:
                # Generate and publish sensor data
                temperature, humidity = self.generate_sensor_data()
                payload = f"{temperature},{humidity}"
                
                # Publish to MQTT
                self.client.publish(self.temp_topic, payload)
                print(f"{datetime.now().strftime('%H:%M:%S')} - Published: Temperature: {temperature}°C, Humidity: {humidity}%")
                
                # Check for user input (non-blocking)
                try:
                    import sys, select
                    if select.select([sys.stdin], [], [], 0)[0]:
                        user_input = sys.stdin.readline().strip().lower()
                        if user_input == 'w':
                            self.simulate_manual_temperature_change(5.0)
                        elif user_input == 'c':
                            self.simulate_manual_temperature_change(-5.0)
                except:
                    pass  # Ignore if running in an environment without stdin
                
                time.sleep(5)  # Wait 5 seconds between readings

        except KeyboardInterrupt:
            print("\nStopping emulator...")
            self.client.loop_stop()
            self.client.disconnect()
            print("Emulator stopped.")

if __name__ == "__main__":
    try:
        emulator = ArduinoEmulator()
        emulator.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Emulator failed to start. Please check your network connection and try again.") 