#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>  // Include the ArduinoJson library
#include <WiFiClientSecure.h> // Include the WiFiClientSecure library
#include <Ultrasonic.h>

const int trigPin = D4;   
const int echoPin = D5; 

#define MIN_DISTANCE 200 // Minimum distance in cm (1 meter)
#define TIME_THRESHOLD 10000 // Time threshold in milliseconds (10 seconds)

#define STASSID "Redmi Note 8"
#define STAPSK "edf18440121a"

const char* ssid = STASSID;
const char* password = STAPSK;

Ultrasonic ultrasonic(trigPin, echoPin);
unsigned long startTime = 0; // To track the start time
bool carDetected = false;
bool lastState = false; // To track the last state of car detection

WiFiClientSecure wifiClient; // Add this line

void setup() {
  Serial.begin(115200);

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  wifiClient.setInsecure(); // Use this if you don't have the SSL certificate

  /* Explicitly set the ESP8266 to be a WiFi-client, otherwise, it by default,
     would try to act as both a client and an access-point and could cause
     network-issues with your other WiFi-devices on your WiFi-network. */
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    float cmMsec = ultrasonic.read(CM);

    Serial.print("Distância: ");
    Serial.print(cmMsec);
    Serial.print(" cm");
    Serial.print("\n");
    delay(1000);

    // Check if distance is less than 1 meter
    if (cmMsec <= MIN_DISTANCE) {
      if (startTime == 0) { // Start the timer if not already started
        startTime = millis();
      } else if (millis() - startTime >= TIME_THRESHOLD) { // Check if the time threshold is reached
        carDetected = true;
        Serial.print("Carro detectado!");
      }
    } else {
      startTime = 0; // Reset the timer if the distance is more than 1 meter
      carDetected = false;
      Serial.print("Carro NÃO detectado!");
    }

    // Check if car detection state has changed
    if (carDetected != lastState) {
      lastState = carDetected;
      HTTPClient http;

      String url = carDetected ? "https://southcarpark-api.onrender.com/Entrou" : "https://southcarpark-api.onrender.com/Saiu";
      http.begin(wifiClient, url);  // Use the determined URL
      http.addHeader("Content-Type", "application/json");

      // Create JSON object
      DynamicJsonDocument json(1024);
      json["Vagaid"] = 3;

      String payload;
      serializeJson(json, payload);

      // Send POST request with JSON payload
      int httpCode = http.POST(payload);

      // Debugging
      if (httpCode > 0) {
        String response = http.getString();
        Serial.println(httpCode);
        Serial.println(response);
      } else {
        Serial.println("Error on HTTP request");
      }

      http.end(); //Close connection
    }

    // Print the status
    Serial.print("Distance: ");
    Serial.print(cmMsec);
    Serial.print(" cm - Car Detected: ");
    Serial.println(carDetected ? "True" : "False");
  } else {
    Serial.println("WiFi not connected");
  }

  delay(1000);
}
