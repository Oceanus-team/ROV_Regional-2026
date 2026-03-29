#include <SoftwareSerial.h>

// BLUETOOTH 
SoftwareSerial bluetooth(11, 12);

//  PINS 
#define RELAY_EXTEND 4
#define RELAY_RETRACT 5
#define SENSOR A0

// CONTROL 
float targetDepth = 1.9;
float tolerance = 0.5;

// ===== DATA =====
#define MAX_DATA 300

struct DataPoint {
  uint16_t time;
  uint16_t depth;
};
float V, depth;
const float OffSet = 0.483 ;


DataPoint dataLog[MAX_DATA];
int indexLog = 0;

//  TIMING 
unsigned long startTime;
unsigned long lastSample = 0;

// FLAGS 
bool profilingStarted = false;

void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600);

  pinMode(RELAY_EXTEND, OUTPUT);
  pinMode(RELAY_RETRACT, OUTPUT);

  digitalWrite(RELAY_EXTEND, LOW);
  digitalWrite(RELAY_RETRACT, LOW);

  startTime = millis();

  Serial.println("READY");
}

// ===== LOOP =====
void loop() {

  V = analogRead(SENSOR) * 5.00 / 1024; //Sensor output voltage
  depth = (V - OffSet) * 250;
  unsigned long now = millis();

  Serial.print("Depth: ");
  Serial.println(depth);

  // STORE DATA (EVERY 3s)
  if (indexLog < MAX_DATA) {

    if (now - lastSample >= 3000) {
      lastSample = now;

      dataLog[indexLog].depth = depth;
      dataLog[indexLog].time = (now - startTime) / 3000;

      indexLog++;

      Serial.print("Stored: ");
      Serial.println(depth);
    }
  }

  // DEPTH CONTROL

  if (90 < depth && depth < 130) {
    digitalWrite(RELAY_EXTEND, LOW);
    digitalWrite(RELAY_RETRACT, LOW);
    Serial.print("sotp");


  }

  else if ( depth > 130) {
    digitalWrite(RELAY_EXTEND, LOW);
    digitalWrite(RELAY_RETRACT, HIGH);
  }
  else if (depth < 90 ) {
    digitalWrite(RELAY_EXTEND, HIGH);
    digitalWrite(RELAY_RETRACT, LOW);
  }




  // SEND DATA WHEN 'S' IS SENT
  if (bluetooth.available()) {
    Serial.println("here");
    char cmd = bluetooth.read();

    if (cmd == 'S') {

      Serial.println("S RECEIVED → SENDING");

      bluetooth.println("DATA START");

      for (int i = 0; i < indexLog; i++) {
        bluetooth.print(dataLog[i].time);
        bluetooth.print(",");
        bluetooth.println(dataLog[i].depth);
        delay(3);
      }

      bluetooth.println("DATA END");

      Serial.println("DATA SENT");
    }
  }

  delay(10);
}
