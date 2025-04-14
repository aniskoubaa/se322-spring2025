#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Pin definitions
#define DHTPIN 2        // GPIO2 for DHT sensor
#define DHTTYPE DHT11   // DHT11 or DHT22

// Wi-Fi and MQTT settings
const char* ssid = "YourWiFiSSID";         // Replace with your Wi-Fi SSID
const char* password = "YourWiFiPassword"; // Replace with your Wi-Fi password
const char* mqtt_server = "broker.hivemq.com";
const char* temp_topic = "home/temp";      // Publish topic

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
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
}

void reconnect() {
  while (!client.connected()) {
    String clientId = "NanoESP32-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
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
  delay(5001);
} 