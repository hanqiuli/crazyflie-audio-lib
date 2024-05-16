#include <Arduino.h>
#include <SoftwareSerial.h>

// Define SoftwareSerial RX and TX pins
#define RX_PIN D9
#define TX_PIN D10

// Create a SoftwareSerial object
SoftwareSerial softSerial(RX_PIN, TX_PIN);

void setup() {
  // Start the hardware serial at 115200 baud rate for monitoring
  Serial.begin(115200);

  // Start the software serial at 19200 baud rate for communication
  softSerial.begin(19200);

  // Print a startup message
  Serial.println("Serial Monitor started at 115200. SoftwareSerial started at 19200.");
}

void loop() {
  // Check if data is available to read from the hardware serial
  if (Serial.available()) {
    // Read a character from the hardware serial
    char receivedChar = Serial.read();

    // Echo the character back to the hardware serial monitor
    Serial.print("Sent: ");
    Serial.println(receivedChar);

    // Send the character over software serial at 19200 baud rate
    softSerial.write(receivedChar);
  }
}