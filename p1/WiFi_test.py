import network
import time

print('Connecting to ND-guest')

# Initialize the WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('ND-guest')

# Wait for WiFi connection
print('Connecting to WiFi...')
timeout = time.time() + 60
while not wlan.isconnected() and time.time() < timeout:
    print('Connecting...')
    time.sleep(5)

if not wlan.isconnected():
    print('Failed to connect to WiFi. Exiting...')
    raise SystemExit

# Display the IP address on the REPL
print('WiFi connected. Network config:', wlan.ifconfig())

