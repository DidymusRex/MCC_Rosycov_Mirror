from machine import Pin, PWM
from stepper import Stepper

# ----------------------------------------------------------
stepper = Stepper(Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(22, Pin.OUT))

for i in range(100):
    stepper.step(1, 100, .3)


