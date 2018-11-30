from Adafruit_IO import Client, Feed, RequestError
import argparse
import json
import sys

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = ''

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = ''
# Initialize Adafruit IO
# Create an instance of the REST client
print("Lamp: initiating adafruit connection")

# Main program logic follows:
# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
parser.add_argument('config_file')
parser.add_argument('color')
args = parser.parse_args()

print ('Press Ctrl-C to quit.')
if not args.clear:
    print('Use "-c" argument to clear LEDs on exit')

if args.config_file:
    with open(args.config_file, 'r') as f:
        print("reading config file")
        config_data = json.load(f)
else:
    print("no configuration file given, please provide one")

if not args.color:
    exit(1)

ADAFRUIT_IO_USERNAME = config_data["connection"]["aio_username"] 
ADAFRUIT_IO_KEY = config_data["connection"]["aio_key"]
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
colorButtonFeed = aio.feeds('long-distance-lamps.colorbutton')
aio.send(colorButtonFeed.key, int(args.color))