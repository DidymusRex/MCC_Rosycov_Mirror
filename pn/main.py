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
from machine import Pin, PWM
import network
from random import randint
import time
import ubinascii
from umqtt.simple import MQTTClient

# Setup built in PICO LED as Output
led = machine.Pin('LED',machine.Pin.OUT)

# ----------------------------------------------------------

# perform a soft reset
def reset():
    debug()
    print('Reset:')
    sleep(5)
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

    while 1==1:
        mqttClient.check_msg()
        if (time.time() - last_publish) >= publish_interval:
            random = randint(1,100)
            mqttClient.publish(MQTT_ROOT + '/random', str(random).encode())
            last_publish = time.time()

    # solution achieved!
    solved()

# ----------------------------------------------------------
if __name__ == '__main__':
    main()

# ----------------------------------------------------------
# ----------------------------------------------------------

