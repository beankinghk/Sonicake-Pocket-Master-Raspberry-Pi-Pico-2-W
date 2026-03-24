import asyncio
import aioble
import bluetooth
import time
import struct
import ubinascii
from machine import Pin
from micropython import const

##### Setup BLE #####

# 1. Setup UUIDs
_MIDI_SERVICE_UUID = bluetooth.UUID("03B80E5A-EDE8-4B33-A751-6CE34EC4C700")
_MIDI_CHAR_UUID = bluetooth.UUID("7772E5DB-3868-4112-A1A9-F2669D106BF3")

# 2. Register Service & Characteristic
midi_service = aioble.Service(_MIDI_SERVICE_UUID)
midi_characteristic = aioble.Characteristic(midi_service, _MIDI_CHAR_UUID, read=True, write=True, notify=True)

aioble.register_services(midi_service)

##### Function in below #####

# Define key first

debounce = 0.2
red_button = Pin(2, Pin.IN, Pin.PULL_UP)
blue_button = Pin(3, Pin.IN, Pin.PULL_UP)
yellow_button = Pin(4, Pin.IN, Pin.PULL_UP)
green_button = Pin(5, Pin.IN, Pin.PULL_UP)
red_toggle = 0
blue_toggle = 0
yellow_toggle = 0
green_toggle = 0

# 3. The key press section while connected

async def key_press(connection):
    print("Starting Output")
    
    while True:
        
        global red_toggle
        
        if red_button.value() == 0 and red_toggle == 0:  # Button pressed
                print("Pressed Red")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X2C, 0X00])
                midi_characteristic.notify(connection, txdata)
                print("Sent Red 00")
                red_toggle = 1
                await asyncio.sleep(debounce)

        if red_button.value() == 0 and red_toggle == 1:  # Button pressed
                print("Pressed Red")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X2C, 0X7F])
                midi_characteristic.notify(connection, txdata)
                print("Sent Red 7F")
                red_toggle = 0
                await asyncio.sleep(debounce)
            
        global blue_toggle
        
        if blue_button.value() == 0 and blue_toggle == 0:  # Button pressed
                print("Pressed Blue")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X2D, 0X00])
                midi_characteristic.notify(connection, txdata)
                print("Sent Blue 00")
                blue_toggle = 1
                await asyncio.sleep(debounce)

        if blue_button.value() == 0 and blue_toggle == 1:  # Button pressed
                print("Pressed Blue")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X2D, 0X7F])
                midi_characteristic.notify(connection, txdata)
                print("Sent Blue 7F")
                blue_toggle = 0
                await asyncio.sleep(debounce)
            
        global yellow_toggle
        
        if yellow_button.value() == 0 and yellow_toggle == 0:  # Button pressed
                print("Pressed yellow")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X31, 0X00])
                midi_characteristic.notify(connection, txdata)
                print("Sent yellow 00")
                yellow_toggle = 1
                await asyncio.sleep(debounce)

        if yellow_button.value() == 0 and yellow_toggle == 1:  # Button pressed
                print("Pressed yellow")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X31, 0X7F])
                midi_characteristic.notify(connection, txdata)
                print("Sent yellow 7F")
                yellow_toggle = 0
                await asyncio.sleep(debounce)
            
        global green_toggle
        
        if green_button.value() == 0 and green_toggle == 0:  # Button pressed
                print("Pressed green")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X32, 0X00])
                midi_characteristic.notify(connection, txdata)
                print("Sent green 00")
                green_toggle = 1
                await asyncio.sleep(debounce)

        if green_button.value() == 0 and green_toggle == 1:  # Button pressed
                print("Pressed green")
                txdata = bytearray([0x80, 0X80, 0XB0, 0X32, 0X7F])
                midi_characteristic.notify(connection, txdata)
                print("Sent green 7F")
                green_toggle = 0
                await asyncio.sleep(debounce)
             
# 4. The Main Loop
async def main():
    
    while True:
        print("Advertising 'BK-Pico2W-MIDI-CTR'...")
        # Wait here until a device (phone/PC) connects
        connection = await aioble.advertise(20_000, name="BK-Pico2W-MIDI-CTR", services=[_MIDI_SERVICE_UUID])
        
        print(f"Connected to {connection.device}!")
        
        # Run the key press section and wait for it to finish (on disconnect)
        await key_press(connection)
        
        print("Disconnected. Restarting in 2 seconds...")
        await asyncio.sleep(2)

# Start the program
asyncio.run(main())

##### The End #####