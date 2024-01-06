"""
Project: Rosycov Mirror
File:    main.py (for RM device p2)
Target:  Raspberry Pi Pico W with RP2040
Description:
Puzzle two in the Rosycov Mirror series. 
"""
from config import *
from grids import *
from umqtt.simple import MQTTClient

import errno
import gc
import i2c_lcd
import machine
import neopixel
import sys
import network
import time
import ubinascii

# Setup built in PICO LED as Output
led = machine.Pin('LED', machine.Pin.OUT)

# set up the neopixels as a 6x12 grid
npxPin = 16
npxHeight = 12
npxWidth = 6
npxLength = npxHeight * npxWidth
np = neopixel.Neopixel(npxLength, 0, 16, "GRB")

# some handy color tuples
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
off = (0,0,0)

# flow red to green through yellow in 12 steps
redToGreen=[(255,0,0),(231,23,0),(208,46,0),
            (185,69,0),(162,92,0),(139,115,0),
            (115,139,0),(92,162,0),(69,185,0),
            (46,208,0),(23,231,0),(0,255,0)]
# actually flow green to red ...
redToGreen.reverse()

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

i2c = machine.SoftI2C(scl=machine.Pin(15), sda=machine.Pin(14), freq=10000)
lcd = i2c_lcd.I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# ----------------------------------------------------------

# perform a soft machine.reset
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

def start():
    pass

# execute command received via MQTT
def do_command(command):
    if 'start' in command:
        start()
    elif 'stop' in command:
        sys.exit()
    elif 'reset' in command:
        machine.reset()
    elif 'debug' in command:
        debug()
    elif 'cheat' in command:
        cheat()
    elif 'clear' in command:
        lcd.clear()
        np_init()
    elif 'on' in command:
        led.value(1)
    elif 'off'in command:
        led.value(0)
    else:
        print(f'unknown command {msg}')

# process data received via MQTT
#  we expect that data is received from topic
# mcc/p1/data in the format aa:aa bb:bb cc:cc
stack = [None,None,None,None,None,None,None,None,None,None,None,None] 
max_stack = 11
stack_index = 0
msg_count = 0

def process_data(m):
    global stack, max_stack, stack_index, msg_count

    msg_count = msg_count +1
    lcd_message(line1=f'msg count {msg_count}', line2=m)

    stack[stack_index] == m
    stack_index = stack_index + 1

    # roll the stack
    if stack_index > max_stack:
        stack_index = 0

    # status maxed out or not
    if msg_count >= max_stack +1:
        np_status(max_stack +1)
    else:
        np_status(msg_count)

# messages from subscriptions will be delivered to this callback
def mqtt_sub_callback(topic, msg):
    global led

    t=topic.decode()
    m=msg.decode()
    
    print('received')
    print(f'topic ....: {t}')
    print(f'message ..: {m}')

    if 'command' in t:
        do_command(m)
    elif 'data' in t:
        process_data(m)
    else:
        print('skip message')


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
    global off
    
    # bounds check
    if n <= 0:
        n=1
    if n > npxHeight:
        n = npxHeight

    print(f'np status {n}')

    # light up rows 0-n
    for r in range(0,n):
        for p in grid[r]:
            np[p]=redToGreen[r]
    # turn off rows n+1 - max
    for r in range(n+1, npxHeight):
        for p in grid[r]:
            np[p]=off

    np.show()

# write up to two lines to LCD
def lcd_message(line1, line2=None):
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(line1)
    if line2 is not None:
        lcd.move_to(0,1)
        lcd.putstr(line2)


# ----------------------------------------------------------
def main():
    lcd_message(line1='system online')

    while True:
        mqttClient.check_msg()
        # callback will process the message

        time.sleep(.5)

    # solution achieved!
    solved()

# ----------------------------------------------------------
if __name__ == '__main__':
    print ('not imported from boot.py')

else:
    # power on sequence
    last_publish = 0
    publish_interval = 1

    # turn off np grid and LCD
    np_init()
    lcd.clear()

    # connect to WiFi
    lcd_message(line1='connect WiFi')
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(SSID, SSID_PW)
    
    while not sta_if.isconnected(): pass

    # connect to MQTT broker
    lcd_message(line1='connect console')
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PW, keepalive=60)

    mqttClient.connect()
    lcd_message(line1='console on')

    # subscribe to commands and data
    mqttClient.set_callback(mqtt_sub_callback)
    mqttClient.subscribe(MQTT_COMMAND)
    print(f'Subscribed to {MQTT_COMMAND} listening for commands')

    mqttClient.subscribe(MQTT_DATA)
    print(f'Subscribed to {MQTT_DATA} listening for data')

    # tell the console we are up and running
    print(f'Sending status online')
    mqtt_publish(mqttClient, MQTT_ROOT + '/status', 'poweron')
    
    # give the game master needed information
    print(f'Sending cheat')
    cheat()

    # ToDo: wait for start command
    lcd_message(line1='standby')

    # This protects against a memory error and resets the Pico
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            machine.reset()

# ----------------------------------------------------------
# ----------------------------------------------------------
