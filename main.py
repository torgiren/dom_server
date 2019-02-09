#!/usr/bin/env python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe("domek/+/out")

def on_message(client, userdata, msg):
    print("Got: " + str(msg.payload))
    if msg.topic == "domek/przedpokoj/out":
        print("Z domku")
        if msg.payload.decode() == "new:5:1":
            print("Wlacz")
            client.publish("domek/przedpokoj/in", "set:4:0")
        elif msg.payload.decode() == "new:5:0":
            print("Wylacz")
            client.publish("domek/przedpokoj/in", "set:4:1")

client = mqtt.Client()
client.connect("192.168.0.25", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
