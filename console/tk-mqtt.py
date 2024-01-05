import tkinter as tk
import os
import paho.mqtt.client as mqtt
from pygame import mixer
from config import *

class MQTTWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Rosycov Mirror Status")

        # Configure the window to be full-screen without a title bar
        self.master.attributes("-fullscreen", True)

        # Initialize the mixer for sound playback
        mixer.init()

        # Create text boxes
        self.p1_box = self.create_text_box("mcc/p1/event", "p1", "red")
        self.p2_box = self.create_text_box("mcc/p2/event", "p2", "yellow")
        self.p3_box = self.create_text_box("mcc/p3/event", "p3", "green")

        # Create buttons
        self.publish_button = tk.Button(self.master, text="Publish", command=self.publish_message)
        self.publish_button.pack(side=tk.TOP, pady=10)

        self.reset_p1_button = tk.Button(self.master, text="Reset P1", command=lambda: self.publish_reset("mcc/p1/status"))
        self.reset_p1_button.pack(side=tk.LEFT, padx=10)

        self.reset_p2_button = tk.Button(self.master, text="Reset P2", command=lambda: self.publish_reset("mcc/p2/status"))
        self.reset_p2_button.pack(side=tk.LEFT, padx=10)

        self.reset_p3_button = tk.Button(self.master, text="Reset P3", command=lambda: self.publish_reset("mcc/p3/status"))
        self.reset_p3_button.pack(side=tk.LEFT, padx=10)

        # MQTT client setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(username=mqtt_username, password=mqtt_password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Connect to the MQTT broker
        self.mqtt_client.connect(mqtt_broker, mqtt_port, 60)

        # Start the MQTT loop
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribe to the MQTT topics upon successful connection
        client.subscribe("mcc/p1/event")
        client.subscribe("mcc/p2/event")
        client.subscribe("mcc/p3/event")
        client.subscribe("mcc/console/sound")
        client.subscribe("mcc/console/speak")

    def on_message(self, client, userdata, msg):
        # Update the appropriate text box with the received MQTT message
        topic = msg.topic
        message = msg.payload.decode("utf-8")

        if topic == "mcc/console/sound":
            self.play_sound(message)
        elif topic == "mcc/console/speak":
            self.speak_text(message)
        elif topic == "mcc/p1/event":
            self.update_text_box(self.p1_box, message)
        elif topic == "mcc/p2/event":
            self.update_text_box(self.p2_box, message)
        elif topic == "mcc/p3/event":
            self.update_text_box(self.p3_box, message)

    def create_text_box(self, topic, name, color):
        text_box = tk.Text(self.master, height=5, width=40, bg="black", fg=color)
        text_box.pack(padx=10, pady=10, fill=tk.X)
        text_box.tag_configure("tag-center", justify="center")
        text_box.insert(tk.END, name + " Box\n", "tag-center")
        text_box.insert(tk.END, "-------------------\n")
        self.master.update_idletasks()
        text_box.see(tk.END)
        self.master.update_idletasks()
        return text_box

    def update_text_box(self, text_box, message):
        # Determine the text color based on the message content
        if "error" in message.lower():
            text_color = "red"
        elif "warning" in message.lower():
            text_color = "yellow"
        else:
            text_color = "green"

        # Update the text box with the appropriate color
        text_box.config(fg=text_color)
        text_box.insert(tk.END, message + "\n")
        text_box.see(tk.END)

    def play_sound(self, sound_file):
        mixer.music.load(sfx_location + sound_file)
        mixer.music.play()

    def speak_text(self, text):
        # this is an insecure methodlogy...
        os.system(f'espeak "{text}"')

    def publish_message(self):
        # Publish the message "button" to the specified MQTT topic
        self.mqtt_client.publish(mqtt_publish_topic, "button")

    def publish_reset(self, topic):
        # Publish the message "reset" to the specified MQTT topic
        self.mqtt_client.publish(topic, "reset")

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTWindow(root)
    root.mainloop()
