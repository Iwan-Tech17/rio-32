// Example firmware: reads one text command per line over USB serial.
//   LED 1 | LED 0   -> turn LED on/off          (reply "OK")
//   PWM 0..255      -> PWM duty on PWM_PIN       (reply "OK")
//   ADC             -> read ANALOG_PIN           (reply the number)
//   PING            -> reply "PONG"
//
// Works on Arduino Uno/Nano/Mega and ESP32 (Arduino core). Adjust the pins below.

const long BAUD = 115200;
const int LED_PIN    = LED_BUILTIN;
const int PWM_PIN    = 9;    // Uno: 3,5,6,9,10,11 | ESP32: any output pin
const int ANALOG_PIN = A0;   // ESP32: use a GPIO like 34 instead

void setup() {
  Serial.begin(BAUD);
  pinMode(LED_PIN, OUTPUT);
  pinMode(PWM_PIN, OUTPUT);
}

void loop() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;

  if (line == "LED 1") {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("OK");
  } else if (line == "LED 0") {
    digitalWrite(LED_PIN, LOW);
    Serial.println("OK");
  } else if (line.startsWith("PWM ")) {
    int v = constrain(line.substring(4).toInt(), 0, 255);
    analogWrite(PWM_PIN, v);
    Serial.println("OK");
  } else if (line == "ADC") {
    Serial.println(analogRead(ANALOG_PIN));
  } else if (line == "PING") {
    Serial.println("PONG");
  } else {
    Serial.println("ERR unknown command");
  }
}
