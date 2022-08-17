import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6,GPIO.OUT)  # Red
GPIO.setup(13,GPIO.OUT) # Orange
GPIO.setup(19,GPIO.OUT) # Yellow
GPIO.setup(26,GPIO.OUT) # Blue

# While loop
while True:
	# set GPIO pins to HIGH
	GPIO.output(6,GPIO.HIGH)
	GPIO.output(13,GPIO.HIGH)
	GPIO.output(19,GPIO.HIGH)
	GPIO.output(26,GPIO.HIGH)
	# show message to Terminal
	print "LED is ON"
	# pause for one second
	time.sleep(1)


        # set GPIO pins to Low
        GPIO.output(6,GPIO.LOW)
	GPIO.output(13,GPIO.LOW)
	GPIO.output(19,GPIO.LOW)
	GPIO.output(26,GPIO.LOW)
        # show message to Terminal
        print "LED is OFF"
        # pause for one second
        time.sleep(1)

