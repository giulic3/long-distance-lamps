#!/usr/bin/env python3
# Long distance lamps
print("loading components...")
import time
from neopixel import *
import argparse
import RPi.GPIO as GPIO
from lamp_lib import Lamp
from effects import *
import json
import logging 

if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create a file handler
    handler = logging.FileHandler('/home/pi/long-distance-lamps/long-distance-lamp.log')
    handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    try:
        # Main program logic follows:
        # Process arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
        parser.add_argument('config_file')
        args = parser.parse_args()

        logger.debug ('Press Ctrl-C to quit.')
        if not args.clear:
            logger.debug('Use "-c" argument to clear LEDs on exit')

        if args.config_file:
            with open(args.config_file, 'r') as f:
                logger.debug("reading config file")
                config_data = json.load(f)
        else:
            logger.debug("no configuration file given, please provide one")

        logger.debug("creating the lamp")

        lamp = Lamp(config_data['connection']['aio_username'],
                config_data['connection']['aio_key'], logger)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        if args.clear:
            lamp.clear()
            logger.debug("closing, please wait...")
            lamp.exit = True
