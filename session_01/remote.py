import network
import socket
import uasyncio as asyncio
from machine import Pin

# Configure the LED
led = Pin(2, Pin.OUT)

# Connect to Wi-Fi
async def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('IOTNET_2.4', '10T@ATC_')
    
    while not wlan.isconnected():
        print("Conectando...")
        await asyncio.sleep(1)
    
    print("Conectado con éxito!")
    print("Dirección IP:", wlan.ifconfig()[0])

# Handle HTTP requests
async def handle_request(cl):
    request = cl.recv(1024)
    print("Solicitud recibida:", request)

    response_body = ""

    if b'/encender' in request:
        if led.value() == 1:  # LED already on
            response_body = "<html><body><h1>LED ya estaba encendido</h1></body></html>"
        else:  # LED off, turn on
            led.on()
            response_body = "<html><body><h1>LED encendido</h1></body></html>"
    elif b'/apagar' in request:
        if led.value() == 0:  # LED already off
            response_body = "<html><body><h1>LED no estaba encendido</h1></body></html>"
        else:  # LED on, turn off
            led.off()
            response_body = "<html><body><h1>LED apagado</h1></body></html>"
    else:
        response_body = "<html><body><h1>Comando no reconocido</h1></body></html>"

    # Build the HTTP response
    response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n""" + response_body
    cl.send(response.encode())  # Send the response
    cl.close()  # Close the connection

# Create an HTTP server
async def iniciar_servidor():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]  # Listen on all interfaces on port 80
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("Servidor HTTP escuchando en:", addr)

    while True:
        cl, addr = s.accept()  # Wait for a client to connect
        print("Cliente conectado desde:", addr)
        await handle_request(cl)  # Handle the request asynchronously

# Main function
async def main():
    await conectar_wifi()  # Connect to Wi-Fi
    await iniciar_servidor()  # Start the server

# Run the event loop
asyncio.run(main())
