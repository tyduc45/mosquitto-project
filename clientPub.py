
import random
import time
import argparse
import ssl
import paramiko 
from paho.mqtt import client as mqtt_client


def parse_args():
    parser = argparse.ArgumentParser(description='MQTT publish')
    parser.add_argument('--broker','-b', default='localhost', help='MQTT ip addr')
    parser.add_argument('--port','-p', type=int, default=8883, help='MQTT port')
    parser.add_argument('--topics', '-t', nargs='+', default=['topic1', 'topic2'], help='publish topics')
    parser.add_argument('--subtopics', '-subs', nargs='+', default=['topic1', 'topic2'], help='Subscribed topics')
    parser.add_argument('--cafile', '-ca', default=None, help='CA cert path')
    parser.add_argument('--username', '-u', default=None, help='username')
    parser.add_argument('--password', '-pass', default=None, help='password')
    return parser.parse_args()


client_id = f'python-mqtt-{random.randint(0, 1000)}'
host = "136.186.230.154"
username = "root"
password = "hjhi15w9"
command = "tail -f /var/log/mosquitto/mosquitto.log"

def monitor_mosquitto_log(host, ssh_username, ssh_password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # connect to remote server
        client.connect(host, username=ssh_username, password=ssh_password)
        
        # start logging
        stdin, stdout, stderr = client.exec_command(command)
        
        # monitor on log output
        while True:
            line = stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            # if "Denied PUBLISH" or "Sending PUBLISH" were detected
            if "Denied PUBLISH" in line:
                print("permission denied:", line.strip())
                return False  # return false for sending failed
            elif "Sending PUBLISH" in line:
                return True  # return True for sending success
    finally:
        client.close()


def connect_mqtt(arguments):
    def on_connect(client, userdata, flags, rc,properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe([(topic , 0) for topic in arguments.subtopics]) # subscribe multiple topic
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(client, userdata, msg):
        received_msg = msg.payload.decode()

        if received_msg.endswith(f"{client_id}"): # check if the sender is itself
            return

        print(f"Received `{received_msg}` from `{msg.topic}` topic")

    
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,client_id,clean_session=True)
    client.tls_set(arguments.cafile,cert_reqs=ssl.CERT_REQUIRED)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(arguments.username, arguments.password)
    client.connect(arguments.broker,arguments.port,keepalive=60)

    return client


def publish(client,arguments):
    cnt = 1
    while True:
        time.sleep(1)

        for topic in arguments.topics:
            # test and watch log result
            client.publish(topic,"test")
            log_monitor_result = monitor_mosquitto_log(host,username,password,command)
            
            # if test was passed
            if log_monitor_result:
                msg = f"messages: test, topic:{topic} client_id: {client_id}"
                result = client.publish(topic, msg)
                # result: [0, 1]
                status = result[0]
                if status == 0:
                    print(f"Send `{msg}` to topic `{topic}`")
                else:
                    print(f"Failed to send message to topic {topic}")
            else: # if it wasn't
                print("please switch to the correct user!")
            
        cnt = cnt+1
        if cnt > 5 :
            break
            


def run():
    args = parse_args()
    client = connect_mqtt(args)
    client.loop_start()
    publish(client,args)
    client.loop_stop()

if __name__ == '__main__':
    run()