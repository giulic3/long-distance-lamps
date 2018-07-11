#include <Adafruit_NeoPixel.h>
#define PIN 5
#define NUM_LEDS 12
Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  // start the ring and blank it out
  ring.begin();
  ring.show();

}

void loop() {
  // set pixel to red, delay(1000)
  ring.setPixelColor(0, 255, 0, 0);
  ring.show();
  delay(1000);
  // set pixel to off, delay(1000)
  ring.setPixelColor(0, 0, 0, 0);
  ring.show();
  delay(1000);

}
