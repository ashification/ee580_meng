##############################################
# 		     Python Decision logic Graphs     #
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
speed['average'].view()
distance.view()
intent.view()

# Definte rules under which to consider
rule1 = ctrl.Rule(speed['poor'] | distance['poor'], intent['low'])
# rule2 = ctrl.Rule(speed['poor'] | distance['average'], intent['low'])
# rule3 = ctrl.Rule(speed['poor'] | distance['good'], intent['low'])

rule4 = ctrl.Rule(distance['average'] & speed['average'], intent['medium'])
# rule5 = ctrl.Rule(distance['average'] & speed['good'], intent['medium'])

# rule6 = ctrl.Rule(distance['good'] & speed['average'], intent['high'])
rule7 = ctrl.Rule(distance['good'] & speed['good'], intent['high'])

# Print out rule graph
rule1.view()

# commit rules to the control system function
# intention_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
intention_ctrl = ctrl.ControlSystem([rule1, rule4, rule7])
intention = ctrl.ControlSystemSimulation(intention_ctrl)


'''
Sample data to manually plug in
speed =  61 office  740  boxrm  702  bedrm  434
speed =  60 office  744  boxrm  704  bedrm  440
speed =  41 office  757  boxrm  715  bedrm  454
'''
# Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
# Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
intention.input['speed'] = 60
intention.input['distance'] = 800

# Crunch the numbers
intention.compute()

print(intention.output['intent'])
intent.view(sim=intention)

