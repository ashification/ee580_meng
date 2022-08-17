 ##############################################
# 		     Python DRTLS simulator	          #
# ------------------------------------------  #
# This purpose of this script is to simulate  #
# The Decawave web manager, live tag tracking #
# and the broadcasting of tag co-ordinates    #
# ------------------------------------------  #
# Links for code sources where adaptions are  #
# made are inline with sections used          #
 ##############################################


# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#Import the required libraries
from tkinter import *
import time
import paho.mqtt.client as paho
from paho import mqtt



##############################################
## MQTT Broker code
## Code adapted from https://console.hivemq.cloud/clients/python-paho?uuid=3a7064825d8d4ce68f4d17cdf59b41e1
##############################################

# when a connection acknowledgement event occurs print function message.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# On publish event print value for TS
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# On subscribe event print values for confirmation
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# On message event print values for confirmation
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="Python Simulator", userdata=None, protocol=paho.MQTTv5)

# LWT Message set up before connection est
lwt="Simulator Offline" # Last will message
lwt_post_topic="device_topic/device"
print("Setting Last will message=",lwt,"topic is",lwt_post_topic )
client.will_set(lwt_post_topic, lwt,1,retain=False)

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

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("tag_topic/tag1", qos=1)
client.subscribe("actuator_topic/#", qos=1)
client.subscribe("device_topic/device", qos=1)

# a single publish, this can also be done in loops, etc.
client.publish("tag_topic/tag1", payload="Intial message", qos=1)

##############################################
## Define Python Simulator app
##############################################

# Canvas Window Values
simulator_window = Tk()
simulator_window.title('RTLS Simulator')
simulator_window.geometry("1340x810")

#Definte Image
bg = PhotoImage(file="Images/Floorplan_v3.png")
tag = PhotoImage(file="Images/tag.png")

#Define co-ordinates
varwidth=800
varheight=500
x_coord=580
y_coord=630

#create canvas
canvas = Canvas(simulator_window, width=varwidth, height=varheight)
canvas.pack(fill="both", expand=True)

#Set canvas Background Image
canvas.create_image(0,0, image=bg, anchor="nw")

# Define Tag
#coordinates_tag = 200, 100, 250, 150  # x1, y1, x2, y2
tag_object = canvas.create_oval(x_coord, y_coord, x_coord+30, y_coord+30, fill="#FFFF00")

def left(event):
    x_coord = -10
    y_coord = 0
    canvas.move(tag_object, x_coord, y_coord)
    # Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object)[0:2])
    client.publish("tag_topic/tag1", payload=str(canvas.coords(tag_object)[0:2]), qos=1)
    client.publish("actuator_topic/act1", payload="1", qos=1)
    client.publish("actuator_topic/act2", payload="0", qos=1)
    client.publish("actuator_topic/act3", payload="0", qos=1)


def right(event):
    x_coord = 10
    y_coord = 0
    canvas.move(tag_object, x_coord, y_coord)
    # Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object)[0:2])
    client.publish("tag_topic/tag1", payload=str(canvas.coords(tag_object)[0:2]), qos=1)
    client.publish("actuator_topic/act1", payload="0", qos=1)
    client.publish("actuator_topic/act2", payload="1", qos=1)
    client.publish("actuator_topic/act3", payload="0", qos=1)


def up(event):
    x_coord = 0
    y_coord = -10
    canvas.move(tag_object, x_coord, y_coord)
    # Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object)[0:2])
    client.publish("tag_topic/tag1", payload=str(canvas.coords(tag_object)[0:2]), qos=1)
    client.publish("actuator_topic/act1", payload="0", qos=1)
    client.publish("actuator_topic/act2", payload="0", qos=1)
    client.publish("actuator_topic/act3", payload="1", qos=1)


def down(event):
    x_coord = 0
    y_coord = 10
    canvas.move(tag_object, x_coord, y_coord)
    #Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object)[0:2])
    client.publish("tag_topic/tag1", payload=str(canvas.coords(tag_object)[0:2]), qos=1)
    client.publish("actuator_topic/act1", payload="0", qos=1)
    client.publish("actuator_topic/act2", payload="0", qos=1)
    client.publish("actuator_topic/act3", payload="0", qos=1)

simulator_window.bind("<Left>", left)
simulator_window.bind("<Right>", right)
simulator_window.bind("<Up>", up)
simulator_window.bind("<Down>", down)

## Anchor co-ords
#1_anchor = (60, 230)
#2_anchor = (60, 590)
#3_anchor = (1140, 420)

client.loop_start()
#Run Window
simulator_window.mainloop()
client.loop_stop()

