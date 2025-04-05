#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Pin definitions
#define DHTPIN 2        // GPIO2 for DHT sensor
#define DHTTYPE DHT11   // DHT11 or DHT22
#define BUZZER 5        // GPIO5 for buzzer
#define LED 13          // GPIO13 for LED

// Wi-Fi and MQTT settings
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "broker.hivemq.com";
const char* temp_topic = "home/temp";      // Publish topic
const char* cmd_topic = "home/cmd";        // Subscribe topic

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER, OUTPUT);
  pinMode(LED, OUTPUT);
  dht.begin();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Connect to MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  if (message == "ALERT_ON") {
    digitalWrite(LED, HIGH);
    tone(BUZZER, 1000, 500); // 1000 Hz for 0.5s
  } else if (message == "ALERT_OFF") {
    digitalWrite(LED, LOW);
    noTone(BUZZER);
  }
  Serial.println("Command: " + message);
}

void reconnect() {
  while (!client.connected()) {
    String clientId = "NanoESP32-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      client.subscribe(cmd_topic);
      Serial.println("MQTT connected");
    } else {
      Serial.println("MQTT failed, retrying...");
      delay(2000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read and publish sensor data every 5 seconds
  float temp = dht.readTemperature();
  float humid = dht.readHumidity();
  if (!isnan(temp) && !isnan(humid)) {
    String payload = String(temp) + "," + String(humid);
    client.publish(temp_topic, payload.c_str());
    Serial.println("Published: " + payload);
  }
  delay(5000);
} 