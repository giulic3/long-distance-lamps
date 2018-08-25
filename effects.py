from enum import Enum
import time
from neopixel import *

# Enumeration class for led colors
class LedColor(Enum):
     WHITE      = 0
     YELLOW     = 1
     RED        = 2
     PURPLE     = 3
     BLUE       = 4
     CYAN       = 5
     GREEN      = 6
# Maps enum colors to RGB colors as defined in the Neopixel library
ledColorsDictionary = {
    '0' : Color(255, 255, 255),
    '1' : Color(129, 255, 0),
    '2' : Color(0, 255, 0),
    '3' : Color(0, 194, 255),
    '4' : Color(0, 0, 255),
    '5' : Color(255, 0, 255),
    '6' : Color(255, 0, 0)
}

# Define functions which animate LEDs in various ways.


def colorWipe(strip, color, wait_ms=20):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, wait_ms=20, iterations=10):
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

def theaterChaseRainbow(strip, wait_ms=20):
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
    colorWipe(strip, ledColorsDictionary[str(i)])
    """
    if i == LedColor.WHITE.value:
        colorWipe(strip, Color(255,255,255))    # White
    elif i == LedColor.YELLOW.value:
        colorWipe(strip, Color(129, 255, 0))    # Yellow/Orange
    elif i == LedColor.RED.value:
        colorWipe(strip, Color(0, 255, 0))      # Red
    elif i == LedColor.PURPLE.value:
        colorWipe(strip, Color(0, 194, 255))    # Purple
    elif i == LedColor.BLUE.value:
        colorWipe(strip, Color(0, 0, 255))      # Blue
    elif i == LedColor.CYAN.value:
        colorWipe(strip, Color(255, 0, 255))    # Cyan
    else:
        colorWipe(strip, Color(255, 0, 0))      # Green
    """
