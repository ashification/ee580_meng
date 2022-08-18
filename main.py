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

# Import the required libraries
from datetime import *
from tkinter import *
import time
import paho.mqtt.client as paho
from paho import mqtt
import sqlite3
from time import sleep
from typing import List
import json

# Define co-ordinates for canvas item
varwidth = 800
varheight = 500
x_coord = 580
y_coord = 630
n = 5

class Tag_data(object):
    def __init__(self, tag_speed: int, distance_office: int, distance_boxrm: int, distance_bedrm: int):
        self.tag_speed = tag_speed
        self.distance_office = distance_office
        self.distance_boxrm = distance_boxrm
        self.distance_bedrm = distance_bedrm


##############################################
## MQTT Broker code
## Code adapted from https://console.hivemq.cloud/clients/python-paho?uuid=3a7064825d8d4ce68f4d17cdf59b41e1
##############################################

# when a connection acknowledgement event occurs print function message.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# On publish event print value for TS
def on_publish(client, userdata, mid, properties=None):
    # print("mid: " + str(mid))
    return


# On subscribe event print values for confirmation
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# On message event print values for confirmation
def on_message(client, userdata, msg):
    #print("Message Event ", msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    '''
       if (msg.topic == "tag_topic/tag1"):
        # Return JSON string to JSON object and extract variables
        json_tag_data = msg.payload
        deserial_json_tag_data = Tag_data(**json.loads(json_tag_data))
        tag_speed = deserial_json_tag_data.tag_speed
        distance_office = deserial_json_tag_data.distance_office
        distance_boxrm = deserial_json_tag_data.distance_boxrm
        distance_bedrm = deserial_json_tag_data.distance_bedrm
        print(" Message Event contains ", tag_speed, " ", distance_office, " ", distance_boxrm, " ", distance_bedrm)
        if (tag_speed != 0):
            client.publish("actuator_topic/act1", payload="1", qos=1)
        if (tag_speed == 0):
            client.publish("actuator_topic/act1", payload="0", qos=1)
    '''


# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="Python Simulator", userdata=None, protocol=paho.MQTTv5)

# LWT Message set up before connection est
lwt = "Simulator Offline"  # Last will message
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

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("tag_topic/tag1", qos=1)
client.subscribe("actuator_topic/#", qos=1)
client.subscribe("device_topic/device", qos=1)

# a single publish, this can also be done in loops, etc.
client.publish("device_topic/device", payload="Simulator Online", qos=1)

##############################################
## Define Python SQL DB
##############################################

'''
# Create the DB
db_connection = sqlite3.connect('user_location_tracking.db')
# Create Table
db_cursor.execute("""CREATE TABLE tag_location (
        tag_id text,
        x_coord int,
        y_coord int,
        time_stamp int
        )""")
    db_connection.commit()
    db_connection.close()
'''


def submit_todb(x1_coord, y1_coord, time1):
    # Connect to the DB
    db_connection = sqlite3.connect('user_location_tracking.db')
    # Create a Cursor
    db_cursor = db_connection.cursor()
    db_cursor.execute("INSERT INTO tag_location VALUES (:tagid, :x1_coord, :y1_coord, :date_time)",
                      {
                          'tagid': "tag_1",
                          'x1_coord': x1_coord,
                          'y1_coord': y1_coord,
                          'date_time': time1
                      })

    db_connection.commit()
    db_connection.close()


def query_fromdb():
    # Connect to the DB
    db_connection = sqlite3.connect('user_location_tracking.db')
    # Create a Cursor
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT oid FROM tag_location ORDER BY oid DESC ")
    print(db_cursor.fetchone())
    current_oid = db_cursor.fetchone()[0]
    print(current_oid)
    nth_oid = current_oid - n
    print(nth_oid)

    db_cursor.execute("""
                    SELECT *,oid 
                    FROM tag_location 
                    WHERE oid == ? 
                    ORDER BY oid DESC 
                    """,
                      (nth_oid,))
    print(db_cursor.fetchall())

    db_cursor.execute("""
                        SELECT x_coord
                        FROM tag_location 
                        WHERE oid == ? 
                        ORDER BY oid DESC 
                        """,
                      (nth_oid,))
    xn_coord = int(db_cursor.fetchone()[0])

    db_cursor.execute("""
                        SELECT y_coord
                        FROM tag_location 
                        WHERE oid == ? 
                        ORDER BY oid DESC 
                        """,
                      (nth_oid,))
    yn_coord = int(db_cursor.fetchone()[0])

    db_cursor.execute("""
                        SELECT time_stamp
                        FROM tag_location 
                        WHERE oid == ? 
                        ORDER BY oid DESC 
                        """,
                      (nth_oid,))
    timen = db_cursor.fetchone()[0]
    print("x5 = ", xn_coord, " y5 = ", yn_coord, " timen = ", timen)

    db_connection.commit()
    db_connection.close()
    return xn_coord, yn_coord, timen


def speed_calc(x1_coord, y1_coord, time1, xn_coord, yn_coord, timen):
    # calc average speed = distance/time
    distance_covered = ((x1_coord - xn_coord) ** 2 + (y1_coord - yn_coord) ** 2) ** 0.5
    time_taken = time1 - timen
    #print("time1 ", time1, " timen ", timen, " timediff ", time_taken, "distance covered ", distance_covered)
    tag_speed = int(distance_covered / time_taken)
    #print("speed = ", tag_speed)
    return tag_speed


def distance_calc(x1_coord, y1_coord, xn_coord, yn_coord):
    ## To Do distance of current X Y to door 1 2 and 3
    ## Door frame center co-ords
    # office = (420 450)
    x_office = 420
    y_office = 450
    # Box rm = (420 590)
    x_boxrm = 420
    y_boxrm = 590
    # Bed rm = (770 400)
    x_bedrm = 770
    y_bedrm = 400

    # distance between 2 pts = sqrt[(x1-x2)^2 + (y1-y2)^2]
    distance_office = int(((x1_coord - x_office) ** 2 + (y1_coord - y_office) ** 2) ** 0.5)
    distance_boxrm = int(((x1_coord - x_boxrm) ** 2 + (y1_coord - y_boxrm) ** 2) ** 0.5)
    distance_bedrm = int(((x1_coord - x_bedrm) ** 2 + (y1_coord - y_office) ** 2) ** 0.5)

    print("office ", distance_office, " boxrm ", distance_boxrm, " bedrm ", distance_bedrm)
    return distance_office, distance_boxrm, distance_bedrm


##############################################
## Define Python Simulator app
##############################################

# Canvas Window Values
simulator_window = Tk()
simulator_window.title('RTLS Simulator')
simulator_window.geometry("1340x810")

# Definte Image
bg = PhotoImage(file="Images/Floorplan_v3.png")
tag = PhotoImage(file="Images/tag.png")

# create canvas
canvas = Canvas(simulator_window, width=varwidth, height=varheight)
canvas.pack(fill="both", expand=True)

# Set canvas Background Image
canvas.create_image(0, 0, image=bg, anchor="nw")

# Define Tag
# coordinates_tag = 200, 100, 250, 150  # x1, y1, x2, y2
tag_object = canvas.create_oval(x_coord, y_coord, x_coord + 30, y_coord + 30, fill="#FFFF00")


def left(event):
    x_coord = -10
    y_coord = 0
    canvas.move(tag_object, x_coord, y_coord)
    #tag_location_update()


def right(event):
    x_coord = 10
    y_coord = 0
    canvas.move(tag_object, x_coord, y_coord)
    #tag_location_update()


def up(event):
    x_coord = 0
    y_coord = -10
    canvas.move(tag_object, x_coord, y_coord)
    #tag_location_update()


def down(event):
    x_coord = 0
    y_coord = 10
    canvas.move(tag_object, x_coord, y_coord)
    #tag_location_update()


def tag_location_update():
    # Get and Print the coordinates of the tag
    print("Tag Loc Update Funct")
    #print("Coordinates of the tag are:", canvas.coords(tag_object)[0:2])
    x1_coord = int(canvas.coords(tag_object)[0])
    y1_coord = int(canvas.coords(tag_object)[1])
    time1 = datetime.now()
    #print("x1", x1_coord, " y1 ", y1_coord, " time1 ", time1)
    currenttime = datetime.now()
    time1 = (currenttime - datetime(1970, 1, 1)).total_seconds()
    submit_todb(x1_coord, y1_coord, time1)
    xn_coord, yn_coord, timen = query_fromdb()

    tag_speed = speed_calc(x1_coord, y1_coord, time1, xn_coord, yn_coord, timen)
    distance_office, distance_boxrm, distance_bedrm = distance_calc(x1_coord, y1_coord, xn_coord, yn_coord)

    # Take data and convert to JSON object and serialise into string
    tag1 = Tag_data(tag_speed, distance_office, distance_boxrm, distance_bedrm)
    json_tag_data = json.dumps(tag1.__dict__)
    print(json_tag_data)
    #print(Tag_data(**json.loads(json_tag_data)))
    client.publish("tag_topic/tag1", payload=json_tag_data, qos=1)

    # Return JSON string to JSON object and extract variables
    deserial_json_tag_data = Tag_data(**json.loads(json_tag_data))
    tag_speed = deserial_json_tag_data.tag_speed
    distance_office = deserial_json_tag_data.distance_office
    distance_boxrm = deserial_json_tag_data.distance_boxrm
    distance_bedrm = deserial_json_tag_data.distance_bedrm
    #print( tag_speed, " ", distance_office, " ", distance_boxrm, " ", distance_bedrm)

    client.publish("tag_topic/tag1/distance_office", payload=distance_office, qos=1)
    client.publish("tag_topic/tag1/distance_boxrm", payload=distance_boxrm, qos=1)
    client.publish("tag_topic/tag1/distance_bedrm", payload=distance_bedrm, qos=1)
    client.publish("tag_topic/tag1/speed", payload=tag_speed, qos=1)

    # client.publish("tag_topic/tag1", payload=str(canvas.coords(tag_object)[0:2]), qos=1)
    # client.publish("actuator_topic/act1", payload="0", qos=1)
    # client.publish("actuator_topic/act2", payload="0", qos=1)
    # client.publish("actuator_topic/act3", payload="0", qos=1)


simulator_window.bind("<Left>", left)
simulator_window.bind("<Right>", right)
simulator_window.bind("<Up>", up)
simulator_window.bind("<Down>", down)

while 1:
    tag_location_update()
    time.sleep(1)

client.loop_start()
simulator_window.mainloop()
client.loop_stop()
