"""
fernando.leon@uco.es
University of Córdoba, Spain
2021
"""

from drivers.sx127x import SX127x
import uasyncio as asyncio
from machine import Pin, SPI
from time import sleep, sleep_ms


class LoraReceiverApp:
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
        'led_pin': 32,
    }

    def __init__(self):
        # button
        self.led = Pin(LoraReceiverApp.APP_PARAMETERS['led_pin'], Pin.OUT)
        
        # spi interface
        self.device_spi = SPI(baudrate = 10000000, 
                                polarity = 0, phase = 0, bits = 8, firstbit = SPI.MSB,
                                sck = Pin(LoraReceiverApp.DEVICE_CONFIG['sck'], Pin.OUT, Pin.PULL_DOWN),
                                mosi = Pin(LoraReceiverApp.DEVICE_CONFIG['mosi'], Pin.OUT, Pin.PULL_UP),
                                miso = Pin(LoraReceiverApp.DEVICE_CONFIG['miso'], Pin.IN, Pin.PULL_UP))
        # driver lora
        self.lora = SX127x(self.device_spi, pins=LoraReceiverApp.DEVICE_CONFIG, parameters=LoraReceiverApp.LORA_PARAMETERS)
        
        # Lock
        self.evt_msg_rx = asyncio.Event()
        
        # Tasks
        asyncio.create_task(self.TriggeredLed())
        asyncio.create_task(self.CheckLoRaRx())
        
    async def CheckLoRaRx(self):
        while True:
            if self.lora.received_packet():
                print('Payload: {}'.format(self.lora.read_payload()))
                self.evt_msg_rx.set()   # set the event          
            await asyncio.sleep_ms(0)
            
    async def TriggeredLed(self):
        while True:
            await self.evt_msg_rx.wait() # wait for event
            #light the led
            print('Event')
            self.led.value(1)
            await asyncio.sleep_ms(250)
            self.led.value(0)
            self.evt_msg_rx.clear() # clear the event
            

    def Loop(self):
        evtloop = asyncio.get_event_loop()
        evtloop.run_forever()