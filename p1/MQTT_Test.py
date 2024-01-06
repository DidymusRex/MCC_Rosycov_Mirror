import time
import ubinascii
from umqtt.simple import MQTTClient
import machine
import random
import network
from config import *

# Setup built in PICO LED as Output
led = machine.Pin('LED',machine.Pin.OUT)

# Publish MQTT messages after every set timeout
last_publish = time.time()
publish_interval = 5

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print(f'topic .: {topic.decode()}')
    print(f'message: {msg.decode()}')

    if 'on' in msg.decode():
        led.value(1)
    elif 'reset' in msg.decode():
        reset()
    else:
        led.value(0)

def reset():
    print('Resetting...')
    time.sleep(5)
    machine.reset()
    
# Generate dummy random temperature readings    
def get_temperature_reading():
    return random.randint(20, 50)
    
def main():
    print(f'Begin connection with MQTT Broker :: {MQTT_BROKER}')
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PW, keepalive=60)
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()
    mqttClient.subscribe(MQTT_SUB)

    print(f'Connected to MQTT Broker :: {MQTT_BROKER}')
    print(f'Subscribed to {MQTT_SUB}')
    print(f'waiting for callback function to be called!')

    while True:
            # Non-blocking wait for message
            mqttClient.check_msg()
            global last_publish
            if (time.time() - last_publish) >= publish_interval:
                random_temp = get_temperature_reading()
                mqttClient.publish(PUBLISH_TOPIC, str(random_temp).encode())
                last_publish = time.time()
            time.sleep(1)


if __name__ == '__main__':
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)


    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(SSID, SSID_PW)
    
    while not sta_if.isconnected(): pass
    
    while True:
        try:
            main()
        except OSError as e:
            print('Error: ' + str(e))
            reset()
