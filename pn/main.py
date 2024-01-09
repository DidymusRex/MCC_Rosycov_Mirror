"""
Project: Rosycov Mirror
File:    main.py (for RM device pn)
Target:  Raspberry Pi Pico W with RP2040
Description: TEMPLATE
Puzzle n in the Rosycov Mirror series. 
"""
from config import *
import errno
import gc
import machine
import network
import random
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

# ----------------------------------------------------------
def main():
    last_publish = 0
    publish_interval = 1

    print('connecting to WiFi')
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(ssid, ssid_pw)
    
    while not sta_if.isconnected(): pass
 
    print(f'Connecting to MQTT Broker :: {mqtt_broker}')
    mqttClient = MQTTClient(mqtt_client_id, mqtt_broker, user=mqtt_username, password=mqtt_password, keepalive=60)
    mqttClient.connect()

    print(f'Subscribing to MQTT Broker :: {mqtt_broker}')
    mqttClient.set_callback(sub_cb)
    mqttClient.subscribe(mqtt_subscribe_topic)
    print(f'Subscribed to {mqtt_subscribe_topic} listening for message')

    # tell the console we are up and running
    print(f'Sending status = online')
    mqtt_publish(mqttClient, mqtt_root + '/status', 'poweron')
    
    # give the game master needed information
    print(f'Sending cheat')
    cheat()

    while 1==1:
        mqttClient.check_msg()
        if (time.time() - last_publish) >= publish_interval:
            r = random.randint(1,100)
            mqttClient.publish(mqtt_root + '/random', str(r).encode())
            last_publish = time.time()

    # solution achieved!
    solved()

# ----------------------------------------------------------
if __name__ == '__main__':
    main()

# ----------------------------------------------------------
# ----------------------------------------------------------


