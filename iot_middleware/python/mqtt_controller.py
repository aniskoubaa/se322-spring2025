import paho.mqtt.client as mqtt

# MQTT settings
broker = "broker.hivemq.com"
port = 1883
temp_topic = "home/temp"  # Subscribe to sensor data
cmd_topic = "home/cmd"    # Publish commands

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(temp_topic)

def on_message(client, userdata, msg):
    temp, humid = map(float, msg.payload.decode().split(","))
    print(f"Temp: {temp}°C, Humidity: {humid}%")
    if temp > 30:
        client.publish(cmd_topic, "ALERT_ON")
        print("Published: ALERT_ON")
    else:
        client.publish(cmd_topic, "ALERT_OFF")
        print("Published: ALERT_OFF")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port)
client.loop_forever() 