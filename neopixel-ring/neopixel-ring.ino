#include <Adafruit_NeoPixel.h>
#define BUTTON_ANIM_PIN   6    // Digital IO pin connected to the button.  This will be
                          // driven with a pull-up resistor so the switch should
                          // pull the pin to ground momentarily.  On a high -> low
                          // transition the button press logic will execute.
                          
#define BUTTON_POWER_PIN 2 // Digital IO pin connected to the button that controls off/on leds state

#define PIXEL_PIN    3    // Digital IO pin connected to the NeoPixels.

#define NUM_PIXELS 12

#define ANIM_TYPES 7 // Number of animation types (controlled with the switch..case below)

Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_PIXELS, PIXEL_PIN, NEO_GRB + NEO_KHZ800);

// Init buttons states
bool buttonLedOldState = HIGH;
bool buttonPowerOldState = HIGH;
int showType = 0;


void setup() {
  // start the ring and blank it out
  ring.begin();
  // Used in setup, to modulate brightness use pixel sketch logic (range 0..255, from min to max)
  ring.setBrightness(30);
  ring.show(); // Initialize all pixels to 'off'

}

void loop() {
  // Get current button state.
  bool buttonLedNewState = digitalRead(BUTTON_ANIM_PIN);
  bool buttonPowerNewState = digitalRead(BUTTON_POWER_PIN);

  // ANIMATION BUTTON LOGIC
  // Check if state changed from high to low (button press).
  if (buttonLedNewState == LOW && buttonLedOldState == HIGH) {
    // Short delay to debounce button.
    delay(20);
    // Check if button is still low after debounce.
    buttonLedNewState = digitalRead(BUTTON_ANIM_PIN);
    if (buttonLedNewState == LOW) {
      // Animation types range from 0 to ANIM_TYPES-1
      showType = (showType+1) % ANIM_TYPES;
      startShow(showType);
    }
  }
  // SWITCH ON/OFF BUTTON LOGIC
  if (buttonPowerNewState == LOW && buttonPowerOldState == HIGH) {
    delay(20);
    buttonPowerNewState = digitalRead(BUTTON_POWER_PIN);
    if (buttonPowerNewState == LOW) {
      // Turn off all the leds
      colorWipe(ring.Color(0, 0, 0), 50); 
    }
  }

  // Set the last button state to the old state.
  buttonLedOldState = buttonLedNewState;
  buttonPowerOldState = buttonPowerNewState;

}


void startShow(int i) {
  switch(i){
    case 0: colorWipe(ring.Color(255,255,255), 50);  // White
            break;
    case 1: colorWipe(ring.Color(255, 129, 0), 50);  // Yellow/Orange
            break;
    case 2: colorWipe(ring.Color(255, 0, 0), 50);    // Red
            break;
    case 3: colorWipe(ring.Color(194, 0, 255), 50);  // Purple
            break;
    case 4: colorWipe(ring.Color(0, 0, 255), 50);    // Blue
            break;
    case 5: colorWipe(ring.Color(0, 255, 255), 50);  // Cyan
            break;
    case 6: colorWipe(ring.Color(0, 255, 0), 50);    // Green
            break;

  
  }
}

// Fill the dots one after the other with a color
void colorWipe(uint32_t c, uint8_t wait) {
  for (uint16_t i = 0; i < ring.numPixels(); i++) {
    ring.setPixelColor(i, c);
    ring.show();
    delay(wait);
  }
}
