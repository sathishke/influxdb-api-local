from influxdb import InfluxDBClient
import csv
import logging
import subprocess
from time import time

from apscheduler.schedulers.blocking import BlockingScheduler
import logger_config


logger = logging.getLogger(__name__)

default_target_client = InfluxDBClient(host='localhost', port='8086', database='preprocessed')

def CsvToInfluxDB(fileName, influxdbClient=default_target_client, customInputTime=None):
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
    ts = time()

    with open(fileName) as inputFile:
        reader = csv.reader(inputFile, delimiter='~')
        for row in reader:
            measurement = row[0]
            tags = row[1]
            fields = row[2]
            customtimestamp = row[3] if customInputTime == None else str(customInputTime)
            if tags == '':
                line_data = measurement  + ' ' + fields + ' ' + customtimestamp
            else:
                line_data = measurement + ',' + tags + ' ' + fields + ' ' + customtimestamp
            #print(line_data)
            influxdbClient.write_points(line_data, protocol="line",batch_size=100)
    logger.info("Pushed data from %s into %s in %s seconds", fileName, influxdbClient._baseurl, time() - ts)

#influx -database test1 -host localhost -execute SELECT * FROM Ax WHERE time > now() - 24h -format csv > E:/influxdb-api-local/sample_extract.csv
def influxDBToCsv(fileName, query, host="localhost", port="8086", database="test1", influxClientPath="."):
    """Get data from influxdb to csvLoade
    Executes above command in terminal, make sure you have influx client installed
    """
    ts = time()
    with open(fileName, "w") as file:
        subprocess.run([influxClientPath + "/influx", "-database", database, "-host", host, "-port",\
        port, "-execute", query, "-format", "csv"], stdout=file)
    logger.info("Loaded data from influxdb http(s)://%s:%s into %s in %s seconds",host, port, fileName, time() - ts)
    
if __name__ == '__main__':
    logger_config.setup_logging()    
    #filename='myapp.log'
    #pull data from influxdb and store in csv
    #influxDBToCsv("../raw/test.csv", query="SELECT * FROM Ax WHERE time > now() - 24h", influxClientPath="/Users/aj_heartnett/PycharmProjects/Influxdb_py_main/influxdb-1.7.10-1/usr/bin")
    #influxDBToCsv("./raw/test.csv", query="SELECT * FROM Ax WHERE time > now() - 24h", influxClientPath="E:\influxdb-1.7.10-1")
    scheduler = BlockingScheduler()
    kwArgs = {"fileName": "./raw/test.csv", "query": "SELECT * FROM Ax WHERE time > now() - 24h", "influxClientPath": "E:\influxdb-1.7.10-1"}
    logger.debug(kwArgs)
    scheduler.add_job(influxDBToCsv, 'interval', kwargs=kwArgs,seconds=5)
    try:
        scheduler.start()
    finally:
        scheduler.shutdown()
    #pull data from csv and store in influxdb
    #CsvToInfluxDB('sample_data.csv', InfluxDBClient(host='localhost', port='8086', database='preprocessed'), time.time_ns())
    #CsvToInfluxDB('sample_data_test1.csv', InfluxDBClient(host='localhost', port='8086', database='preprocessed'), time.time_ns())
