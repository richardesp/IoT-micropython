"""
fernando.leon@uco.es
University of Córdoba, Spain
2021
"""

from drivers.sx127x import SX127x
import uasyncio as asyncio
from machine import Pin, SPI
from time import sleep, sleep_ms


class LoraSenderApp:
    DEVICE_CONFIG = {
        'miso':19,
        'mosi':27,
        'ss':18,
        'sck':5,
        'dio_0':23,
        'reset':9, 
    }

    LORA_PARAMETERS = {
        'frequency': 433E6, 
        'tx_power_level': 2, 
        'signal_bandwidth': 125E3,    
        'spreading_factor': 8, 
        'coding_rate': 5, 
        'preamble_length': 8,
        'implicit_header': False, 
        'sync_word': 0x12, 
        'enable_CRC': False,
        'invert_IQ': False,
    }
    
    APP_PARAMETERS = {
        'btn_pin': 36,
    }

    def __init__(self):
        # button
        self.push_button = Pin(LoraSenderApp.APP_PARAMETERS['btn_pin'], Pin.IN)
        #self.push_button.irq(trigger=Pin.IRQ_RISING, handler=lambda pin: self.ButtonIRQ())
        
        # spi interface
        self.device_spi = SPI(baudrate = 10000000, 
                                polarity = 0, phase = 0, bits = 8, firstbit = SPI.MSB,
                                sck = Pin(LoraSenderApp.DEVICE_CONFIG['sck'], Pin.OUT, Pin.PULL_DOWN),
                                mosi = Pin(LoraSenderApp.DEVICE_CONFIG['mosi'], Pin.OUT, Pin.PULL_UP),
                                miso = Pin(LoraSenderApp.DEVICE_CONFIG['miso'], Pin.IN, Pin.PULL_UP))
        # driver lora
        self.lora = SX127x(self.device_spi, pins=LoraSenderApp.DEVICE_CONFIG, parameters=LoraSenderApp.LORA_PARAMETERS)
        
        # Lock
        self.lock_button_push = asyncio.Lock()
        self.lock_button_push.acquire()
        
        # Tasks
        asyncio.create_task(self.TriggeredSend())
        asyncio.create_task(self.CheckButton())
        
    async def CheckButton(self):
        while True:
            if self.push_button.value():
                print("Push")
                self.lock_button_push.release() # release the lock
                await asyncio.sleep_ms(250)
            await asyncio.sleep_ms(10)
            
    async def TriggeredSend(self):
        while True:
            await self.lock_button_push.acquire() # wait for lock release
            
            #send a packet
            payload = '*'
            print("Sending packet: \n{}\n".format(payload))
            self.lora.println(payload)

    def Loop(self):
        evtloop = asyncio.get_event_loop()
        evtloop.run_forever()