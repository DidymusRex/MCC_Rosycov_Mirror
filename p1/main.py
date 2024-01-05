"""
Project: Rosycov Mirror
File:    p1.py
Target:  Raspberry Pi Pico W
Description:
Puzzle one in the Rosycov Mirror series. Presented with four tuners,
three of which have rotary encoders, the players must figure out how to
adjust the values such that blue + yellow - red = target value (wht).

Each tuner has a target value constant. Turning the rotary encoder
increases or decreases the value. The puzzle is solved when the white
tuner shows its target value.
"""
from config import *
from machine import Pin, PWM
import math
from math import fabs, floor
import network
from rotary_irq_rp2 import RotaryIRQ
from stepper import Stepper
from time import sleep, sleep_ms, time
import tm1637
from tuner import Tuner
import ubinascii
from umqtt.simple import MQTTClient

# create a list of tuner init values
tuner_values=list()
tuner_values = [{'min_val': 1000,'max_val': 2000,'tgt_val': 1325,'ini_val': 1500,'display_clk_pinNo': 2,'display_dio_pinNo': 3,'rotary_clk_pinNo': 10,'rotary_dt_pinNo': 11,'button_pinNo': 12,'color': 'blu'},
                {'min_val': 0,'max_val': 2000,'tgt_val': 1762,'ini_val': 1000,'display_clk_pinNo': 4,'display_dio_pinNo': 5,'rotary_clk_pinNo': 28,'rotary_dt_pinNo': 27,'button_pinNo': 26,'color': 'ylw'},
                {'min_val': 3000,'max_val': 5000,'tgt_val': 2056,'ini_val': 1000,'display_clk_pinNo': 6,'display_dio_pinNo': 7,'rotary_clk_pinNo': 21,'rotary_dt_pinNo': 20,'button_pinNo': 19,'color': 'red'},
                {'min_val': 0,'max_val': 0,'tgt_val': 1031,'ini_val': 0,'display_clk_pinNo': 8,'display_dio_pinNo': 9,'rotary_clk_pinNo': -1,'rotary_dt_pinNo': -1,'button_pinNo': -1,'color': 'wht'}]

# create a dictionary of tuners
tuners=dict()
for t in tuner_values:
    tuners[t['color']] = Tuner(t['min_val'],t['max_val'],t['tgt_val'],t['ini_val'],t['display_clk_pinNo'],t['display_dio_pinNo'],t['rotary_clk_pinNo'],t['rotary_dt_pinNo'],t['button_pinNo'],t['color'])
    
# ----------------------------------------------------------

# perform a soft reset
def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()

# Function to check pin states and execute button_press if state is 0 (pressed)
def check_switch_states(delay_ms=50):

    for k,t in tuners.items():
        if not t.has_button():
            break
        
        # Debouncing logic
        current_time = utime.ticks_ms()

        if utime.ticks_diff(current_time, t.last_button_change) > delay_ms:
            new_state = t.get_button()

            if new_state != t.button_state:
                if new_state == 0:
                    button_press(t)
                
                t.set_button_state(new_state)
                print(f"Tuner {t.color} button state: {t.button_state}")
            
            t.set_last_button_change(current_time)

# messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    if 'reset' in msg:
        reset()

    print((topic, msg))

# publish a message on a topic to the mqtt broker
def mqtt_publish(topic, message):
    mqttClient.publish(topic, message)

# send a message when a button is pressed
def button_press(tuner):
    topic = 'mcc/p1/event/button'
    message = tuner.get_color() + ',' + str(tuner.value())
    mqtt_publish(topic, message)

# notify the console the puzzle is solved
def solved():
    global tuners
    
    stepper = Stepper(Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(22, Pin.OUT))

    blink_interval = 0.5
    last_blink = time()

    # alert the console
    mqtt_publish('mcc/p1/event', 'solved')

    # set the antenna turning and lights blinking
    while True:
        if (time() - last_blink) >= blink_interval:
            for k,t in tuners.items():
                t.randomize_display()

            last_blink = time()

        stepper.step(1, 10, .3)

# ----------------------------------------------------------
def main():
    global tuners
    
    # Where the work gets done until solved
    # white is blu + ylw - red
    while tuners['wht'].value() != tuners['wht'].target():
        
        w = tuners['blu'].value() + tuners['ylw'].value() - tuners['red'].value()

        for k,t in tuners.items():
            if t.get_color() == 'wht':
                t.update_display(w)
            else:
                t.update_display()

        # Non-blocking wait for message
        mqttClient.check_msg()

    solved()

# ----------------------------------------------------------
if __name__ == '__main__':
    
    # connect to WiFi
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(SSID, SSID_PW)
    
    while not sta_if.isconnected(): pass

    # connect to MQTT
    print(f"Begin connection with MQTT Broker :: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PW, keepalive=60)
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()
    mqttClient.subscribe(SUBSCRIBE_TOPIC)
    print(f"Connected to MQTT  Broker :: {MQTT_BROKER}, and waiting for callback function to be called!")

    # This protects against a memory error and resets the Pico
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            reset()

# ----------------------------------------------------------
# ----------------------------------------------------------
