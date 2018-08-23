#!/usr/bin/env python3
# Long distance lamps
import time
from neopixel import *
import argparse
import RPi.GPIO as GPIO
from lamp_lib import Lamp
from effects import *

if __name__ == "__main__":

    try:
        # TODO add lamp number as main argument
        # Main program logic follows:
        # Process arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
        args = parser.parse_args()

        print ('Press Ctrl-C to quit.')
        if not args.clear:
            print('Use "-c" argument to clear LEDs on exit')

        lamp = Lamp()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(lamp.strip, Color(0,0,0), 10)
