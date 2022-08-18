##############################################
# 		     Python Decision logic	          #
# ------------------------------------------  #
# This purpose of this script is to determine #
# The probability a person is likely to try   #
# and enter a door way                        #
# ------------------------------------------  #
# Links for code sources where adaptions are  #
# made are inline with sections used          #
##############################################


import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from datetime import *
import time
import paho.mqtt.client as paho
from paho import mqtt
import json

# Declare subtopics to match rooms
door_office = "act1"
door_boxrm = "act2"
door_bedrm = "act3"
threshold = 5.0


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
    print("Message Event ", msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # Return JSON string to JSON object and extract variables
    json_tag_data = msg.payload
    deserial_json_tag_data = Tag_data(**json.loads(json_tag_data))
    tag_speed = deserial_json_tag_data.tag_speed
    # Invert the distance measurment to comply with fuzzy logic
    distance_office = 800 - deserial_json_tag_data.distance_office
    distance_boxrm = 800 - deserial_json_tag_data.distance_boxrm
    distance_bedrm = 800 - deserial_json_tag_data.distance_bedrm
    print("office ", distance_office, " boxrm ", distance_boxrm, " bedrm ", distance_bedrm)

    office_prob = fuzzylogic_funct(tag_speed, distance_office, door_office)
    boxrm_prob = fuzzylogic_funct(tag_speed, distance_boxrm, door_boxrm)
    bedrm_prob = fuzzylogic_funct(tag_speed, distance_bedrm, door_bedrm)

    actuator_function(office_prob, boxrm_prob, bedrm_prob)


# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="Fuzzy Logic algorithm", userdata=None, protocol=paho.MQTTv5)

# LWT Message set up before connection est
lwt = "Decision Logic Offline"  # Last will message
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

# a single publish, this can also be done in loops, etc.
client.publish("device_topic/device", payload="Simulator Online", qos=1)

##############################################
## Fuzzy logic decision code
# Code adapted from https://pythonhosted.org/scikit-fuzzy/auto_examples/plot_intention_problem_newapi.html
##############################################

# New Antecedent (inputs) and Consequent (outputs)
# objects hold universe variables and membership functions

speed = ctrl.Antecedent(np.arange(0, 70, 1), 'speed')  # range from 0 to 70 in 1 unit increments
distance = ctrl.Antecedent(np.arange(0, 800, 10), 'distance')  # range from 0 to 800 in 10 unit increments
intent = ctrl.Consequent(np.arange(0, 10, 1), 'intent')  # range from 0 to 10 in 1 unit increments

# Auto-membership function population is possible with .automf(3, 5, or 7)
speed.automf(3)
distance.automf(3)

# Custom membership functions can be built interactively with a familiar,
# Pythonic API
intent['low'] = fuzz.trimf(intent.universe, [0, 0, 5])  # triangle pts abc
intent['medium'] = fuzz.trimf(intent.universe, [2, 5, 8])  # triangle pts abc
intent['high'] = fuzz.trimf(intent.universe, [5, 10, 10])  # triangle pts abc

# Print out graphs of above functions
# speed['average'].view()
# distance.view()
# intent.view()

# Definte rules under which to consider
rule1 = ctrl.Rule(speed['poor'] | distance['poor'], intent['low'])
# rule2 = ctrl.Rule(speed['poor'] | distance['average'], intent['low'])
# rule3 = ctrl.Rule(speed['poor'] | distance['good'], intent['low'])

rule4 = ctrl.Rule(distance['average'] & speed['average'], intent['medium'])
# rule5 = ctrl.Rule(distance['average'] & speed['good'], intent['medium'])

# rule6 = ctrl.Rule(distance['good'] & speed['average'], intent['high'])
rule7 = ctrl.Rule(distance['good'] & speed['good'], intent['high'])

# Print out rule graph
# rule1.view()

# commit rules to the control system function
# intention_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
intention_ctrl = ctrl.ControlSystem([rule1, rule4, rule7])
intention = ctrl.ControlSystemSimulation(intention_ctrl)


def fuzzylogic_funct(tag_speed, distance, door):
    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
    intention.input['speed'] = tag_speed
    intention.input['distance'] = distance
    intention.compute()
    probability_intention = intention.output['intent']
    print(" Door - ", door, " intention - ", probability_intention)
    # intent.view(sim=intention)
    return probability_intention


def actuator_function(office_prob, boxrm_prob, bedrm_prob):
    if (office_prob >= threshold) & (office_prob > boxrm_prob) & (office_prob > bedrm_prob):
        client.publish("actuator_topic/act1", payload="1", qos=1)
        time.sleep(1)
        client.publish("actuator_topic/act1", payload="0", qos=1)
    if (boxrm_prob >= threshold) & (boxrm_prob > office_prob) & (boxrm_prob > bedrm_prob):
        client.publish("actuator_topic/act2", payload="1", qos=1)
        time.sleep(1)
        client.publish("actuator_topic/act2", payload="0", qos=1)
    if (bedrm_prob >= threshold) & (bedrm_prob > office_prob) & (bedrm_prob > boxrm_prob):
        client.publish("actuator_topic/act3", payload="1", qos=1)
        time.sleep(1)
        client.publish("actuator_topic/act3", payload="0", qos=1)


'''
Sample data to manually plug in
speed =  61 office  740  boxrm  702  bedrm  434
speed =  60 office  744  boxrm  704  bedrm  440
speed =  41 office  757  boxrm  715  bedrm  454

# Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
# Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
intention.input['speed'] = 65
intention.input['distance'] = 20

# Crunch the numbers
intention.compute()

print(intention.output['intent'])
intent.view(sim=intention)
'''

# loop_forever for simplicity, here you need to stop the loop manually
# you can also use loop_start and loop_stop
client.loop_forever()
