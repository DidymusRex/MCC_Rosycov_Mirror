"""
Project: Rosycov Mirror
File: lab1.py
Target: Raspberry Pi Pico W
Description:
Puzzle one in the Rosycov Mirror series. Presented with four displays,
three of which have rotary encoders, the players must figure out how to
adjust the values such that blue + yellow - red = target value.

Each display has a target value constant. Turning the rotary encoder
increases or decreases the value. The puzzle is solved when the white
display shows the correct value.
"""

from config import *
import tm1637
from machine import Pin, PWM
import math
import network
from rotary_irq_rp2 import RotaryIRQ
from servo import Servo
from stepper import Stepper
from time import sleep, sleep_ms
from math import fabs, floor
import utime

"""
--------------------------------------------------------------------------------
Globals
--------------------------------------------------------------------------------
"""
#1325 (1000-2000)
targetBlu = 1325
valueBlu = 1500
displayBlu = tm1637.TM1637(clk=Pin(2), dio=Pin(3))
rotaryBlu = RotaryIRQ(pin_num_clk=10,
              pin_num_dt=11,
              min_val=1000,
              max_val=2000,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_WRAP)
switchBlu = 12

#1762 (0-2000)
targetYlw = 1762
valueYlw = 1000
displayYlw = tm1637.TM1637(clk=Pin(4), dio=Pin(5))
rotaryYlw = RotaryIRQ(pin_num_clk=28,
              pin_num_dt=27,
              min_val=0,
              max_val=2000,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_WRAP)
switchYlw = 26

#2056 (3000-5000)
targetRed = 2056
valueRed = 1000
displayRed = tm1637.TM1637(clk=Pin(6), dio=Pin(7))
rotaryRed = RotaryIRQ(pin_num_clk=21,
              pin_num_dt=20,
              min_val=900,
              max_val=3000,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_WRAP)
switchRed = 19

#(1031) computed
targetWht = 1031
valueWht = valueBlu + valueYlw - valueRed
displayWht = tm1637.TM1637(clk=Pin(8), dio=Pin(9))
# rotaryWht = None
# switchWht = None

servo1 = Servo(15)
stepper1 = Stepper(Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(22, Pin.OUT))
stepper2 = Stepper(Pin(14, Pin.OUT), Pin(13, Pin.OUT), Pin(1, Pin.OUT), Pin(0, Pin.OUT))

"""
--------------------------------------------------------------------------------
Functions
--------------------------------------------------------------------------------
"""
def demo(d):
    # all on
    d.show('8888', True)
    sleep(.5)

    # all off
    d.show('    ')
    sleep(.5)

def updateDisplay(display, rotary, target):
    global valueBlu, valueYlw, valueRed

    if rotary is None:
        v = int(valueBlu + valueYlw - valueRed)

    else:
        v = floor(rotary.value())

    if fabs(v - target) == 0:
        bright=7
    else:
        if fabs(target - v) > 69:
            bright = 0
        else:
            bright = 7 - floor(fabs(target - v)%70 / 10)

    if rotary is None:
        if v < (targetWht - 1000):
            display.brightness(2)  
            display.show("  Lo  ")
        else:
            if v > (targetWht + 1000):
                display.show(" Hi  ")
            else:
                display.number(v) # expects an int -- see floor above
                display.brightness(int(bright)) 

    else:
        display.number(v) # expects an int -- see floor above
        display.brightness(int(bright))

    return v

def connectWiFi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PW)
        while not sta_if.isconnected():
            print("Attempting to connect....")
            utime.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())

def notMain():
    servo1.write(0)
    rotaryBlu.set(value=valueBlu)
    rotaryYlw.set(value=valueYlw)
    rotaryRed.set(value=valueRed)

    while valueWht != targetWht:
        valueBlu = updateDisplay(displayBlu, rotaryBlu, targetBlu)
        valueYlw = updateDisplay(displayYlw, rotaryYlw, targetYlw)
        valueRed = updateDisplay(displayRed, rotaryRed, targetRed)
        valueWht = updateDisplay(displayWht, None, targetWht)

        sleep(.1)

    # Solved
    # Do somethng MQTT-ish....
    displayBlu.show('    ')
    displayYlw.show('    ')
    displayRed.show('    ')
    displayWht.show('    ')

    for i in range(10):
        displayWht.show('8888')
        sleep(.1)
        displayWht.show('    ')
        sleep(.1)

    servo1.write(90)

"""
--------------------------------------------------------------------------------
Main
--------------------------------------------------------------------------------
"""
def main():
    connectWiFi()

    for i in range(10):
        displayWht.show('8888')
        sleep(.1)
        displayWht.show('    ')
        sleep(.1)

        stepper1.step(1, 50,  .3)
        stepper2.step(-1, 20, .3)

    stepper1.step(1, 0,  .3)
    stepper2.step(-1, 0, .3)

"""
--------------------------------------------------------------------------------
Begin here ...
--------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    main()
