from influxdb import InfluxDBClient
import time
import datetime
from pytz import UTC


def getConnection(inputHost, inputPort, inputDatabase):
    client = InfluxDBClient(host=inputHost, port=inputPort, database=inputDatabase)
    return client

def generateMean(client, epoch):
    query = 'SELECT mean(Value) FROM "autogen"."Ax" WHERE time > now() - 24h;'
    meanPoints = client.query(query).get_points()
    print("Printing:", epoch)
    for meanPoint in meanPoints:
        mean = meanPoint['mean']
        jsonData = [
            {
                "measurement": "mean",
                "tags": {
                    "metric": "Ax",
                },
                "fields": {
                    "Value": mean
                },
                "time": epoch
            }
        ]
    return jsonData

# every 5 secs, calculate the mean of Ax(Accelerometer - X - Axis) for last 24 hrs and write to preprocessed database
# pre-req :
#   influxdb in localhost @ port 8086, with 2 databases. sensors and preprocessed
#   sensors database to have Accelerometer - X- Axis data in measurement named Ax
client = getConnection(inputHost="localhost", inputPort="8086", inputDatabase="sensors")
# while "true":
# calculate last 24 hours mean of Accelerometer X-Axis
current_time = datetime.datetime(2020, 3, 24, 20, 1, 2, 790612)
EPOCH = UTC.localize(datetime.datetime.utcfromtimestamp(0))

ns = (current_time - EPOCH).total_seconds() * 1e9
print(ns)

mean = generateMean(client, epoch=current_time.timestamp())
# write to database
client.write_points(mean, database="preprocessed", time_precision="s")
# repeat for every 5 sec
# time.sleep(5)
