"""
Project: Rosycov Mirror
File:    main.py (for RM device p2)
Target:  Raspberry Pi Pico W with RP2040
Description:
Puzzle two in the Rosycov Mirror series. 
"""
from config import *
import errno
import gc
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from machine import SoftI2C, Pin, PWM, reset
from neopixel import Neopixel
import network
from random import randint
import time
import ubinascii
from umqtt.simple import MQTTClient

# Setup built in PICO LED as Output
led = machine.Pin('LED',machine.Pin.OUT)

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
redToGreen=((255,0,0),(231,23,0),(208,46,0),
            (185,69,0),(162,92,0),(139,115,0),
            (115,139,0),(92,162,0),(69,185,0),
            (46,208,0),(23,231,0),(0,255,0))

# create dictionary grid of rows on neopixel strip
grid = dict()
for row in range(npxHeight):
    r=list()
    for col in range(npxWidth):
        r.append((col*npxHeight)+row)
        
    grid[row] = r

# set up the LCD
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(5), sda=Pin(6), freq=10000)
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# ----------------------------------------------------------

# perform a soft reset
def reset():
    debug()
    print('Reset:')
    time.sleep(5)
    machine.reset()

# gah!
def debug():
    print('Debug:')
    print(f'memory used {gc.mem_alloc()}')
    print(f'memory free {gc.mem_free()}')

# cheat for the game master
def cheat():
    print('Cheat:')
    pass

# messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global led

    print('received')
    print(f'topic ....: {topic.decode()}')
    print(f'message ..: {msg.decode()}')

    if 'reset' in msg.decode():
        reset()
    elif 'debug' in msg.decode():
        debug()
    elif 'cheat' in msg.decode():
        cheat()
    elif 'on' in msg.decode():
        led.value(1)
    elif 'off'in msg.decode():
        led.value(0)
    else:
        print(f'unknown command {msg}')

# publish a message on a topic to the mqtt broker
def mqtt_publish(client, topic, message):
    client.publish(topic, message)

    print('sent')
    print(f'client....: {client}')
    print(f'topic ....: {topic}')
    print(f'message ..: {message}')

# notify the console the puzzle is solved
def solved():
    debug()

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

# ----------------------------------------------------------
def main():
    last_publish = 0
    publish_interval = 1

    print('connecting to WiFi')
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(SSID, SSID_PW)
    
    while not sta_if.isconnected(): pass
 
    print(f'Connecting to MQTT Broker :: {MQTT_BROKER}')
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PW, keepalive=60)

    mqttClient.connect()
    print(f'Connected to MQTT Broker :: {MQTT_BROKER}')
    
    mqttClient.set_callback(sub_cb)
    mqttClient.subscribe(MQTT_SUB)
    print(f'Subscribed to {MQTT_SUB} listening for message')

    # tell the console we are up and running
    print(f'Sending status online')
    mqtt_publish(mqttClient, MQTT_ROOT + '/status', 'online')
    
    # give the game master needed information
    print(f'Sending cheat')
    cheat()

    while True:
        mqttClient.check_msg()
        if (time.time() - last_publish) >= publish_interval:
            random = randint(0, npxHeight-1)
            mqttClient.publish(MQTT_ROOT + '/random', str(random).encode())
            last_publish = time.time()
            np_status(random)
        
    # solution achieved!
    solved()

# ----------------------------------------------------------
if __name__ == '__main__':
    main()

# ----------------------------------------------------------
# ----------------------------------------------------------
