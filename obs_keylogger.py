#!/usr/bin/python
from dotenv import load_dotenv
from os import getenv
from pynput import keyboard
import paho.mqtt.client as mqtt

load_dotenv()
MQTT_HOST = getenv('MQTT_HOST')

client = mqtt.Client()

last_char = None
last_char_count = 0
current_modifier_keys = set()
current_modifier_chars = set()

def print_and_broadcast(message):
    print(message)
    client.publish('obs_keylogger/macbook', message)

def on_press(key):
    global last_char, last_char_count, current_modifier_keys, current_modifier_chars
    try:
        char = key.char;
        if last_char == char:
            last_char_count = last_char_count + 1
            print_and_broadcast(f'+{last_char_count}')
        else:
            last_char = key.char;
            last_char_count = 1
            if char == None:
                return
            elif len(current_modifier_chars) >0:
                print_and_broadcast(''.join(current_modifier_chars)  + char)
            else: 
                print_and_broadcast(char)

    except AttributeError:
        modifier = False
        char = None

        if key == keyboard.Key.backspace:
            char = '⌫'
        elif key == keyboard.Key.enter:
            char = '⏎'
        elif key == keyboard.Key.delete:
            char = '⌦'
        elif key == keyboard.Key.space:
            char = '⎵'
        elif key == keyboard.Key.esc:
            char = '⎋'
        elif key == keyboard.Key.tab:
           char = '⇥'
        elif key == keyboard.Key.up:
            char = '↑'
        elif key == keyboard.Key.right:
            char = '→'
        elif key == keyboard.Key.down:
            char = '↓'
        elif key == keyboard.Key.left:
            char = '←'
        elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            modifier = True
            char = '⇧'
        elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
            modifier = True
            char = '⌘'
        elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
            modifier = True
            char = '^'
        elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
            modifier = True
            char = '⎇'
        else:
            char = key
        
        if modifier:
            current_modifier_keys.add(key)
            current_modifier_chars.add(char)
        else: 
            print_and_broadcast(char)

        last_char = None
        last_char_count = 1

def on_release(key):
    global  current_modifier_keys, current_modifier_chars
    modifier = None
    symbol = None

    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        modifier = True
        symbol = '⇧'
    elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
        modifier = True
        symbol = '⌘'
    elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
        modifier = True
        symbol = '^'
    elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
        modifier = True
        symbol = '⎇'

    if modifier:
        current_modifier_keys.remove(key)
        current_modifier_chars.remove(symbol)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

client.on_connect = on_connect
client.on_connect_fail = print
client.on_disconnect = print

client.connect(MQTT_HOST, 1883, 60)
client.loop_forever()


