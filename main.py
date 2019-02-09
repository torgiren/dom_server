#!/usr/bin/env python
import paho.mqtt.client as mqtt
import time
import sched
import threading

sched_run = True

timers = {}
output_disabled = {}

def scheduler_loop():
    while sched_run:
        if s.queue:
            print("Sched loop", time.time(), s.queue)
        s.run(blocking=False)
        time.sleep(1)
def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe("domek/+/out")

def on_message(client, userdata, msg):
    print("Got: " + str(msg.payload))
    if msg.topic == "domek/przedpokoj/out":
        process_przedpokoj(msg)

def process_przedpokoj(msg):
    print("Z domku")
    if msg.payload.decode() == "new:5:1":
        print("Wlacz")
        if not output_disabled.get("przedpokoj_5"):
            s.enter(0, 1, client.publish, argument=("domek/przedpokoj/in", "set:4:0"))
            if timers.get('przedpokoj_5') in s.queue:
                s.cancel(timers.get('przedpokoj_5'))
    elif msg.payload.decode() == "new:5:0":
        print("Wylacz")
        turn_off_time = time.time() + 5
        if timers.get('przedpokoj_5') in s.queue:
            if timers.get('przedpokoj_5').time < turn_off_time:
                s.cancel(timers.get('przedpokoj_5'))
                timers['przedpokoj_5'] = s.enterabs(turn_off_time, 1, client.publish, argument=("domek/przedpokoj/in","set:4:1"))
        else:
            timers['przedpokoj_5'] = s.enterabs(turn_off_time, 1, client.publish, argument=("domek/przedpokoj/in","set:4:1"))
#       client.publish("domek/przedpokoj/in", "set:4:1")
    elif msg.payload.decode().startswith("oneshot:5:"):
        print("oneshot")
        if timers.get('przedpokoj_5') in s.queue:
            s.cancel(timers.get('przedpokoj_5'))
        s.enter(0, 1, client.publish, argument=("domek/przedpokoj/in","set:4:0"))
        t = int(msg.payload.decode().split(':')[-1])
        print(t)
        s.enter(0, 1, client.publish, argument=("domek/przedpokoj/in","set:4:0"))
        timers['przedpokoj_5'] = s.enter(t, 1, client.publish, argument=("domek/przedpokoj/in","set:4:1"))

s = sched.scheduler(time.time, time.sleep)
threading.Thread(target=scheduler_loop).start()

client = mqtt.Client()
client.connect("192.168.0.25", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
