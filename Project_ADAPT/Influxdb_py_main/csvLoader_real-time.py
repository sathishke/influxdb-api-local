from influxdb import InfluxDBClient
import csv

"""
reads data from csv and stores in influxdb
===========================
fileFormat - delimited by ~
===========================
for every line,
    1st column = measurement_name
    2nd column = machineid and sensorid(tags delimited by ,)
    3rd column = temp and accel(fields delimited by ,)
    4th column = timestamp read from influxdb
    5th column = custom timestamp
"""
client = InfluxDBClient(host='localhost', port='8086', database='preprocessed')

def loadCsvIntoInfluxDb(fileName, influxdbClient=client):
    with open(fileName) as inputFile:
        reader = csv.reader(inputFile, delimiter='~')
        for row in reader:
            measurement = row[0]
            tags = row[1]
            fields = row[2]
            customtimestamp = row[4]
            line_data = measurement + ',' + tags + ' ' + fields + ' ' + customtimestamp
            influxdbClient.write_points(line_data, protocol="line")

loadCsvIntoInfluxDb('sample_data.csv', InfluxDBClient(host='localhost', port='8086', database='test'))
