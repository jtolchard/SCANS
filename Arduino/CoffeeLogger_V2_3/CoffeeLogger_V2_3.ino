/*
  Coffee Logging Arduino V2

 Disclaimer:
  THAR BE BODGES AHEAD 
  1) This project uses a wifi UNO board AND an ethernet shield because I didn't realise my location only had enterprise wifi, to which the wifi board won't connect; necessitating the ethernet shield. But..
  2) The Ethernet shield uses and obscures the SPI header, making access for the RFID reader impossible. If it weren't for the old RFID1 library (see link below), this wouldn't work with the standard MFC522 library.
  3) Google scripts webhooks require SSL/HTTPS encryption, which - it turns out - my (avr) UNO board cannot cope with. This therefore makes a custom/IoT Proxy necessary. I made my own with python but tools like https://io.adafruit.com/ might work better for you in this situation. 

 Circuit:
  Uno WiFi Rev.2 board & Ethernet shield rev 2 (no thanks to WPA2-Enterprise Wifi)
  Green LEDs attached to pins 11 + 12
  Yellow LED attached to pin 13
  Piezo buzzer attached to pin 8

  RFID-RC522 board. 
  Due to Ethernet shield, the SPI header was not available, so used rfid1 library with fully customizable pins
  Thank you Michael! (https://arduino.stackexchange.com/questions/8743/use-rfid-rc522-with-other-pins)
    - Ground and 3.3V directly attached to Arduino power pins
    - IRQ pin attached to Arduino pin 2
    - SCK pin attached to Arduino pin 3
    - MOSI pin attached to Arduino pin 4
    - MISO pin attached to Arduino pin 5
    - SDA/NSS pin attached to Arduino pin 6
    - RST pin attached to Arduino pin 7
 */

//#############################################################################
//############################## BASE PARAMETERS ##############################
//#############################################################################

// Libraries
#include <SPI.h>
#include <Ethernet.h>
#include <ArduinoHttpClient.h> 
#include"rfid1.h"

// Google sheets connection details
char server[] = "script.google.com";
String webhook = "AKfycbyHBXlsxBw4fXBuWD1N9LowE_yDaxpIKkZP9UwVOZywSFMtPhKaWuMPsbTUiRzbuEO0";

// Proxy settings
byte proxyServer[] = { 192, 168, 103, 10 }; // This is the proxy server
int proxyPort = 777; // The port for the proxy server

// Ethernet settings
byte mac[] = { 0xA8, 0x61, 0x0A, 0xAE, 0xBD, 0x70 };
IPAddress ip(192, 168, 103, 111);
EthernetClient client;
HttpClient http(client, proxyServer, proxyPort);

// Pin settings
const int networkCheck = 13;   // LED 13 = Yellow Network Status
const int networkOn = 12;   // LED 12 = Green Network Status
const int readOk = 11;      // LED 11 = Card Reader Light
const int buzzer = 8;       // buzzer to arduino pin 8

// Set cardReader parameters
RFID1 rfid;
uchar serNum[5];  // array to store your ID

//Counter to help in regular reset of RFID card
int counter = 0;

//#############################################################################
//############################### MAIN FUNCTIONS ##############################
//#############################################################################

String silentMode = "NO"; //YES OR NO

void setup() {
  // Initialize Network connection
  Ethernet.begin(mac, ip);

  // Initialize Serial for debugging
  Serial.begin(9600);
  Serial.println("##########");
  Serial.print("Coffee Logger IP address: ");
  Serial.println(Ethernet.localIP());

  // Reset all o/p pins
  pinMode(networkCheck, OUTPUT);
  pinMode(networkOn, OUTPUT);  
  pinMode(readOk, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  // Test connected devices
  Serial.println("Initialising components..");
  // Test all LEDs + buzzer
  if (silentMode != "YES") {
    initPulse();
  }

  // Test network connection possible  
  networkTest();

  // Initialise RFID reader
  initRfidReader();
  //rfid.begin(2, 3, 4, 5, 6, 7);  //(IRQ,SCK,MOSI,MISO,NSS,RST);
  //delay(100);
  //Serial.println("Connecting to card reader.");
  //rfid.init();
}

void loop() {
  
  if (counter == 200)
  {
  Serial.println("Resetting Card");;
  initRfidReader();
  counter = 0;
  }
  else
  {
  counter++;
  }


  //Each loop, check if a cable is attached and run network test upon reconnection
  networkStatus();
    
  //Identify and print card ID
  uchar status;
  uchar str[MAX_LEN];
  status = rfid.request(PICC_REQIDL, str);
  if (status != MI_OK)
  {
    return;
  }
  
  //rfid.showCardType(str);
  status = rfid.anticoll(str);

  if (status == MI_OK)
  {
    memcpy(serNum, str, 5);
    String cardID = hexToString(serNum, 4);
    Serial.println("----------");
    Serial.print("The card's number is: " + cardID);
    Serial.println();
    delay(150);
    if (silentMode != "YES") {
      cardBeep();
    }
    sendHttpPostRequest(cardID);
  }
  delay(1500);
  rfid.halt(); //command the card into sleep mode 
}


//#############################################################################
//############################## MINOR FUNCTIONS ##############################
//#############################################################################

// A small function to pulse all the LEDS and buzzer as an initialization check
void initPulse(){
  digitalWrite(networkCheck, HIGH);
  digitalWrite(networkOn, HIGH);
  digitalWrite(readOk, HIGH); 
  tone(buzzer, 800);
  delay(60);
  noTone(buzzer);
  digitalWrite(networkCheck, LOW);
  digitalWrite(networkOn, LOW);
  digitalWrite(readOk, LOW); 
}

// Blink an LED on and off every 1/4 second until a count has been reached
void blink(int count) {
    while ( count-- ) {
      digitalWrite(networkCheck, HIGH);
      delay(250);
      digitalWrite(networkCheck, LOW);
      delay(250);
    }
}

// Set status lights based on ethernet connection
void networkStatus(){
  if (Ethernet.linkStatus() != 1) {
    Serial.println("Check network connection...");
    while (Ethernet.linkStatus() != 1){
      digitalWrite(networkOn, LOW);
      blink(2);
    }
    networkTest();
  } else {
    digitalWrite(networkOn, HIGH);
  }
}

void networkTest(){
  Serial.println("Testing network connection");
  int test = 0;
  while (test != 1) {
    test = client.connect(proxyServer, proxyPort);
   blink(2);
  }

  Serial.print("Connection to ");
  Serial.print(client.remoteIP());
  Serial.println(" OK");
  client.stop();
  Serial.println("##########");
}

void sendHttpPostRequest(String cardID) {
  HttpClient http(client, proxyServer, proxyPort);

  delay(1000);
  Serial.println("Sending card id: "+cardID+" to proxy");
  String data = "url=https://script.google.com/macros/s/AKfycbyDJe4fseo9GXCcTllAHmZ89QakbjZ1_PBLUd28GDKeKl9beXJegCDdKy8xXlqfUWi0/exec?card_no=" + cardID;

  http.post("/forward", "application/x-www-form-urlencoded", data);

  int statusCode = http.responseStatusCode();

  if (statusCode == -2) {
    Serial.println("Status code -2. Failed to send HTTP GET request.");
    if (silentMode != "YES") {
      ohOhBuzz();
    }

  }

/*
  if (http.post("/forward", "application/x-www-form-urlencoded", data)) {
    int statusCode = http.responseStatusCode();


    if (statusCode == -2) {
    Serial.println("NULL");
    } else {
    Serial.println("BAHH");
    Serial.println(statusCode);
    }
     



    if (statusCode == 200) {
      Serial.println("HTTP GET request sent successfully!");
      String response = http.responseBody();
      //Serial.println("Response: " + response);
      Serial.println("xx");
    } else {
      Serial.print("HTTP GET request failed with status code: ");
      Serial.println(statusCode);
      ohOhBuzz();
    }
  } else {
    Serial.println("Failed to send HTTP GET request.");
    ohOhBuzz();
  }

*/  
  Serial.println("----------");
  http.stop();
}

// Generate a piezo-beep and flash an LED for 1 second
void cardBeep(){
  digitalWrite(readOk, HIGH); 
  tone(buzzer, 800);
  delay(60);
  tone(buzzer, 1200);
  delay(60);
  noTone(buzzer);
  digitalWrite(readOk, LOW);
}

// Generate a bad piezo-beep
void ohOhBuzz(){
  digitalWrite(readOk, LOW); 
  digitalWrite(networkCheck, HIGH);
  tone(buzzer, 700);
  delay(160);
  tone(buzzer, 666);
  delay(200);
  tone(buzzer, 632);
  delay(450);
  noTone(buzzer);
  digitalWrite(networkCheck, LOW);
}

// Create a string of characters from the card ID hex
String hexToString(byte *buffer, byte bufferSize) {
  String hexString = "";
  for (byte i = 0; i < bufferSize; i++) {
    if(buffer[i] < 0x10) {
      hexString += "0";
    }
    hexString += String(buffer[i], HEX);
  }
  return hexString;
}

void initRfidReader(){
  // Initialise RFID reader
  rfid.begin(2, 3, 4, 5, 6, 7);  //(IRQ,SCK,MOSI,MISO,NSS,RST);
  delay(100);
  Serial.println("Connecting to card reader.");
  Serial.println("----------");
  rfid.init();
}
