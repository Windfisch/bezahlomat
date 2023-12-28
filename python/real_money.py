import os
import threading
import time
import RPi.GPIO as g
import time

INHIBIT_PIN=40
MONEY_PIN=38
CENTS_PER_PULSE=500
TIMEOUT = 0.3

amount = 0
lock = threading.Lock()
callback = None
timer = None

def pulse_done_cb():
    global amount
    global timer

    print("PULSE DONE")

    with lock:
        timer.cancel()
        timer = None
        saved_amount = amount
        amount = 0
    print("callback")
    callback(saved_amount/100)

def pulse_cb(x):
    global amount
    global timer
    print("PULSE")
    with lock:
        amount += CENTS_PER_PULSE
        if timer is not None: timer.cancel()
        timer = threading.Timer(TIMEOUT, pulse_done_cb)
        timer.start()
        print("ok")


g.setmode(g.BOARD)

g.setup(INHIBIT_PIN, g.OUT)
g.output(INHIBIT_PIN, True)

g.setup(MONEY_PIN, g.IN, pull_up_down = g.PUD_UP)
g.add_event_detect(MONEY_PIN, g.FALLING, callback = pulse_cb, bouncetime=130)

def watch(cb):
    global callback
    callback = cb

def enable():
    g.output(INHIBIT_PIN, False)

def disable():
    g.output(INHIBIT_PIN, True)
