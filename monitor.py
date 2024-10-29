import argparse
import ssl
from paho.mqtt import client as mqtt_client

def parse_args():
    parser = argparse.ArgumentParser(description='MQTT Monitor')
    parser.add_argument('--broker', '-b', default='localhost', help='MQTT broker address')
    parser.add_argument('--port', '-p', type=int, default=8883, help='MQTT port')
    parser.add_argument('--cafile', '-ca', default=None, help='CA cert path')
    parser.add_argument('--username', '-u', default=None, help='username')
    parser.add_argument('--password', '-pass', default=None, help='password')
    return parser.parse_args()

def on_connect(client, userdata, flags, rc,properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe('#')  # 订阅所有主题
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

def run():
    args = parse_args()
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    client.tls_set(args.cafile, cert_reqs=ssl.CERT_REQUIRED)
    client.username_pw_set(args.username, args.password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.broker, args.port)
    
    client.loop_start()
    while True:
        user_input = input("Enter a topic to publish or type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break
        message = input("Enter a message: ")
        client.publish(user_input, message)
    client.loop_stop()

if __name__ == '__main__':
    run()
