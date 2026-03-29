#include "MPU9250.h"
#include <Servo.h>

MPU9250 mpu;

#define Relay1 6
#define Relay2 7
#define Relay3 4
#define Relay4 5
#define Relay5 8
#define Relay6 9
#define LeakPin 12

bool arduino1 = true;
int sensorValue;
int LeakValue;

Servo ESC1;
Servo ESC2;

float readVoltage()
{
  float v = analogRead(A4) * (5.0 / 1023.0);
  return v;  // adjust divider ratio if needed
}

float readCurrent()
{
  float sensitivity = 0.066;  // 66mV/A for 30A version
  float zeroCurrent = 2.5;
  
  float v = analogRead(A2) * (5.0 / 1023.0);
  float current = (v - zeroCurrent) / sensitivity;

  return current;
}

float readPress()
{
  float V, P;
  const float OffSet = 0.483 ;

  V = analogRead(A0) * 5.00 / 1024;
  P = (V - OffSet) * 250;
  return P;
}
void setup() {

  Serial.begin(115200);
  delay(2000);
  pinMode(Relay1, OUTPUT);
  pinMode(Relay2, OUTPUT);
  pinMode(Relay3, OUTPUT);
  pinMode(Relay4, OUTPUT);
  pinMode(Relay5, OUTPUT);
  pinMode(Relay6, OUTPUT);
  pinMode(11, INPUT_PULLUP);
  pinMode(LeakPin, INPUT);

  ESC1.attach(2);
  ESC2.attach(3);

  ESC1.writeMicroseconds(1500);
  ESC2.writeMicroseconds(1500);

  arduino1 = digitalRead(11);
  delay(3000);
  if (arduino1) {
    Wire.begin();
    if (!mpu.setup(0x68))
    { // change to your own address
      while (1) {
        Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
        delay(5000);
      }
    }
  }
}


void setMotor(int motorIndex, int value) {
  // motorIndex: 0 → Relay1/2, 1 → Relay3/4, 2 → Relay5/6
  // value: -1 = backward, 0 = stop, 1 = forward
  int rA, rB;
  switch (motorIndex) {
    case 0: rA = Relay1; rB = Relay2; break;
    case 1: rA = Relay3; rB = Relay4; break;
    case 2: rA = Relay5; rB = Relay6; break;
    default: return;
  }

  if (value == 1) {
    digitalWrite(rA, HIGH);
    digitalWrite(rB, LOW);
  } else if (value == -1) {
    digitalWrite(rA, LOW);
    digitalWrite(rB, HIGH);
  } else {
    digitalWrite(rA, LOW);
    digitalWrite(rB, LOW);
  }
}

void loop()
{

  int LeakValue = digitalRead(LeakPin);
  Serial.print("Leak:");
  Serial.print(LeakValue);
  if (arduino1) {
    print_roll_pitch_yaw();
    if (mpu.update())
    {
      static uint32_t prev_ms = millis();
      if (millis() > prev_ms + 25) {
        prev_ms = millis();
      }
    }
  }
  else {
    Serial.print("  Voltage:");
    Serial.println(readVoltage());
  }

  if (!Serial.available()) return;

  String input = Serial.readStringUntil('\n');
  input.trim();

  int sep = input.indexOf("#");
  if (sep == -1) return;
  //
  String leftPart  = input.substring(0, sep);
  String rightPart = input.substring(sep + 1);
  //
  leftPart.trim();
  rightPart.trim();
  //
  String data = arduino1 ? leftPart : rightPart;
  //
  int fork, RL, unused, ESCUP, ESCFB;
  int parsed = sscanf(data.c_str(), "%d %d %d %d %d", &fork, &RL, &unused, &ESCUP, &ESCFB);
  //
  if (parsed == 5) {
    // Motor1 = fork
    setMotor(0, fork);
    // Motor2 = RL
    setMotor(1, RL);
    // Motor3 = unused (keep stopped)
    setMotor(2, 0);

    ESC1.writeMicroseconds(constrain(ESCFB, 1000, 2000));
    ESC2.writeMicroseconds(constrain(ESCUP, 1000, 2000));
  }
}

void print_roll_pitch_yaw() 
{

  float pressure = readPress();

  float voltage = readVoltage();

  float current = readCurrent();
  
  Serial.print("  Yaw,Pitch,Roll,Temp,Pressure");
  Serial.print(mpu.getYaw(), 2);
  Serial.print(",");
  Serial.print(mpu.getPitch(), 2);
  Serial.print(",");
  Serial.print(mpu.getRoll(), 2);
  Serial.print(",");
  Serial.print(mpu.getTemperature(), 2);
  Serial.print(",");
  Serial.println(pressure);
  Serial.print(",");
  Serial.println(current);
}
