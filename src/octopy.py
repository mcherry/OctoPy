#!/usr/bin/python

import fcntl
import json
import os
import pygame
import random
import requests
import signal
import socket
import struct
import sys
import time
import thorpy
from datetime import datetime
from os.path import expanduser
from pytz import timezone
from pygame.locals import *

# required environment variables for pygame
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

timezone = "US/Central";
ds = u'\N{DEGREE SIGN}'

signal.signal(signal.SIGINT, ctrl_c)

def backLight(state):
    file = open("/sys/class/backlight/soc:backlight/brightness","w") 
    file.write(state)
    file.close()
    return

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def getHWAddr(ifname):
    retval = ""
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        retval = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
    except:
        retval = None
    
    if retval == None:
        return "00:00:00:00:00:00"
    else:
        return retval

def getHeaders():
    global dat_key
    
    headers = {
        'Content-Type': 'application/json',
	'X-Api-Key': dat_key
    }

    return headers

def ctrlC(signal, frame):
    pygame.quit() 

def getInfo(api_path):
    response = requests.get("http://octopi.inditech.org/api/" + api_path, headers = getHeaders())

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def postInfo(api_path, command):
    response = requests.post("http://octopi.inditech.org/api/" + api_path, headers = getHeaders(), data = json.dumps(command))
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
	return None

def CtoF(value):
    return `int(round(9 / 5 * value + 32))`

def repeatStr(str, cnt):
    return ''.join([char * cnt for char in str])

def set_blue():
    background.set_main_color((0,0,255))
    background.unblit_and_reblit()

def set_red():
    background.set_main_color((255,0,0))
    background.unblit_and_reblit()

def my_choices_1():
    choices = [("I like blue",set_blue), ("No! red",set_red), ("cancel",None)]
    thorpy.launch_nonblocking_choices("This is a non-blocking choices box!\n", choices)
    print("Proof that it is non-blocking : this sentence is printing!")

def my_choices_2():
    choices = [("I like blue",set_blue), ("No! red",set_red), ("cancel",None)]
    thorpy.launch_blocking_choices("Blocking choices box!\n", choices, parent=background) #for auto unblit
    print("This sentence will print only after you clicked ok")

application = thorpy.Application((320,480), "OctoPy")

button1 = thorpy.make_button("Non-blocking version", func=my_choices_1)
button2 = thorpy.make_button("Blocking version", func=my_choices_2)

background = thorpy.Background.make(elements=[button1,button2])
thorpy.store(background)

menu = thorpy.Menu(background)
menu.play()

application.quit()