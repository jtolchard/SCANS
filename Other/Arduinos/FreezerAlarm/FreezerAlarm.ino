#include <Wire.h>
#include <SPI.h>
#include <Ethernet.h>

// Ethernet settings
// The mac-address of the ethernet shield
byte mac[] = { 0xA8, 0x61, 0x0A, 0xAF, 0x13, 0xF9 };
// A hard coded IP address of your choice
IPAddress ip(192, 168, 103, 55);
EthernetServer server(80);

// FREEZER 1 ALARMS
int low = 2;
int high = 3;
int f1_com = 4;
int alarm1_1 = 5;
int alarm1_2 = 6;
String alarm1_status;

// FREEZER 2 ALARMS
int f2_com = 7;
int alarm2_1 = 8;
int alarm2_2 = 9;
String alarm2_status;

void setup() {
  // Initialize Serial for debugging
  Serial.begin(9600);

  // Initialize peripherals
  //Wire.begin();
  Ethernet.begin(mac, ip);
  server.begin();

  Serial.print("Server IP address: ");
  Serial.println(Ethernet.localIP());

  //Set pins for Freezer 1 alarm
  pinMode(low, OUTPUT);  
  pinMode(high, OUTPUT);
  digitalWrite(low, LOW);
  digitalWrite(high, HIGH);
  pinMode(f1_com, INPUT);
  pinMode(alarm1_1, OUTPUT);  
  pinMode(alarm1_2, OUTPUT); 
  
  //Set pins for Freezer 2 alarm
  //pinMode(f2_0v, OUTPUT);  
  //pinMode(f2_5v, OUTPUT);
  //digitalWrite(f2_0v, LOW);
  //digitalWrite(f2_5v, HIGH);
  pinMode(f2_com, INPUT);
  pinMode(alarm2_1, OUTPUT);  
  pinMode(alarm2_2, OUTPUT); 

}

void loop() {
  
  delay(1000);

  if (digitalRead(f1_com) == HIGH) {
    digitalWrite(alarm1_1, LOW);
    digitalWrite(alarm1_2, HIGH);
    alarm1_status = "\"ERROR\"";
  } else if (digitalRead(f1_com) == LOW) {
    digitalWrite(alarm1_1, HIGH);
    digitalWrite(alarm1_2, LOW);
    alarm1_status = "\"OK\"";
  }

  if (digitalRead(f2_com) == HIGH) {
    digitalWrite(alarm2_1, LOW);
    digitalWrite(alarm2_2, HIGH);
    alarm2_status = "\"ERROR\"";
  } else if (digitalRead(f2_com) == LOW) {
    digitalWrite(alarm2_1, HIGH);
    digitalWrite(alarm2_2, LOW);
    alarm2_status = "\"OK\"";
  }

  Serial.print("Alarm 1: ");
  Serial.println(alarm1_status);

  Serial.print("Alarm 2: ");
  Serial.println(alarm2_status);


  EthernetClient client = server.available();
  // Handle incoming HTTP requests
  if (client) {
    processRequest(client);
    delay(1);
    client.stop();
  }

}

// function upon receiving an HTTP connection
void processRequest(EthernetClient client) {

  // Prepare the HTTP response
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: application/json\r\n\r\n";
  response += "{";
  response += "\"Freezer_1_status\": ";
  response += String(alarm1_status);
  response += ", \"Freezer_2_status\": ";
  response += String(alarm2_status);
  response += "}";

  // Send the HTTP response
  client.println(response);
}
