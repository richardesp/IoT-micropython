"""
fernando.leon@uco.es
University of Córdoba, Spain
2021
"""
import uasyncio as asyncio
from app import LoraReceiverApp

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    set_global_exception() 
    app = LoraReceiverApp()   # Constructor de la App, crea las sub tareas
    await app.Loop()  
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()