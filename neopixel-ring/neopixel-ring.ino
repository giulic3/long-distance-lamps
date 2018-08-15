#include <Adafruit_NeoPixel.h>
#define BUTTON_PIN   6    // Digital IO pin connected to the button.  This will be
                          // driven with a pull-up resistor so the switch should
                          // pull the pin to ground momentarily.  On a high -> low
                          // transition the button press logic will execute.

#define PIXEL_PIN    3    // Digital IO pin connected to the NeoPixels.

#define NUM_PIXELS 12

#define ANIM_TYPES 4
Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_PIXELS, PIXEL_PIN, NEO_GRB + NEO_KHZ800);


bool oldState = HIGH;
int showType = 0;


void setup() {
  // start the ring and blank it out
  ring.begin();
  ring.show(); // Initialize all pixels to 'off'

}

void loop() {
  // Get current button state.
  bool newState = digitalRead(BUTTON_PIN);

  // Check if state changed from high to low (button press).
  if (newState == LOW && oldState == HIGH) {
    // Short delay to debounce button.
    delay(20);
    // Check if button is still low after debounce.
    newState = digitalRead(BUTTON_PIN);
    if (newState == LOW) {
      
      //showType++;
      //if (showType > 9)
      //  showType = 0;
      // Animation types range from 0 to ANIM_TYPES-1
      showType = (showType+1) % ANIM_TYPES;
      startShow(showType);
    }
  }

  // Set the last button state to the old state.
  oldState = newState;

}


void startShow(int i) {
  switch(i){
    case 0: colorWipe(ring.Color(0, 0, 0), 50);    // Black/off
            break;
    case 1: colorWipe(ring.Color(255, 0, 0), 50);  // Red
            break;
    case 2: colorWipe(ring.Color(0, 255, 0), 50);  // Green
            break;
    case 3: colorWipe(ring.Color(0, 0, 255), 50);  // Blue
            break;
  }
}

// Fill the dots one after the other with a color
void colorWipe(uint32_t c, uint8_t wait) {
  for(uint16_t i=0; i<ring.numPixels(); i++) {
    ring.setPixelColor(i, c);
    ring.show();
    delay(wait);
  }
}
