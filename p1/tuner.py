"""
Project: Rosycov Mirror
File: tuner.py
Target: Raspberry Pi Pico W
Description: Micropyton class for puzzle one of the MCC Rosycov Mirror project
"""
from machine import Pin
from math import fabs, floor
from random import randrange
from rotary_irq_rp2 import RotaryIRQ
import tm1637

class Tuner:

    def __init__(self,
                 min_val,
                 max_val,
                 tgt_val,
                 ini_val,
                 display_clk_pinNo,
                 display_dio_pinNo,
                 rotary_clk_pinNo,
                 rotary_dt_pinNo,
                 button_pinNo,
                 color):

        self.min_val = min_val
        self.max_val = max_val
        self.tgt_val = tgt_val
        self.cur_val = ini_val
        self.button_pinNo = button_pinNo
        self.color = color
        self.button_state = 1
        self.last_button_change = 0

        # set up the 4 digit LED display
        self.display = tm1637.TM1637(clk=Pin(display_clk_pinNo),
                                     dio=Pin(display_dio_pinNo))

        # set up the rotary encoder
        # if either pin number is < 0 there is no encoder
        if rotary_clk_pinNo < 0 or rotary_dt_pinNo < 0:
            self.rotary = None
        else:
            self.rotary = RotaryIRQ(rotary_clk_pinNo,
                                    rotary_dt_pinNo,
                                    min_val,
                                    max_val,
                                    reverse=True,
                                    range_mode=RotaryIRQ.RANGE_WRAP)

        # set up the rotary encoder button
        # if the pin number is < 0 there is no button
        if button_pinNo < 0:
            self.button = None
        else:
            self.button = Pin(button_pinNo, Pin.IN, Pin.PULL_UP)

    # provide control information
    def has_rotary(self):
        if self.rotary is None:
            return False
        else:
            return True

    def has_button(self):
        if self.button is None:
            return False
        else:
            return True

    def has_controls(self):
        if self.has_rotary() and self.has_button():
            return True
        else:
            return False

    # provide internal value information
    def get_color(self):
        return self.color

    def value(self):
        return self.cur_val
    
    def target(self):
        return self.tgt_val
    
    def min(self):
        return min_val
    
    def max(self):
        return max_val

    # update the LED display
    # if there is no encoder for this tuner then expect a value to be passed
    def update_display(self, value=0):
        if self.has_rotary():
            self.cur_val = self.rotary.value()
        else:
            self.cur_val = value

        # the display gets brighter as the value approaches the target value
        # brightness can be 0-7
        b = fabs(self.tgt_val - self.cur_val)
        if b == 0:
            bright=7
        elif b > 69:
            bright = 0
        else:
            bright = 7 - floor(b % 70 / 10)

        self.display.number(self.cur_val)
        self.display.brightness(int(bright))

    # clear the LED display
    def clear_display(self):
        self.display.show('    ')

    # fill the display
    def fill_display(self):
        self.display.show('8888')

    # set a random pattern on the display
    def randomize_display(self):
        self.display.write([randrange(128), randrange(128), randrange(128), randrange(128)])
        
    # return the current button value.
    # if there is no button return 1
    def get_button(self):
        if self.has_button():
            return self.button.value()
        else:
            return 1

    # return the saved button state
    def set_button_state(self, state):
        self.button_state = state

    # set the last button change time for debouncing
    def set_last_button_change(t):
        last_button_change = t
