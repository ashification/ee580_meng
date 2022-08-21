##############################################
# 		     Python Decision logic	          #
# ------------------------------------------  #
# This purpose of this script is to determine #
# The probability a person is likely to try   #
# and enter a door way referred to as their   #
# intent value
# ------------------------------------------  #
# Links for code sources where adaptions are  #
# made are inline with sections used          #
##############################################


#Import all library functions required
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
# Declare the threshold value for decision-making
# 5.0 selected as it is 83% of the range being output 1.6 - 6.0
threshold = 5.0

# Definte the tag object to be used when de-serialsing the JSON data
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


# On message event capture and parse the JSON string payload and pass to relevant fucntions
def on_message(client, userdata, msg):
    print("Message Event ", msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # Store JSON string payload as variable
    json_tag_data = msg.payload
    # Return JSON string to JSON object
    deserial_json_tag_data = Tag_data(**json.loads(json_tag_data))
    # extract speed and distance variables
    tag_speed = deserial_json_tag_data.tag_speed
    #Note it is required to invert the distance measurment to comply with fuzzy logic analysis bands. Maximum distance is 800 units
    distance_office = 800 - deserial_json_tag_data.distance_office
    distance_boxrm = 800 - deserial_json_tag_data.distance_boxrm
    distance_bedrm = 800 - deserial_json_tag_data.distance_bedrm
    print("office ", distance_office, " boxrm ", distance_boxrm, " bedrm ", distance_bedrm)

    #Pass parsed data to the fuzzylogic function for an intent value to be calculated
    office_prob = fuzzylogic_funct(tag_speed, distance_office, door_office)
    boxrm_prob = fuzzylogic_funct(tag_speed, distance_boxrm, door_boxrm)
    bedrm_prob = fuzzylogic_funct(tag_speed, distance_bedrm, door_bedrm)

    #Pass intent valued to the actuator function for decison making based on intent
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

# New Antecedent (inputs) and Consequent (outputs) objects to be decalred
# objects hold universe variables and membership functions

speed = ctrl.Antecedent(np.arange(0, 70, 1), 'speed')  # range from 0 to 70 in 1 unit increments
distance = ctrl.Antecedent(np.arange(0, 800, 10), 'distance')  # range from 0 to 800 in 10 unit increments
intent = ctrl.Consequent(np.arange(0, 10, 1), 'intent')  # range from 0 to 10 in 1 unit increments

# Auto-membership function population is possible with .automf(3, 5, or 7)
# the numerical value provided determines the number of category the antecedents are segmented into
# eg 3 produces 3 categories poor average high
#    5 produces 5 categories lower, low, average (always middle), high, higher
#    7 produces all the following: lowest, lower, low, average (always middle), high, higher, highest
speed.automf(3)
distance.automf(3)

# Custom membership functions can be built interactively with a familiar, Pythonic API
# Provide points of triangles and values that fall within those areas are treated as negative, inconclusive or affirmative
intent['low'] = fuzz.trimf(intent.universe, [0, 0, 5])  # triangle pts abc negative
intent['medium'] = fuzz.trimf(intent.universe, [2, 5, 8])  # triangle pts abc inconclusive
intent['high'] = fuzz.trimf(intent.universe, [5, 10, 10])  # triangle pts abc affirmative

# Print out graphs of the above functions
# speed.view()
# distance.view()
# intent.view()

# Define rules under which to consider
# Conditions to produce a negative result
rule1 = ctrl.Rule(speed['poor'] | distance['poor'], intent['low'])
# rule2 = ctrl.Rule(speed['poor'] | distance['average'], intent['low'])
# rule3 = ctrl.Rule(speed['poor'] | distance['good'], intent['low'])

# Conditions to produce an inconclusive result
rule4 = ctrl.Rule(distance['average'] & speed['average'], intent['medium'])
# rule5 = ctrl.Rule(distance['average'] & speed['good'], intent['medium'])

# Conditions to produce an affimative result
# rule6 = ctrl.Rule(distance['good'] & speed['average'], intent['high'])
rule7 = ctrl.Rule(distance['good'] & speed['good'], intent['high'])

# Print out rule graph
# rule1.view()

# commit rules to the control system function
# intention_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
intention_ctrl = ctrl.ControlSystem([rule1, rule4, rule7])
intention = ctrl.ControlSystemSimulation(intention_ctrl)


def fuzzylogic_funct(tag_speed, distance, door):
    # Function to calculate the intent value upon which decisions will be made
    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    intention.input['speed'] = tag_speed
    intention.input['distance'] = distance
    intention.compute()
    probability_intention = intention.output['intent']
    print(" Door - ", door, " intention - ", probability_intention)
    intent.view(sim=intention)
    return probability_intention


def actuator_function(office_prob, boxrm_prob, bedrm_prob):
    # Function to trigger actuation based off of data based decision
    # If intent value exceeds threshold and is higher than that of the other 2 rooms publish
    # to corresponding topic a 1 for actuation to occur and a second later publish 0 to trigger deactivation

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
