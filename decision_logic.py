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
from PIL import Image

# Code adapted from https://pythonhosted.org/scikit-fuzzy/auto_examples/plot_intention_problem_newapi.html

# New Antecedent/Consequent objects hold universe variables and membership
# functions
speed = ctrl.Antecedent(np.arange(0, 71, 1), 'speed')
distance = ctrl.Antecedent(np.arange(0, 800, 10), 'distance')
intent = ctrl.Consequent(np.arange(0, 11, 1), 'intent')

# Auto-membership function population is possible with .automf(3, 5, or 7)
speed.automf(3)
distance.automf(3)

# Custom membership functions can be built interactively with a familiar,
# Pythonic API
intent['low'] = fuzz.trimf(intent.universe, [0, 0, 5])
intent['medium'] = fuzz.trimf(intent.universe, [2, 5, 8])
intent['high'] = fuzz.trimf(intent.universe, [5, 10, 10])

speed['average'].view()
distance.view()
intent.view()

rule1 = ctrl.Rule(speed['poor'] | distance['poor'], intent['low'])
rule2 = ctrl.Rule(speed['poor'] | distance['average'], intent['low'])
rule3 = ctrl.Rule(speed['poor'] | distance['good'], intent['low'])

rule4 = ctrl.Rule(distance['average'] & speed['average'], intent['medium'])
rule5 = ctrl.Rule(distance['average'] & speed['good'], intent['medium'])

rule6 = ctrl.Rule(distance['good'] & speed['average'], intent['high'])
rule7 = ctrl.Rule(distance['good'] & speed['good'], intent['high'])

rule1.view()

intention_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
intention = ctrl.ControlSystemSimulation(intention_ctrl)

# Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
# Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
intention.input['speed'] = 65
intention.input['distance'] = 20

'''
Sample data to manually plug in
speed =  61 office  740  boxrm  702  bedrm  434
speed =  60 office  744  boxrm  704  bedrm  440
speed =  41 office  757  boxrm  715  bedrm  454

intention.input['speed'] = 65
intention.input['distance'] = 20
'''
# Crunch the numbers
intention.compute()

print(intention.output['intent'])
intent.view(sim=intention)
