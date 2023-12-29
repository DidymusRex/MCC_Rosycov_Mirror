"""
stepper class for 28byj-48 stepper motor with a ULN2003 driver board
based on code from https://electrocredible.com
https://electrocredible.com/raspberry-pi-pico-stepper-control-uln2003-micropython

Dec 2023 John Grover
    - original code
    - to do: implement half-step
    - implement degree rotation
"""
import utime
from machine import Pin

class Stepper:

    def __init__(self, in1, in2, in3, in4):

        self.stepper_pins = [in1, in2, in3, in4]
        self.step_index = 0
        
        # http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html
        # half steps per rotation = int(4075.7728395061727 / 8)
        self.full_rotation_steps = 509
        self.delay_min = 3 # (3ms delay)
        
        # Define the sequence of steps for the motor to take
        self.step_sequence = [
        [1, 0, 0, 1],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        ]

        """
        self.half_step_sequence = [
        {1, 0, 0, 0},
        {1, 1, 0, 0},
        {0, 1, 0, 0},
        {0, 1, 1, 0},
        {0, 0, 1, 0},
        {0, 0, 1, 1},
        {0, 0, 0, 1},
        {1, 0, 0, 1}
        ]
        """

    def step(self, direction, steps, delay):
            # bound direction to -1 (back) or 1 (forward)
            if direction < 0:
                direction = -1
            else:
                direction = 1
            
            # minimum delay the motor can handle
            if delay < self.delay_min:
                delay = self.delay_min

            # Loop through the specified number of steps in the specified direction
            for i in range(steps):
                # Add the specified direction to the current step index to get the new step index
                self.step_index = (self.step_index + direction) % len(self.step_sequence)
                
                # Loop through each pin in the motor
                for pin_index in range(len(self.stepper_pins)):
                    # Get the value for this pin from the step sequence using the current step index
                    pin_value = self.step_sequence[self.step_index][pin_index]
                    
                    # Set the pin to this value
                    self.stepper_pins[pin_index].value(pin_value)

                # Delay for the specified amount of time before taking the next step
                utime.sleep_ms(delay)
