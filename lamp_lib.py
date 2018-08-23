#from Adafruit_IO import Client, Feed, RequestError
import RPi.GPIO as GPIO
import time
from neopixel import *
from effects import *

class Lamp:

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
    LED_STRIP = ws.SK6812_STRIP_RGBW


    LED_COLORS     = 7       # Number of possible led colors
    BUTTON_COLOR_PIN = 27    # GPIO connected to the touch button used to change leds color
    BUTTON_POWER_PIN = 17    # GPIO connected to the switch button used turn off the leds
    BUTTON_SEND_PIN = 22     # GPIO connected to the touch button used to 'answer' to the sister lamp

    currentColor = -1

    strip = None


    def __init__ (self):
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
        """
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
        """

        # Set to true when the send button is pressed
        #sendAnimation = 0

        # Create NeoPixel object with appropriate configuration
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL, self.LED_STRIP)
        # Intialize the neopixel library (must be called once before other functions)
        self.strip.begin()
        self.strip.setBrightness(5)
        # Leds are turned off at the beginning
        # colorWipe(strip, Color(255,255,255))  # White

    def buttonLedCallback(self, channel):
        print("Led Pressed")
        # Colors range from 0 to COLORS-1
        self.currentColor = (self.currentColor+1) % self.LED_COLORS
        print(self.currentColor)
        showColor(self.strip, self.currentColor)
        # aio.send(colorButtonFeed.key, currentColor)

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
    def syncColors(feed):
        return

    """ Function used to 'answer' to a sister lamp that has changed the color,
    it sends an animation as a signal of communication received """
    def sendAnimation(feed):
        return

        #theaterChase(strip, Color(127, 127, 127))  # White theater chase
        #theaterChase(strip, Color(127,   0,   0))  # Red theater chase
        #theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
        #rainbow(strip)
        #rainbowCycle(strip)
        #theaterChaseRainbow(strip)
        """
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
        """
