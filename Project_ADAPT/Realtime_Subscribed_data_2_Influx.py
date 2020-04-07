"""
/* 
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Created on Wed Mar 11 16:01:12 2020
 */
"""

#Imports
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import pandas as pd 
#Import list of Sensor topic and Measurement names
Sensor_Topic_and_Measurement_names=pd.read_csv('Sensor_topic_and_Measurement_names.csv', sep=',')

# Function to insert realtime data into influxdb without custom time
def Write_Realtime_data_2_Influxdb(msg_payload,measurement_name):
    value_acc=float(str(msg_payload)[2:-1])
    json_body = [
    {
        "measurement": measurement_name,
        #"tags":{},
        #"tags": {
            #"host": "aquarium",
        #},
        #"time": str(current_time),
        "fields": {
            "value": value_acc
        }
    }
    ]
    influx_client.write_points(json_body)
    print(value_acc ) #Uncomment to see sensor data in console.
    
    
    
############################################ Helpers ########################################
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
    Topic_name=msg.topic
    A=Sensor_Topic_and_Measurement_names[Sensor_Topic_and_Measurement_names.values[:,2] == Topic_name]
    #print(bool(A.values[:,3]))
    if str(bool(A.values[:,3]))=="True":
        measurement_name = str(A.values[:,3])[2:-2] 
        Write_Realtime_data_2_Influxdb(msg.payload,measurement_name)
    else:
        pass

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
global CONNACK_count
CONNACK_count=0

def on_log(mqttc, obj, level, string):
    
#    CONNACK_count=0
    
    if string == "Received CONNACK (0, 0)":
        CONNACK_count=CONNACK_count+1
        print(CONNACK_count)
        if CONNACK_count>1:
            lets_connect()
            
    elif string == "Received PINGRESP":
        
        lets_connect()
            
    
    print(string)

############################################ Helpers ends ####################################

# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
def lets_connect():
    
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    # Uncomment to enable debug messages
    mqttc.on_log = on_log
    mqttc.connect("192.168.1.8", 1883)
    #Subscribing to all topics
    mqttc.subscribe("#", qos=2)
    
    mqttc.loop_forever()

influx_client = InfluxDBClient('localhost', 8086, database='test1')
lets_connect()