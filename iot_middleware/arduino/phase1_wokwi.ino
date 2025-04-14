#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

// Pin definitions
#define DHTPIN 15        // GPIO15 for DHT sensor (changed from GPIO2)

// WiFi and MQTT settings
const char* ssid = "Wokwi-GUEST";         // Wokwi WiFi SSID
const char* password = "";                 // No password needed for Wokwi
const char* mqtt_server = "broker.emqx.io";  // Changed to EMQX broker
const char* temp_topic = "home/temp";      // Publish topic

// Initialize DHT sensor
DHTesp dhtSensor;

// Initialize WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5001);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Initialize DHT sensor
  dhtSensor.setup(DHTPIN, DHTesp::DHT22);
  
  // Setup WiFi and MQTT
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  
  Serial.println("Setup complete");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 5001) {
    lastMsg = now;
    
    // Read temperature and humidity
    float temperature = dhtSensor.getTemperature();
    float humidity = dhtSensor.getHumidity();
    
    // Check if readings are valid
    if (!isnan(temperature) && !isnan(humidity)) {
      // Create message string
      snprintf(msg, MSG_BUFFER_SIZE, "%.1f,%.1f", temperature, humidity);
      
      Serial.print("Publishing temperature and humidity: ");
      Serial.println(msg);
      
      // Publish to MQTT topic
      client.publish(temp_topic, msg);
    } else {
      Serial.println("Failed to read from DHT sensor!");
    }
  }
} 