import asyncio
import aioble
import bluetooth
from machine import Pin

##### Setup BLE #####
_MIDI_SERVICE_UUID = bluetooth.UUID("03B80E5A-EDE8-4B33-A751-6CE34EC4C700")
_MIDI_CHAR_UUID = bluetooth.UUID("7772E5DB-3868-4112-A1A9-F2669D106BF3")

midi_service = aioble.Service(_MIDI_SERVICE_UUID)
midi_characteristic = aioble.Characteristic(midi_service, _MIDI_CHAR_UUID, read=True, write=True, notify=True)
aioble.register_services(midi_service)

##### Def Buttonns #####
buttons = [
    {"pin": 2, "cc": 0x2C, "name": "Red"},
    {"pin": 3, "cc": 0x2D, "name": "Blue"},
    {"pin": 4, "cc": 0x31, "name": "Yellow"},
    {"pin": 5, "cc": 0x32, "name": "Green"},
]

debounce_ms = 170

# 3. To handle key press
async def handle_button(btn_conf, connection):
    pin = Pin(btn_conf["pin"], Pin.IN, Pin.PULL_UP)
    toggle = 0
    last_state = 1 # 1 是未按下 (PULL_UP)
    
    while True:
        current_state = pin.value()
        
        # 偵測按下動作 (從 1 變 0) - Detect Pin short to GND
        if last_state == 1 and current_state == 0:
            print(f"Pressed {btn_conf['name']}")
            
            # 切換 MIDI 數值 (00 或 7F)
            val = 0x7F if toggle == 0 else 0x00
            txdata = bytearray([0x80, 0x80, 0xB0, btn_conf["cc"], val])
            
            try:
                midi_characteristic.notify(connection, txdata)
                print(f"Sent {btn_conf['name']} {val:02X}")
                toggle = 1 - toggle # 切換狀態
            except Exception as e:
                print(f"Notify error: {e}")
                break # 發生錯誤（通常是斷開連接）跳出循環
                
            # 只針對這一個按鍵進行消抖，不會影響其他 Task
            await asyncio.sleep_ms(debounce_ms)
        
        last_state = current_state
        # 給予極短的釋放時間讓 CPU 處理其他協程
        await asyncio.sleep_ms(10)

# 2. Loop key scan (Part.3)
async def key_press_handler(connection):
    print("Starting Multi-Button Output")
    tasks = []
    
    # 為每個按鍵建立一個併發任務
    for item in buttons:
        tasks.append(asyncio.create_task(handle_button(item, connection)))
    
    # 等待直到連接斷開（監控連線狀態）
    try:
        await connection.disconnected()
    finally:
        # 斷開後取消所有按鍵任務
        for t in tasks:
            t.cancel()
        print("Cleaning up button tasks...")

# 1. Main Loop
async def main():
    while True:
        print("Advertising 'BK-Pico2W-MIDI-CTR'...")
        try:
            connection = await aioble.advertise(
                250_000, 
                name="BK-Pico2W-MIDI-CTR", 
                services=[_MIDI_SERVICE_UUID]
            )
            print(f"Connected to {connection.device}!")
            
            # Go to loop Part.2
            await key_press_handler(connection)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error: {e}")
        
        print("Disconnected. Restarting in 2 seconds...")
        await asyncio.sleep(2)

asyncio.run(main())
### The End ###
