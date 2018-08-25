from Adafruit_IO import Client, Feed, RequestError
import RPi.GPIO as GPIO
import time, datetime
import threading
from neopixel import *
from effects import *
from subprocess import check_output
import signal

class Lamp:

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
    LED_BRIGHTNESS = 5       # Set to 0 for darkest and 255 for brightest
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

    strip = None
    hostname = None     
    
    aio = None
    colorButtonFeed = None
    # Wait 'timeoutSend' seconds after choosing the color before sending to aio
    timeoutSend = 5
    changingColor = False

    def __init__ (self, aio_username, aio_key):

        # Setup buttons GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_POWER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BUTTON_COLOR_PIN, GPIO.IN)
        GPIO.setup(self.BUTTON_SEND_PIN, GPIO.IN)
        GPIO.add_event_detect(self.BUTTON_COLOR_PIN, GPIO.FALLING, callback=self.buttonLedCallback, bouncetime=200)
        GPIO.add_event_detect(self.BUTTON_POWER_PIN, GPIO.FALLING, callback=self.buttonPowerCallback, bouncetime=200)
        GPIO.add_event_detect(self.BUTTON_SEND_PIN, GPIO.FALLING, callback=self.buttonSendCallback, bouncetime=200)

        # Initialize Adafruit IO
        # Create an instance of the REST client
        self.ADAFRUIT_IO_USERNAME =  aio_username
        self.ADAFRUIT_IO_KEY = aio_key
        self.aio = Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)

        # Initialize feeds
    	# Read from existing feeds

        self.colorButtonFeed = self.aio.feeds('long-distance-lamps.colorbutton')
        """
        sendButtonFeed1 = aio.feeds('long-distance-lamps.sendbutton1')
        sendButtonFeed2 = aio.feeds('long-distance-lamps.sendbutton2')
        sendAnimationFeed = aio.feeds('long-distance-lamps.sendanimation')
        """

        # Set to true when the send button is pressed
        #sendAnimation = 0

        signal.signal(signal.SIGALRM, self.sendColorTimeoutHandler)

        self.colorUpdateTimestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        self.colorUpdateTimestamp += 'Z'

        # Retrieve Pi hostname to distinguish lamps
        self.hostname =  check_output(["hostname"]).decode().strip("\ \n \t")
        print(self.hostname)
        # Create NeoPixel object with appropriate configuration
        if self.hostname == "flash":
            self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL, self.LED_STRIP)
        elif self.hostname == "priscilla": 
            self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        else:
            print("Invalid hostname!")
            exit(1)

        # Intialize the neopixel library (must be called once before other functions)
        self.strip.begin()
        self.strip.setBrightness(5)
        # Leds are turned off at the beginning

    def sendColorTimeoutHandler(self,signum, frame):
        self.colorUpdateTimestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        self.colorUpdateTimestamp += 'Z'
        self.aio.send(self.colorButtonFeed.key, self.currentColor)
        print("Color sent")
        self.changingColor = False

    def buttonLedCallback(self, channel):
        print("Led Pressed")
        self.changingColor = True
        # Colors range from 0 to COLORS-1
        self.currentColor = (self.currentColor+1) % self.LED_COLORS
        print(self.currentColor)
        showColor(self.strip, self.currentColor)

        # Send signal timer
        signal.alarm(self.timeoutSend)
        """
        self.colorUpdateTimestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        self.colorUpdateTimestamp += 'Z'
        self.aio.send(self.colorButtonFeed.key, self.currentColor)
        """

    def buttonPowerCallback(self, channel):
        print("Power Pressed")
        colorWipe(self.strip, Color(0, 0, 0))
        self.currentColor = -1

    def buttonSendCallback(self, channel):
        print("Send Pressed")
        self.strip.setBrightness(50)
        self.strip.show()
        # TODO send animation to adafruit io
        #sendAnimation = 1


    """ Function used to synchronize the color of the two lamps, after one has been modified """
    def syncColors(self):
        if not self.changingColor:
            colorButtonData = self.aio.receive(self.colorButtonFeed.key)
            print(colorButtonData.updated_at)
            # If the online value is more recent than local
            if colorButtonData.updated_at >= self.colorUpdateTimestamp:
                self.currentColor = int(colorButtonData.value)
                showColor(self.strip, self.currentColor)
                # Update local timestamp
                self.colorUpdateTimestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
                self.colorUpdateTimestamp += 'Z'
                # Update global timestamp
                self.aio.send(self.colorButtonFeed.key, self.currentColor)
            
        # 10 seconds timer
        threading.Timer(10, self.syncColors).start()

    """ Function used to 'answer' to a sister lamp that has changed the color,
    it sends an animation as a signal of communication received """
    def sendAnimation(self):
        return

        #theaterChase(strip, Color(127, 127, 127))  # White theater chase
        #theaterChase(strip, Color(127,   0,   0))  # Red theater chase
        #theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
        #rainbow(strip)
        #rainbowCycle(strip)
        #theaterChaseRainbow(strip)
        """
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
        """
