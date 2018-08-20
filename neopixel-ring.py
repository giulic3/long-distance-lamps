#!/usr/bin/env python3
# Long distance lamps
import time
from neopixel import *
import argparse
import RPi.GPIO as GPIO

HIGH = 0 # 
LOW = 1 # Button pressed

# LED strip configuration:
LED_COUNT      = 12      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 5     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
# uSE GRB instead of RGB!

LED_COLORS     = 7      # Number of possible led colors
BUTTON_COLOR_PIN = 27   # GPIO connected to the touch button used to change leds color
BUTTON_POWER_PIN = 17	# GPIO connected to the switch button used turn off the leds
BUTTON_SEND_PIN = 22 	# GPIO connected to the touch button used to 'answer' to the sister lamp

# Setup buttons GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_POWER_PIN, GPIO.IN)
GPIO.setup(BUTTON_COLOR_PIN, GPIO.IN)
GPIO.setup(BUTTON_SEND_PIN, GPIO.IN)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def showColor(strip, i):
    if i == 0:
        colorWipe(strip, Color(255,255,255))  # White
    elif i == 1:
        colorWipe(strip, Color(129, 255, 0))  # Yellow/Orange
    elif i == 2:
        colorWipe(strip, Color(0, 255, 0))   # Red
    elif i == 3:
        colorWipe(strip, Color(0, 194, 255))  # Purple
    elif i == 4:
        colorWipe(strip, Color(0, 0, 255))   # Blue
    elif i == 5:
        colorWipe(strip, Color(255, 0, 255))  # Cyan
    else:
        colorWipe(strip, Color(255, 0, 0))    # Green


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Init buttons states
    buttonLedOldState = HIGH
    buttonSendOldState = HIGH
    buttonPowerOldState = HIGH
    currentColor = 0

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    strip.setBrightness(5)
    strip.show()
    colorWipe(strip, Color(255,255,255))  # White

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            
            # Get current buttons state
            buttonLedNewState = GPIO.input(BUTTON_COLOR_PIN)
	    buttonSendNewState = GPIO.input(BUTTON_SEND_PIN)
            buttonPowerNewState = GPIO.input(BUTTON_POWER_PIN)
	   

            # Color button logic
            # Check if state changed from high to low (button press).
            if buttonLedNewState == LOW and buttonLedOldState == HIGH:
                # Short delay to debounce button
                time.sleep(0.05)
                # Check if button is still low after debounce.
                buttonLedNewState = GPIO.input(BUTTON_COLOR_PIN)
                if buttonLedNewState == LOW:
                    # Colors range from 0 to COLORS-1
                    currentColor = (currentColor+1) % LED_COLORS
                    showColor(strip, currentColor)

	    # Send button logic
	    if buttonSendNewState == LOW and buttonSendOldState == HIGH:
	        time.sleep(0.05)
		buttonSendNewState = GPIO.input(BUTTON_SEND_PIN)
		if buttonSendNewState == LOW:
		    # Tmp: increase brightness
		    strip.setBrightness(100)
	 	    strip.show()

            # Switch off button logic
            if buttonPowerNewState == LOW and buttonPowerOldState == HIGH:
                time.sleep(0.05)
                buttonPowerNewState = GPIO.input(BUTTON_POWER_PIN)
                if buttonPowerNewState == LOW:
                    # Turn off all the leds
                    colorWipe(strip, Color(0, 0, 0)) 


            # Set the last button state to the old state.
            buttonLedOldState = buttonLedNewState
	    buttonSendOldState = buttonSendNewState
            buttonPowerOldState = buttonPowerNewState

            #print ('Theater chase animations.')
            #theaterChase(strip, Color(127, 127, 127))  # White theater chase
            #theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            #theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            #print ('Rainbow animations.')
            #rainbow(strip)
            #rainbowCycle(strip)
            #theaterChaseRainbow(strip)
            
    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)

