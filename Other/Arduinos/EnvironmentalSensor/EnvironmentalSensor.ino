#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <SPI.h>
#include <TimeLib.h>
#include <Ethernet.h>
#include <LiquidCrystal_I2C.h>
#include <NTPClient.h>

// BME280 sensor setup
Adafruit_BME280 bme;
#define SEALEVELPRESSURE_HPA (1013.25)

// Ethernet settings
// The mac-address of the ethernet shield
byte mac[] = { 0xA8, 0x61, 0x0A, 0xAE, 0xBD, 0x42 };
// A hard coded IP address of your choice
IPAddress ip(192, 168, 103, 20);
EthernetServer server(80);

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 4);

// NTP setup
EthernetUDP udp;
NTPClient timeClient(udp, "193.52.184.106"); //points to > pool.ntp.org
const int timeZoneOffset = 2 * 3600; // 2 = GMT + 2 for France

void setup() {
  // Initialize Serial for debugging
  Serial.begin(9600);

  // Initialize peripherals
  Wire.begin();
  bme.begin();

  Ethernet.begin(mac, ip);
  server.begin();

  lcd.begin(16, 4); // Initialize the LCD with 16 columns and 4 rows
  lcd.backlight();  // Turn on the backlight

  Serial.print("Server IP address: ");
  Serial.println(Ethernet.localIP());

  // Initialize NTP
  timeClient.begin();
  timeClient.forceUpdate();
  timeClient.setTimeOffset(timeZoneOffset);
}

void loop() {
  // Handle incoming HTTP requests
  EthernetClient client = server.available();

  if (client) {
    processRequest(client);
    delay(1);
    client.stop();
  }

  // Update sensor readings
  float temperature = bme.readTemperature();
  float humidity = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0F;

  // Update NTP time
  timeClient.update();
  
  // Format the date & time
  time_t utcCalc = timeClient.getEpochTime();
  Serial.println(utcCalc);
  char timeStamp[40];
  sprintf(timeStamp, "%02d:%02d %02d/%02d/%02d", hour(utcCalc), minute(utcCalc), day(utcCalc), month(utcCalc), year(utcCalc) % 100);

  //If no network time is found, show a warning.
  String topLine;
  //If network time will be wrong, print that the network is down
  if (String(year(utcCalc)) == "1970") {
    topLine = "** Check Network **";
  } else {
    topLine = "CRMN "+String(timeStamp);
  };

  // Clear the LCD screen
  // N.B: This leads to an annoying flicker, but if you're fully changing what's on a line, it is necessary
  //lcd.clear();

  // Display information on the LCD
  lcd.setCursor(0, 0);
  lcd.print(topLine);

  lcd.setCursor(0, 1);
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print(" \xDF""C");

  lcd.setCursor(0, 2);
  lcd.print("Humidity: ");
  lcd.print(humidity);
  lcd.print(" %");

  lcd.setCursor(0, 3);
  lcd.print("Press: ");
  lcd.print(pressure);
  lcd.print(" hPa");

  delay(10000); // Refresh delay for the LCD display
}

// function upon receiving an HTTP connection
void processRequest(EthernetClient client) {
  // Read sensor data
  float temperature = bme.readTemperature();
  float humidity = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0F;

  // Prepare the HTTP response
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: application/json\r\n\r\n";
  response += "{";
  response += "\"temperature\": ";
  response += String(temperature);
  response += ", \"humidity\": ";
  response += String(humidity);
  response += ", \"pressure\": ";
  response += String(pressure);
  response += "}";

  // Send the HTTP response
  client.println(response);
}
