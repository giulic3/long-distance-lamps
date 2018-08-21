#!/usr/bin/env python3
# Long distance lamps
import time
from neopixel import *
import argparse
import RPi.GPIO as GPIO

# Import Adafruit Blinka
import board
import digitalio

# import Adafruit IO REST client.
from Adafruit_IO import Client, Feed, RequestError

import pixels

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = ''

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = ''

HIGH = 0
LOW = 1        # Button pressed

# LED strip configuration:
LED_COUNT      = 12      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10     # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 5       # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
# Use GRB instead of RGB!

LED_COLORS     = 7       # Number of possible led colors
BUTTON_COLOR_PIN = 27    # GPIO connected to the touch button used to change leds color
BUTTON_POWER_PIN = 17    # GPIO connected to the switch button used turn off the leds
BUTTON_SEND_PIN = 22     # GPIO connected to the touch button used to 'answer' to the sister lamp

# Setup buttons GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_POWER_PIN, GPIO.IN)
GPIO.setup(BUTTON_COLOR_PIN, GPIO.IN)
GPIO.setup(BUTTON_SEND_PIN, GPIO.IN)

""" Function used to synchronize the color of the two lamps, after one has been modified """
def syncColors(feed):

""" Function used to 'answer' to a sister lamp that has changed the color,
it sends an animation as a signal of communication received """
def sendAnimation(feed):

# TODO add lamp number as main argument
# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Initialize Adafruit IO
    # Create an instance of the REST client
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Initialize feeds
	# Read from existing feeds
    colorButtonFeed1 = aio.feeds('long-distance-lamps.colorbutton1')
    colorButtonFeed2 = aio.feeds('long-distance-lamps.colorbutton2')
    sendButtonFeed1 = aio.feeds('long-distance-lamps.sendbutton1')
    sendButtonFeed2 = aio.feeds('long-distance-lamps.sendbutton2')
    ledsFeed1 = aio.feeds('long-distance-lamps.leds1')
    ledsFeed2 = aio.feeds('long-distance-lamps.leds2')
    syncColorsFeed = aio.feeds('long-distance-lamps.synccolors')
    sendAnimationFeed = aio.feeds('long-distance-lamps.sendanimation')

    # Init buttons states
    buttonLedOldState = HIGH
    buttonSendOldState = HIGH
    buttonPowerOldState = HIGH
    currentColor = -1
    # Set to true when the send button is pressed
    sendAnimation = 0

    # Create NeoPixel object with appropriate configuration
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the neopixel library (must be called once before other functions)
    strip.begin()
    strip.setBrightness(5)
    strip.show()
    # Leds are turned off at the beginning
    # colorWipe(strip, Color(255,255,255))  # White

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
                    # Colors range from 0 to LED_COLORS-1
                    currentColor = (currentColor+1) % LED_COLORS
                    showColor(strip, currentColor)
                    aio.send(colorButtonFeed.key, currentColor)
                    # Avoid timeout from Adafruit IO
                    time.sleep(1)

            # Send button logic
            if buttonSendNewState == LOW and buttonSendOldState == HIGH:
                time.sleep(0.05)
                buttonSendNewState = GPIO.input(BUTTON_SEND_PIN)
                if buttonSendNewState == LOW:
                    # TODO Tmp: increase brightness
                    strip.setBrightness(50)
                    strip.show()
                    # TODO send animation to adafruit io
                    sendAnimation = 1

            # Switch off button logic
            if buttonPowerNewState == LOW and buttonPowerOldState == HIGH:
                time.sleep(0.05)
                buttonPowerNewState = GPIO.input(BUTTON_POWER_PIN)
                if buttonPowerNewState == LOW:
                    # Turn off all the leds
                    colorWipe(strip, Color(0, 0, 0))
                    currentColor = -1


            # Set the last button state to the old state.
            buttonLedOldState = buttonLedNewState
            buttonSendOldState = buttonSendNewState
            buttonPowerOldState = buttonPowerNewState

            #theaterChase(strip, Color(127, 127, 127))  # White theater chase
            #theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            #theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            #rainbow(strip)
            #rainbowCycle(strip)
            #theaterChaseRainbow(strip)

            # Two-lamps communication logic TODO imo too many requests
            shouldSync = aio.receive(syncColorsFeed.key)
            if shouldSync.value == 1:
                color1 = aio.receive(colorButtonFeed1.key) # check if correct!
                color2 = aio.receive(colorButtonFeed2.key) #
                # Update with the most recent color
                if color1.updated_at <= color2.updated_at: # check
                    # update with the color of 2
                else:
                    # update with the color of 1

            # Check if the sister lamp wants to send an animation
            shouldReceiveAnimation = aio.receive(sendAnimationFeed.key)
            # Identify the receiving lamp
            if shouldReceiveAnimation.value == 1 and sendAnimation == 0:
                # animate pixels TODO
                # ...
                aio.send(sendAnimationFeed.key, 0)

            # Zero 'sendAnimation' variable for the sending lamp
            elif shouldReceiveAnimatin.value == 0 and sendAnimation == 1:
                sendAnimation = 0


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
