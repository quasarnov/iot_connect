# IoT Connect
## Overview
IoT Connect is a project designed to facilitate the collection and transmission of data from IoT devices to a central server. This README provides details on how to use the API to fetch and send data.
## Getting Started
### Prerequisites
- An IoT device with internet connectivity.
- Access to the server where IoT Connect is hosted.
### Installation
Clone the IoT Connect repository:
```
git clone https://github.com/quasarnov/iot_connect.git
```
# API Usage
## Fetching Data
To fetch data from your devices, use the following endpoint:
GET /api/measurements/<device_serial>/<start_date>/<end_date>/
### Parameters:
```
device_serial: Serial number of the device.
start_date and end_date: Date and time in the format YYYY-MM-DDTHH:MM.
```
### Example:

JavaScript (using Fetch API):
```
fetch('/api/measurements/device_serial/2023-01-01T00:00/2023-01-31T23:59/', {
    method: 'GET',
    headers: {
        'Authorization': 'Token b931e56159f1cbe6d69397d61fbcef7d06221335'
    }
}).then(response => response.json())
.then(data => console.log(data));
```
Python (using requests library):
```
import requests

url = 'http://yourserver.com/api/measurements/device_serial/2023-01-01T00:00/2023-01-31T23:59/'
headers = {'Authorization': 'Token b931e56159f1cbe6d69397d61fbcef7d06221335'}
response = requests.get(url, headers=headers)
data = response.json()
print(data)
```
### Sending Data
To send data to the server, use this endpoint:
POST /api/receive-iot/
### Example:
- JavaScript (using Fetch API):
```
fetch('/api/receive-iot/', {
    method: 'POST',
    headers: {
        'Authorization': 'Token b931e56159f1cbe6d69397d61fbcef7d06221335',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        serial: 'DEVICE_SERIAL',
        values: [23.5, 48.7]  // Example values
    })
}).then(response => response.json())
.then(data => console.log(data));
```
- Python (using requests library):
```
import requests

url = 'http://yourserver.com/api/receive-iot/'
headers = {
    'Authorization': 'Token b931e56159f1cbe6d69397d61fbcef7d06221335',
    'Content-Type': 'application/json'
}
data = {
    'serial': 'DEVICE_SERIAL',
    'values': [23.5, 48.7]  // Example values
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```
- ESP32 Example : 
```
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <WiFi.h>
#include <HTTPClient.h>

// BME280 sensor pins
#define SDA_PIN 18
#define SCL_PIN 19

// WiFi credentials
const char* ssid = "<your ssid>";
const char* password = "<password>";

// Server details
const char* serverName = "<server name>/api/receive-iot/";
String serialNumber = "<DEVICE_SERIAL>";

Adafruit_BME280 bme; // Create an instance of the BME280 class

void setup() {
  Serial.begin(115200);

  // Initialize the I2C communication for BME280
  Wire.begin(SDA_PIN, SCL_PIN);

  // Initialize the BME280
  if (!bme.begin(0x76)) {  // Change to 0x77 if needed
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  Serial.println("BME280 sensor found!");

  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Read sensor values
    float temperature = bme.readTemperature();
    float humidity = bme.readHumidity();
    float pressure = bme.readPressure() / 100.0F;

    // Construct the JSON payload
    String values = "[" + String(temperature) + ", " + String(humidity) + ", " + String(pressure) + "]";
    String httpRequestData = "{\"serial\":\"" + serialNumber + "\", \"values\":" + values + "}";

    // Send the data to the server
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Token b931e56159f1cbe6d69397d61fbcef7d06221335");

    int httpResponseCode = http.POST(httpRequestData);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

  delay(30000); // Send data every 30 seconds
}
```
Replace 'DEVICE_SERIAL' with your device's actual serial number and adjust values accordingly.
