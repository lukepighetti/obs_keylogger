#!/usr/bin/python
from dotenv import load_dotenv
from os import getenv
from pynput import keyboard
import paho.mqtt.client as mqtt

load_dotenv()
MQTT_HOST = getenv('MQTT_HOST')

client = mqtt.Client()

last_message = None
last_message_count = 0
current_modifier_keys = set()
current_modifier_chars = set()

def print_and_broadcast(message):
    print(message)
    client.publish('obs_keylogger/macbook', message)

def on_press(key):
    global last_message, last_message_count, current_modifier_keys, current_modifier_chars
    try:
        char = key.char
        message = ''.join(current_modifier_chars) + char
        if char == None:
            return
        elif last_message == message:
            last_message_count = last_message_count + 1
            print_and_broadcast(f'+{last_message_count}')
        else:
            last_message = message;
            last_message_count = 1
            print_and_broadcast(message)

    except AttributeError:
        modifier = False
        char = None
         
        match key:
            case keyboard.Key.backspace:
                char = '⌫'
            case keyboard.Key.enter:
                char = '⏎'
            case keyboard.Key.delete:
                char = '⌦'
            case keyboard.Key.space:
                char = '⎵'
            case keyboard.Key.esc:
                char = '⎋'
            case keyboard.Key.tab:
                char = '⇥'
            case keyboard.Key.up:
                char = '↑'
            case keyboard.Key.right:
                char = '→'
            case keyboard.Key.down:
                char = '↓'
            case keyboard.Key.left:
                char = '←'
            case keyboard.Key.shift | keyboard.Key.shift_r:
                modifier = True
                char = '⇧'
            case keyboard.Key.cmd | keyboard.Key.cmd_r:
                modifier = True
                char = '⌘'
            case keyboard.Key.ctrl | keyboard.Key.ctrl_r:
                modifier = True
                char = '^'
            case keyboard.Key.alt | keyboard.Key.alt_r:
                modifier = True
                char = '⎇'
            case _:
                char = key
        
        if modifier:
            current_modifier_keys.add(key)
            current_modifier_chars.add(char)
        else: 
            print_and_broadcast(char)

        last_message = None
        last_message_count = 1

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


