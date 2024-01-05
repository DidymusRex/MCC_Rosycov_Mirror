# boot_neoFx.py
from machine import Pin, reset
from neopixel import Neopixel
from random import randint
from time import sleep, sleep_ms

# set up the neopixels as a 6x12 grid
npxPin = 16
npxHeight = 12
npxWidth = 6
npxLength = npxHeight * npxWidth
np = Neopixel(npxLength, 0, 16, "GRB")

# some handy color tuples
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
off = (0,0,0)

# flow red to green through yellow in 12 steps
redToGreen=((255,0,0),(231,23,0),(208,46,0),(185,69,0),(162,92,0),(139,115,0),(115,139,0),(92,162,0),(69,185,0),(46,208,0),(23,231,0),(0,255,0))

# create dictionary grid of rows on neopixel strip
grid = dict()
for row in range(npxHeight):
    r=list()
    for col in range(npxWidth):
        r.append((col*npxHeight)+row)
        
    grid[row] = r

# turn off the entire strip
def np_init():
    global off
    
    np.fill(off)
    np.show()

# light up the grid to row n
def np_status(n):
    global grid
    global npxHeight
    
    # bounds check
    if n < 0:
        n=0
    if n > npxHeight:
        n = npxHeight

    # light up rows 0-n
    for r in range(0,n):
        for p in grid[r]:
            np[p]=redToGreen[r]
    # turn of rows n+1 - max
    for r in range(n+1, npxHeight):
        for p in grid[r]:
            np[p]=off

    np.show()

def main():
    for x in range(100):
        s = randint(0, npxHeight-1)
        np_status(s)
        sleep(.1)

# ----------------------------------------------------------
if __name__ == '__main__':
    np_init()
    main()
    np_init()
