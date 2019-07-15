#include <ESP8266WiFi.h>
#include <SPI.h>
#include <MFRC522.h>
#include <String.h> 


#define SS_PIN D4 
#define RST_PIN D3 

const char *ssid = "AP-22-2G";
const char *password = "12345678";


char host[] = "47522a0a.ngrok.io";


MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  delay(10);
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
 

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
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

int value = 0;

void loop() {
  delay(5000);
  ++value;

  Serial.print("connecting to ");
  Serial.println(host);
  
  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 80;
  if (!client.connect(host,httpPort)) {
    Serial.println("connection failed");
    client.println("Connected!");
    return;
  }
  
  // We now create a URI for the request
  String url = "/rfid?cardId=";
//  url += streamId;
//  url += "?private_key=";
//  url += privateKey;
//  url += "&value=";
//  url += value;
  

  // This will send the request to the server
    if ( ! mfrc522.PICC_IsNewCardPresent()) {
      return;
    }

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Dump debug info about the card; PICC_HaltA() is automatically called
  String content= "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {  
     String temp="";
     temp.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     temp.concat(String(mfrc522.uid.uidByte[i], HEX));
     content.concat(temp);
  }
   mfrc522.PICC_HaltA();
   content.replace(" ", "");
   Serial.print(content);
   url = url + content;
   client.print(String("GET ") + url+ " HTTP/1.1\r\n" +"Host: " + host + "\r\n" + "Connection: close\r\n\r\n");

  
  
  int timeout = millis() + 3000;
  while (client.available() == 0) {
    if (timeout - millis() < 0) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      return;
    }
  }
   while(client.available()){
    String line = client.readStringUntil('\r');
    Serial.print(line);
  }
  // Read all the lines of the reply from server and print them to Serial
  
  Serial.println();
  Serial.println("closing connection");
}
