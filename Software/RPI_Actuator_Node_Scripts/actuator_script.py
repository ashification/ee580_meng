import RPi.GPIO as GPIO
import time
import paho.mqtt.client as paho
from paho import mqtt
import re

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6, GPIO.OUT)  # Red
GPIO.setup(13, GPIO.OUT)  # Orange
GPIO.setup(19, GPIO.OUT)  # Yellow
GPIO.setup(26, GPIO.OUT)  # Blue


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    GPIO.output(6, GPIO.HIGH)  # Red


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    raw_payload = str(msg.payload)
    print(raw_payload)
    if ("actuator_topic/" in msg.topic):
        trigger = int(re.sub('[^0-9]', '', raw_payload))  # remove non alphanuemeric characters
        print(trigger)
    if (msg.topic == "device_topic/device"):
        message = raw_payload  # [1:-1]
        print(message)
    if (msg.topic == "actuator_topic/act1"):
        if (trigger == 1):
            print("Turn ON Orange LED")
            # set GPIO pin to HIGH
            GPIO.output(13, GPIO.HIGH)  # Orange
        if (trigger == 0):
            print("Turn Off Orange LED")
            # set GPIO pin to Low
            GPIO.output(13, GPIO.LOW)  # Orange
    if (msg.topic == "actuator_topic/act2"):
        if (trigger == 1):
            print("Turn ON Yellow LED")
            # set GPIO pins to HIGH
            GPIO.output(19, GPIO.HIGH)  # Yellow
        if (trigger == 0):
            print("Turn Off Yellow LED")
            # set GPIO pins to Low
            GPIO.output(19, GPIO.LOW)  # Yellow
    if (msg.topic == "actuator_topic/act3"):
        if (trigger == 1):
            print("Turn ON Blue LED")
            # set GPIO pins to HIGH
            GPIO.output(26, GPIO.HIGH)  # Yellow
        if (trigger == 0):
            print("Turn Off Blue LED")
            # set GPIO pins to Low
            GPIO.output(26, GPIO.LOW)  # Yellow
    if (msg.topic == "device_topic/device"):
        if ("Offline" in message):
		  print("Turn OFF Red LED")
		  # set GPIO pin to Low
		  GPIO.output(6, GPIO.LOW)  # Red
		  GPIO.output(13, GPIO.LOW)  # Orange
		  GPIO.output(19, GPIO.LOW)  # Yellow
		  GPIO.output(26, GPIO.LOW)  # Blue
        if (message == "Simulator Online"):
            print("Turn OFF Red LED")
            # set GPIO pin to HIGH
            GPIO.output(6, GPIO.HIGH)  # Red

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="Actuator", userdata=None, protocol=paho.MQTTv5)

# LWT Message set up before connection est
lwt = "Actuator Offline"  # Last will message
lwt_post_topic = "device_topic/device"
print("Setting Last will message=", lwt, "topic is", lwt_post_topic)
client.will_set(lwt_post_topic, lwt, 1, retain=False)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("SN20216371", "EE580_alee")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("3a7064825d8d4ce68f4d17cdf59b41e1.s1.eu.hivemq.cloud", 8883)

# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

# subscribe to all actuator and device topics by using the wildcard "#"
client.subscribe("actuator_topic/#", qos=1)
client.subscribe("device_topic/#", qos=1)

# a single publish, this can also be done in loops, etc.
client.publish("device_topic/device", payload="Actuator Online", qos=1)

# loop_forever for simplicity, here you need to stop the loop manually
# you can also use loop_start and loop_stop
client.loop_forever()
