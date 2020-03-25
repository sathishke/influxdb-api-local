from influxdb import InfluxDBClient
import time

def getConnection(inputHost,inputPort,inputDatabase):
    client = InfluxDBClient(host = inputHost, port = inputPort, database = inputDatabase)
    return client

def writeData():
    print("Writing data")

def generateMean(client):
    query='SELECT mean(Value) FROM "autogen"."Ax" WHERE time > now() - 24h;'
    meanPoints = client.query(query).get_points()
    for meanPoint in meanPoints:
        mean =meanPoint['mean']
        jsonData = [
        {
            "measurement": "mean",
            "tags": {
                "metric": "Ax",
            },
            "fields": {
                "Value": mean
            }
        }
        ]
        return jsonData

client = getConnection(inputHost="localhost", inputPort="8086", inputDatabase="sensors")
while "true":
    # calculate last 24 hours mean of Accelerometer X-Axis
    mean = generateMean(client);
    # write to database
    client.write_points(mean , database="preprocessed")
    # repeat for every 5 sec
    time.sleep(5)
