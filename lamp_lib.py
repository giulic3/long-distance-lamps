from Adafruit_IO import Client, Feed, RequestError
import RPi.GPIO as GPIO
import time
import datetime
import threading
from neopixel import *
from effects import *
from subprocess import check_output
import signal
import traceback

def atomicConnection(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args,**kwargs)            
            #self.logger.debug("normal execution")
        except Exception:
            self.logger.debug("AN ERROR OCCURRED!!!!")
            traceback.self.print_exc()
            self.rollback()
    return wrapper

class Lamp:

    logger = ""

    # Set to your Adafruit IO key.
    # Remember, your key is a secret,
    # so make sure not to publish it when you publish this code!
    ADAFRUIT_IO_KEY = ''

    # Set to your Adafruit IO username.
    # (go to https://accounts.adafruit.com to find your username)
    ADAFRUIT_IO_USERNAME = ''

    # LED strip configuration:
    LED_COUNT      = 12      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10     # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 5       # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 150       # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    # Use GRB instead of RGB!
    LED_STRIP = ws.SK6812_STRIP_RGBW


    LED_COLORS     = 7       # Number of possible led colors
    BUTTON_COLOR_PIN = 27    # GPIO connected to the touch button used to change leds color
    BUTTON_POWER_PIN = 17    # GPIO connected to the switch button used turn off the leds
    BUTTON_SEND_PIN = 22     # GPIO connected to the touch button used to 'answer' to the sister lamp

    currentColor = -1
    # UTC Timezone in ISO-8601 format "YYYY-MM-DDTHH:MM:SSZ"
    colorUpdateTimestamp = ''

    powerButtonPressTimestamp = ''

    strip = None
    hostname = None

    aio = None
    colorButtonFeed = None
    # Wait 'timeoutSend' seconds after choosing the color before sending to aio
    timeoutSend = 5
    # 'True' if the user is in the middle of changing the leds color
    changingColor = False
    # 'True' to indicate that a thread must exit
    exit = False

    lastSavedState = None

    bootstrap = True

    BOUNCE_TIME = 200

    pulseThread = None
    stopPulse = True

    def __init__ (self, aio_username, aio_key, logger, debug=False):

        self.logger = logger

        # Setup buttons GPIO
        self.logger.debug("Lamp: setting up gpio")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_POWER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BUTTON_COLOR_PIN, GPIO.IN)
        GPIO.setup(self.BUTTON_SEND_PIN, GPIO.IN)
        GPIO.add_event_detect(self.BUTTON_COLOR_PIN, GPIO.FALLING, callback=self.buttonLedCallback, bouncetime=self.BOUNCE_TIME)
        GPIO.add_event_detect(self.BUTTON_POWER_PIN, GPIO.FALLING, callback=self.buttonPowerCallback, bouncetime=self.BOUNCE_TIME)
        GPIO.add_event_detect(self.BUTTON_SEND_PIN, GPIO.FALLING, callback=self.buttonSendCallback, bouncetime=self.BOUNCE_TIME)
        #TODO : gpio per il pulsante di spegnimento del raspberry

        # Initialize Adafruit IO
        # Create an instance of the REST client
        self.logger.debug("Lamp: initiating adafruit connection")
        self.ADAFRUIT_IO_USERNAME =  aio_username
        self.ADAFRUIT_IO_KEY = aio_key
        self.aio = Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)

        # Initialize feeds
    	# Read from existing feeds
        self.colorButtonFeed = self.aio.feeds('long-distance-lamps.colorbutton')

        # Set to true when the send button is pressed
        #sendAnimation = 0

        signal.signal(signal.SIGALRM, self.sendColorTimeoutHandler)

        self.colorUpdateTimestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        self.colorUpdateTimestamp += 'Z'

        # Retrieve Pi hostname to distinguish lamps
        self.hostname =  check_output(["hostname"]).decode().strip("\ \n \t")
        self.logger.debug("Lamp: hostname = %s", self.hostname)
        # Create NeoPixel object with appropriate configuration
        if self.hostname == "flash":
            self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL, self.LED_STRIP)
        elif self.hostname == "priscilla":
            self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        else:
            self.logger.debug("Invalid hostname!")
            exit(1)

        # Intialize the NeoPixel library (must be called once before other functions)
        self.strip.begin()
        self.strip.setBrightness(self.LED_BRIGHTNESS)
        # Leds are turned off at the beginning

        self.clear()

        threading.Thread(target=self.syncColors).start()
        self.pulseThread = threading.Thread(target=self.newColorReceived)

        self.logger.debug('Lamp: Ready\n \
            d         b\n \
           d           b\n \
          d             b\n \
         d               b\n \
        d     BradiPi     b\n \
         """:::.....:::"""\n \
                fff\n \
              ."   ".\n \
             ^       ^."--.\n \
             b       d     ,\n \
              zzzzzzz       ..oOo\n \
        ')
    
    def newColorReceived(self):
        self.logger.debug("pulsing...")
        # 10 minutes
        timeout = 600
        while (not self.stopPulse) and timeout >= 0:
            pulse(self.strip, int(self.currentColor), self.LED_BRIGHTNESS)
            timeout -= 1
        self.stopPulse = True
        self.logger.debug("stop pulsing")

    def rollback(self):
        self.logger.debug("Rolling back to last known state....")
        if self.lastSavedState is not None:
            showColor(self.strip, int(self.lastSavedState.value))
            self.colorUpdateTimestamp = self.lastSavedState.updated_at
        self.stopPulse = True
        self.changingColor = False

    @atomicConnection
    def sendColorTimeoutHandler(self,signum, frame):
        self.logger.debug("Lamp: Timeout reached. Sending Color....")
        self.aio.send(self.colorButtonFeed.key, self.currentColor) 
        time.sleep(2) 
        self.colorUpdateTimestamp = self.aio.receive(self.colorButtonFeed.key).updated_at
        self.logger.debug("Lamp: Color sent. Timestamp: %s" , self.colorUpdateTimestamp)
        self.changingColor = False

    def buttonLedCallback(self, channel):
        self.logger.debug("Lamp: Led button Pressed")
        if self.stopPulse == False:
            #if it was pulsing wait to stop pulsing
            self.stopPulse = True
            self.pulseThread.join()

        self.changingColor = True
        # Colors range from 0 to COLORS-1
        self.currentColor = (self.currentColor+1) % self.LED_COLORS
        self.logger.debug("current color %s", self.currentColor)
        showColor(self.strip, self.currentColor)
        # Send signal timer
        signal.alarm(self.timeoutSend)

    @atomicConnection
    def buttonPowerCallback(self, channel):
        self.logger.debug("Lamp: Power button Pressed")
        colorWipe(self.strip, Color(0, 0, 0))
        self.currentColor = -1
        colorButtonData = self.aio.receive(self.colorButtonFeed.key)
        self.powerButtonPressTimestamp = colorButtonData.updated_at

    def buttonSendCallback(self, channel):
        self.logger.debug("Lamp: Send button Pressed")
        #self.strip.setBrightness(50)
        # TODO send animation to adafruit io
        #sendAnimation = 1

    @atomicConnection
    def doSyncColor(self):
        self.logger.debug("syncing color")
        colorButtonData = self.aio.receive(self.colorButtonFeed.key)
        self.lastSavedState = colorButtonData
        #self.logger.debug("%s",colorButtonData.updated_at)
        # If the online value is more recent than local
        if colorButtonData.updated_at > self.colorUpdateTimestamp and not self.bootstrap:
            self.logger.debug("updating colors")
            self.logger.debug("%s",colorButtonData)
            self.currentColor = int(colorButtonData.value)
            self.colorUpdateTimestamp = colorButtonData.updated_at
            showColor(self.strip, self.currentColor)
            self.logger.debug("Lamp: color updated. Timestamp: %s" , self.colorUpdateTimestamp)
            #received new color, start to pulse 
            if self.pulseThread.is_alive():
                #wait for termination of any running thread
                self.stopPulse = True
                self.pulseThread.join()
            self.stopPulse = False
            self.pulseThread = threading.Thread(target=self.newColorReceived)
            self.pulseThread.start()
            # Update global timestamp
            #self.aio.send(self.colorButtonFeed.key, self.currentColor)
        if self.bootstrap:
            #just started the lamp, set to the last color 
            self.logger.debug("updating colors")
            self.logger.debug("%s", colorButtonData)
            self.bootstrap = False
            self.currentColor = int(colorButtonData.value)
            self.colorUpdateTimestamp = colorButtonData.updated_at
            showColor(self.strip, self.currentColor)
            self.logger.debug("Lamp: color updated. Timestamp: %s" , self.colorUpdateTimestamp)
            #received new color, start to pulse 
            # Update global timestamp
            #self.aio.send(self.colorButtonFeed.key, self.currentColor)

        #self.colorUpdateTimestamp = self.aio.receive(self.colorButtonFeed.key).updated_at
        #self.logger.debug("curent update time %s", self.colorUpdateTimestamp )

    def syncColors(self):
        """ Function used to synchronize the color of the two lamps, after one has been modified """
        while not self.exit:
            if (not self.changingColor):
                self.doSyncColor()
            # 10 seconds timer
            time.sleep(10)

    def clear (self):
        self.stopPulse = True
        colorWipe(self.strip, Color(0, 0, 0))
