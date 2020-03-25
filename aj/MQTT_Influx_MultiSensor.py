#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 16:01:12 2020

@author: Anil Jaeni
"""

#import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import datetime
import time

#def data_parse_to_Influx()

def Insert_data_in_Influxdb(msg_payload,measurement_name):
    value_acc=float(str(msg_payload)[2:-1])
    json_body = [
    {
        "measurement": measurement_name,
        #"tags":{},
        "tags": {
            "host": "aquarium",
        },
        #"time": str(current_time),
        "fields": {
            "Value": value_acc
        }
    }
    ]
    influx_client.write_points(json_body)
    print(value_acc )
   
   

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        #print("Connection successful, Returned code=",rc)
    elif rc==1:
        print("Connection refused – incorrect protocol version, Returned code=",rc)
    elif rc==2:
        print("Connection refused – invalid client identifier, Returned code=",rc)
    elif rc==3:
        print("Connection refused – server unavailable, Returned code=",rc)
    elif rc==4:
        print("Connection refused – bad username or password, Returned code=",rc)
    elif rc==5:
        print("Connection refused – not authorised, Returned code=",rc)
    else:
        print("Currently unused, Returned code=",rc)
   

# The callback for when a PUBLISH message is received from the server.



def on_message(mqttc, obj, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    #current_time = datetime.datetime.now().isoformat()
    if msg.topic == "sensornode/livestream/Accelerometer/x":
       
        Insert_data_in_Influxdb(msg.payload,"Ax")
       
    elif msg.topic == "sensornode/livestream/Accelerometer/y":
       
        Insert_data_in_Influxdb(msg.payload,"Ay")

    elif msg.topic == "sensornode/livestream/Accelerometer/z":

        Insert_data_in_Influxdb(msg.payload,"Az")

    elif msg.topic == "sensornode/livestream/Gyroscope/x":

        Insert_data_in_Influxdb(msg.payload,"Gx")
       
    elif msg.topic == "sensornode/livestream/Gyroscope/y":

        Insert_data_in_Influxdb(msg.payload,"Gy")

    elif msg.topic == "sensornode/livestream/Gyroscope/z":
        Insert_data_in_Influxdb(msg.payload,"Gz")
    else:
        print("Not send to influxdb")

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
influx_client = InfluxDBClient('localhost', 8086, database='sensors')

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
#mqttc.on_log = on_log
mqttc.connect("192.168.1.17", 1883)
mqttc.subscribe("sensornode/livestream/+/+", qos=0)

mqttc.loop_forever()
