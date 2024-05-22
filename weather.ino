#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <deque>

#define DHT_SENSOR_PIN 4
#define DHT_SENSOR_TYPE DHT22

DHT dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

const char* ssid1 = "";
const char* password1 = "";
const char* ssid2 = "";
const char* password2 = "";

#define API_KEY "AIzaSyBPKchBPeBoAaNcYdzTUR2ZjI2itc4p5ks"
#define DATABASE_URL "temprh-36591-default-rtdb.asia-southeast1.firebasedatabase.app"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;
unsigned long wifiCheckPrevMillis = 0;
unsigned long wifiDisconnectedSince = 0;
bool signupOK = false;
bool usingSSID1 = true;

float tempSum = 0, humSum = 0;
float tempMin = 1000, tempMax = -1000;
float humMin = 1000, humMax = -1000;
int count = 0;

// NTP Client setup
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 25200, 60000); // zona waktu WIB (UTC+7)


struct SensorData {
  float temperature;
  float humidity;
  unsigned long timestamp;
};

std::deque<SensorData> dataBuffer;

void connectToWiFi(const char* ssid, const char* password) {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();
}

void setup() {
  dht_sensor.begin();
  Serial.begin(115200);

  connectToWiFi(ssid1, password1);

  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("ok");
    signupOK = true;
  } else {
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  config.token_status_callback = tokenStatusCallback;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  timeClient.begin();


  if (Firebase.RTDB.getFloat(&fbdo, "DHT_11/Stats/TempSum")) {
    tempSum = fbdo.floatData();
  }
  if (Firebase.RTDB.getFloat(&fbdo, "DHT_11/Stats/HumSum")) {
    humSum = fbdo.floatData();
  }
  if (Firebase.RTDB.getInt(&fbdo, "DHT_11/Stats/Count")) {
    count = fbdo.intData();
  }
  if (Firebase.RTDB.getFloat(&fbdo, "DHT_11/Stats/TempMin")) {
    tempMin = fbdo.floatData();
  }
  if (Firebase.RTDB.getFloat(&fbdo, "DHT_11/Stats/TempMax")) {
    tempMax = fbdo.floatData();
  }
  if (Firebase.RTDB.getFloat(&fbdo, "DHT_11/Stats/HumMin")) {
    humMin = fbdo.floatData();
  }
  if (Firebase.RTDB.getFloat(&fbdo, "DHT_11/Stats/HumMax")) {
    humMax = fbdo.floatData();
  }
}

void updateStats(float temperature, float humidity) {
  tempSum += temperature;
  humSum += humidity;
  if (temperature < tempMin) tempMin = temperature;
  if (temperature > tempMax) tempMax = temperature;
  if (humidity < humMin) humMin = humidity;
  if (humidity > humMax) humMax = humidity;
  count++;
}

void resetStats() {
  tempSum = 0;
  humSum = 0;
  tempMin = 1000;
  tempMax = -1000;
  humMin = 1000;
  humMax = -1000;
  count = 0;
}

void sendDataToFirebase(float temperature, float humidity) {
  if (Firebase.RTDB.setInt(&fbdo, "DHT_11/Temperature", temperature)) {
    Serial.print("Temperature : ");
    Serial.println(temperature);
  } else {
    Serial.println("Failed to Read from the Sensor");
    Serial.println("REASON: " + fbdo.errorReason());
  }

  if (Firebase.RTDB.setFloat(&fbdo, "DHT_11/Humidity", humidity)) {
    Serial.print("Humidity : ");
    Serial.println(humidity);
  } else {
    Serial.println("Failed to Read from the Sensor");
    Serial.println("REASON: " + fbdo.errorReason());
  }

  if (Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/TempAverage", tempSum / count) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/TempMin", tempMin) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/TempMax", tempMax) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/HumAverage", humSum / count) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/HumMin", humMin) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/HumMax", humMax) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/TempSum", tempSum) &&
      Firebase.RTDB.setFloat(&fbdo, "DHT_11/Stats/HumSum", humSum) &&
      Firebase.RTDB.setInt(&fbdo, "DHT_11/Stats/Count", count)) {
    Serial.println("Statistics updated successfully.");
  } else {
    Serial.println("Failed to update statistics.");
    Serial.println("REASON: " + fbdo.errorReason());
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    if (wifiDisconnectedSince == 0) {
      wifiDisconnectedSince = millis();
    } else if (millis() - wifiDisconnectedSince > 5000) {
      Serial.println("Wi-Fi disconnected for more than 5 seconds, trying to reconnect...");
      wifiDisconnectedSince = millis();
      usingSSID1 = !usingSSID1;
      if (usingSSID1) {
        connectToWiFi(ssid1, password1);
      } else {
        connectToWiFi(ssid2, password2);
      }
    }
  } else {
    wifiDisconnectedSince = 0;
  }

  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  struct tm *ptm = gmtime((time_t *)&epochTime);

  float temperature = dht_sensor.readTemperature();
  float humidity = dht_sensor.readHumidity();

  if (Firebase.ready() && signupOK && (millis() - sendDataPrevMillis > 1000 || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    if (WiFi.status() == WL_CONNECTED) {
      sendDataToFirebase(temperature, humidity);

      while (!dataBuffer.empty()) {
        SensorData bufferedData = dataBuffer.front();
        sendDataToFirebase(bufferedData.temperature, bufferedData.humidity);
        dataBuffer.pop_front();
      }
    } else {
      SensorData newData = { temperature, humidity, epochTime };
      dataBuffer.push_back(newData);
      Serial.println("Data buffered due to Wi-Fi disconnection.");
    }

    updateStats(temperature, humidity);

    if (ptm->tm_hour == 0 && ptm->tm_min == 0 && ptm->tm_sec < 2) {
      resetStats();
    }
  }
}
