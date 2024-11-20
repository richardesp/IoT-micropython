# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/
import ujson
import random

def sub_cb(topic, msg):
  print((topic, msg))

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pass)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

def generate_random_data():
    temperature = round(random.uniform(15.0, 30.0), 2)  # Random temperature between 15.0 and 30.0
    humidity = random.randint(30, 80)  # Random humidity between 30 and 80
    status = random.choice(["OK", "Warning", "Error"])  # Random status choice
    return {
        "temperature": temperature,
        "humidity": humidity,
        "status": status
    }

while True:
    try:
        new_message = client.check_msg()
        if new_message != 'None':
            # Generate new random data
            data = generate_random_data()
            json_data = ujson.dumps(data)
            # Publish the random data
            client.publish(topic_pub, json_data)
        time.sleep(1)
    except OSError as e:
        restart_and_reconnect()
