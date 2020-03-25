from influxdb import InfluxDBClient
import time


def getConnection(inputHost, inputPort, inputDatabase):
    client = InfluxDBClient(host=inputHost, port=inputPort, database=inputDatabase)
    return client


def generateMean(client):
    query = 'SELECT mean(Value) FROM "autogen"."Ax" WHERE time > now() - 24h;'
    meanPoints = client.query(query).get_points()
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
                }
            }
        ]
        return jsonData

# every 5 secs, calculate the mean of Ax(Accelerometer - X - Axis) for last 24 hrs and write to preprocessed database
# pre-req :
#   influxdb in localhost @ port 8086, with 2 databases. sensors and preprocessed
#   sensors database to have Accelerometer - X- Axis data in measurement named Ax


client = getConnection(inputHost="localhost", inputPort="8086", inputDatabase="sensors")
while "true":
    # calculate last 24 hours mean of Accelerometer X-Axis
    mean = generateMean(client)
    # write to database
    client.write_points(mean, database="preprocessed")
    # repeat for every 5 sec
    time.sleep(5)
