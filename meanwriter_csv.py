from influxdb import InfluxDBClient
import time
import datetime

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
                "timestamp": epoch
            }
        ]
    return jsonData

client = getConnection(inputHost="localhost", inputPort="8086", inputDatabase="sensors")
# while "true":
current_time = datetime.datetime(2020, 3, 24, 20, 1, 2, 790612)
mean = generateMean(client, epoch=current_time.timestamp()*1000000)
client.write_points(mean, database="preprocessed",time_precision="ms")
# time.sleep(5)
