"""
Project: Rosycov Mirror
File:    main.py (for RM device p1)
Target:  Raspberry Pi Pico W with RP2040
Description:
Puzzle one in the Rosycov Mirror series. Presented with four tuners,
three of which have rotary encoders, the players must figure out how to
adjust the values such that blue + yellow - red = target value (wht).

Each tuner has a target value. Turning the rotary encoder increases or
decreases the value. The puzzle is solved when the white tuner shows its
target value.
"""
from config import *
import errno
import gc
from machine import Pin, PWM
import math
from math import fabs, floor
import network
import random
from rotary_irq_rp2 import RotaryIRQ
from stepper import Stepper
from time import sleep, sleep_ms, time
import tm1637
from tuner import Tuner
import ubinascii
from umqtt.simple import MQTTClient
import utime

# ----------------------------------------------------------

# perform a soft reset
def reset():
    debug()
    print('Resetting...')
    sleep(5)
    machine.reset()

# gah!
def debug():
    global tuners

    print('Debug:')
    print(f'memory used {gc.mem_alloc()}')
    print(f'memory free {gc.mem_free()}')
    
    #for k in tuners.keys():
    #elp()    tuners[k].debug()

# cheat for the game master
def cheat():
    a = tuners['blu'].target()
    b = tuners['ylw'].target()
    c = tuners['red'].target()

    message =  f'solution is {a} {b} {c}'
    print(message)
    mqtt_publish(MQTT_ROOT + '/cheat', message)

# Function to check pin states and execute button_press if state is 0 (pressed)
def check_button_states(delay_ms=50):
    global tuners

    for k,t in tuners.items():
        if not t.has_button():
            break
        
        # Debouncing logic
        current_time = utime.ticks_ms()

        if utime.ticks_diff(current_time, t.get_last_button_change()) > delay_ms:
            new_state = t.get_button()

            if new_state != t.get_button_state():
                if new_state == 0:
                    button_press(t)
                
                t.set_button_state(new_state)
                print(f'Tuner {t.color} button state: {t.button_state}')
                t.set_last_button_change(current_time)

# messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print('received')
    print(f'topic ....: {topic.decode()}')
    print(f'message ..: {msg.decode()}')

    if 'cheat' in msg.decode():
        cheat()

    if 'debug' in msg.decode():
        debug()

    if 'reset' in msg.decode():
        reset()

# publish a message on a topic to the mqtt broker
def mqtt_publish(topic, message):
    mqttClient.publish(topic, message)

    print('sent')
    print(f'topic ....: {topic}')
    print(f'message ..: {message}')

# send a message when a button is pressed
def button_press(tuner):
    global tuners

    print(tuner.get_color() + 'pressed')
    
    topic = MQTT_ROOT + '/event/button'
    message = tuner.get_color() + ',' + str(tuner.value())
    mqtt_publish(topic, message)
    
    a = tuners['blu'].value()
    b = tuners['ylw'].value()
    c = tuners['red'].value()

    print(f'game status {a} {b} {c}')
                
# notify the console the puzzle is solved
def solved():
    global tuners

    debug()
    
    stepper = Stepper(Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(22, Pin.OUT))

    interval = 0.5
    last_interval = time()

    mqtt_publish(MQTT_ROOT + '/event', 'solved')

    # set the antenna turning and lights blinking
    while True:
        if (time() - last_interval) >= interval:
            # Non-blocking wait for MQTT message
            mqttClient.check_msg()

            for k,t in tuners.items():
                t.randomize_display()

            last_interval = time()

        stepper.step(1, 10, .3)

# ----------------------------------------------------------
def main():
    global tuners
    
    # tell the console we are up and running
    mqtt_publish(MQTT_ROOT + '/status', 'online')
    
    # give the game master needed information
    cheat()

    # the solution to the puzzle
    while (tuners['blu'].value() != tuners['blu'].target()
           or tuners['ylw'].value() != tuners['ylw'].target()
           or tuners['red'].value() != tuners['red'].target()):

        # update the LED displays. White is calculated, the rest are input
        for k,t in tuners.items():
            if t.has_controls():
                t.update_display()
                if t.value() != t.target():
                    tuners['wht'].update_display(t.target() - t.value())

        # check buttons
        check_button_states()

        # Non-blocking wait for MQTT message
        mqttClient.check_msg()

    # solution achieved!
    solved()

# ----------------------------------------------------------
if __name__ == '__main__':

    # create a list of tuner initialization values
    print('Solution 231 625 144')
    
    tuner_values=list()
    tuner_values = [{'min_val': 180,'max_val': 280,'tgt_val': 231,'display_clk_pinNo': 2,'display_dio_pinNo': 3,'rotary_clk_pinNo': 10,'rotary_dt_pinNo': 11,'button_pinNo': 12,'color': 'blu'},
                    {'min_val': 575,'max_val': 676,'tgt_val': 625,'display_clk_pinNo': 4,'display_dio_pinNo': 5,'rotary_clk_pinNo': 28,'rotary_dt_pinNo': 27,'button_pinNo': 26,'color': 'ylw'},
                    {'min_val': 96,'max_val': 201,'tgt_val': 144,'display_clk_pinNo': 6,'display_dio_pinNo': 7,'rotary_clk_pinNo': 21,'rotary_dt_pinNo': 20,'button_pinNo': 19,'color': 'red'},
                    {'min_val': 0,'max_val': 0,'tgt_val': 0,'display_clk_pinNo': 8,'display_dio_pinNo': 9,'rotary_clk_pinNo': -1,'rotary_dt_pinNo': -1,'button_pinNo': -1,'color': 'wht'}]

    # create a dictionary of tuners
    tuners=dict()
    for t in tuner_values:
        tuners[t['color']] = Tuner(t['min_val'],t['max_val'],t['tgt_val'],t['display_clk_pinNo'],t['display_dio_pinNo'],t['rotary_clk_pinNo'],t['rotary_dt_pinNo'],t['button_pinNo'],t['color'])

    # connect to WiFi
    print(f'connecting to wifi {SSID}')
    sta_if = network.WLAN(network.STA_IF)
    #ap_if = network.WLAN(network.AP_IF)

    #ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(SSID, SSID_PW)
    
    while not sta_if.isconnected():
        sleep(.1)

    # connect to MQTT
    print(f'Begin connection with MQTT Broker :: {MQTT_BROKER}')
    mqttClient = MQTTClient(MQTT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PW, keepalive=60)
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()
    mqttClient.subscribe(MQTT_SUB)
    
    print(f'Connected to MQTT Broker :: {MQTT_BROKER}')
    print(f'Subscribed to {MQTT_SUB}')
    print(f'waiting for callback function to be called!')

    # This protects against a memory error and resets the Pico
    while True:
        try:
            main()
        except OSError as e:
            print('Error: ' + str(e))
            print(errno.errorcode[e])
            reset()

# ----------------------------------------------------------
# ----------------------------------------------------------
