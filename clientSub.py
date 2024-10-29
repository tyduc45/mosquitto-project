import random
import time
import argparse
import ssl
from paho.mqtt import client as mqtt_client


def parse_args():
    parser = argparse.ArgumentParser(description='MQTT publish')
    parser.add_argument('--broker', '-b', default='localhost', help='MQTT ip addr')
    parser.add_argument('--port', '-p', type=int, default=8883, help='MQTT port')
    parser.add_argument('--topics', '-subs', nargs='+', default=['topic1', 'topic2'], help='Subscribed topics')
    parser.add_argument('--cafile', '-ca', default=None, help='CA cert path')
    parser.add_argument('--username', '-u', default=None, help='username')
    parser.add_argument('--password', '-pass', default=None, help='password')
    return parser.parse_args()

client_id = f'python-mqtt-{random.randint(0, 1000)}'
client_id = f'python-mqtt-{random.randint(0, 1000)}'
host = "136.186.230.154"
username = "root"
password = "hjhi15w9"
command = "tail -f /var/log/mosquitto/mosquitto.log"


def connect_mqtt(arguments) -> mqtt_client:
    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {reason_code}")

 
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,client_id=client_id, clean_session=False)

    # set TLS connection 
    client.tls_set(arguments.cafile,cert_reqs=ssl.CERT_REQUIRED)

    # setup username and password
    client.username_pw_set(arguments.username,arguments.password)
    
    # setup on_connect callback
    client.on_connect = on_connect

    # connect to MQTT Broker
    client.connect(arguments.broker, arguments.port)


    return client

def subscribe(client: mqtt_client, arguments):
    def on_message(client, userdata, msg):
        received_msg = msg.payload.decode()
        if received_msg.endswith(f"{client_id}"): # check if the sender is itself
            return
        
        print(f"Received {msg.payload.decode()} from {msg.topic} topic")
        back_msg = f'acknowledged, client_id: {client_id}'
        client.publish(msg.topic,back_msg)
        print("sending "+ back_msg +" back")

    client.subscribe([(topic, 0) for topic in arguments.topics])# subscribe multiple topic
    client.on_message = on_message

def run():
    args = parse_args()
    client = connect_mqtt(args)
    subscribe(client, args)
    client.loop_forever()

if __name__ == '__main__':
    run()
