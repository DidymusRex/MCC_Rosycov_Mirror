import ubinascii

SSID='grover_net'
SSID_PW='open says me'

MQTT_USER='mcc'
MQTT_PW='mcc'
MQTT_BROKER = "192.168.100.22"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
SUBSCRIBE_TOPIC = b"led"
PUBLISH_TOPIC = b"temperature"
