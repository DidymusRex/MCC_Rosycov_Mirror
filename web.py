"""
Demo Five: Control an LED from the web
    Credit: ChatGPT
"""
import machine
import network
import usocket as socket
import time
import ssd1306

# Initialize the OLED display
i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize the LED pin
led = machine.Pin(16, machine.Pin.OUT)

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

# Define the HTML for the web page
web_page = """
<!DOCTYPE html>
<html>
<head>
  <title>Pico Web Demo</title>
</head>
<body>
  <h1>Pico Web Demo</h1>
  <form method="POST">
    <label for="textbox">Text:</label>
    <input type="text" id="textbox" name="textbox">
    <input type="submit" value="Submit">
  </form>
  <form method="POST">
    <input type="submit" value="LED Control" onclick="toggleLED()">
  </form>
  <script>
    function toggleLED() {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/led");
      xhr.send();
    }
  </script>
</body>
</html>
"""

# Define the function to handle web requests
def handle_request(conn):
    request = conn.recv(1024)
    # had to fix this line. str(request) to request.decode()
    # to remove b' from result
    request_str = request.decode()
    request_method = request_str.split(' ')[0]
    request_path = request_str.split(' ')[1]

    if request_method == 'POST' and request_path == '/led':
        led.value(not led.value())
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n')
        conn.send('LED toggled')
    else:
        if 'textbox=' in request_str:
            text = request_str.split('textbox=')[1].split(' ')[0].replace('+', ' ')
            oled.fill(0)
            oled.text(text, 0, 10)
            oled.show()
        
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n')
        conn.send(web_page)

    conn.close()

# Start the web server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
print('Web server started.')

# Loop forever and handle incoming connections
while True:
    conn, addr = s.accept()
    handle_request(conn)

