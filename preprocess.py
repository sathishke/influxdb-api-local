import csvLoader
import time
import csv
from datetime import datetime
from influxdb import InfluxDBClient

def preprocess(inputfileName, outputFileName, start_time):
    """
    read from the inputfile
    preprocess
    write to outputfile
    starting time of process will stored in outputfile
    """
    print("Preprocessing", inputfileName, "started @", datetime.now())
    with open(inputfileName) as inputFile:
        with open(outputFileName, 'w') as outputFile:
            reader = csv.reader(inputFile, delimiter=',')
            isFirstLine = 1
            #need to change if tags/multiple fields are coming in
            for row in reader:
                if isFirstLine==1:
                    measurementName =row[0]
                    tagNames=''
                    fieldNames=row[2]
                    isFirstLine = 0
                else:
                    measurement = row[0]
                    tags = ''
                    fields = row[2]
                    customtimestamp = row[1] if start_time == None else str(start_time)
                    line_data = measurement + '~' + tags + "~" + fieldNames+ "=" + fields + '~' + customtimestamp
                    outputFile.write(line_data + '\n')

preprocessOutputDB = InfluxDBClient(host='localhost', port='8086', database='preprocessed')

def loadAndPreprocess(query, query_interval, rawDatahost="localhost", rawDataport="8086", rawDatabase="test1",\
 influxClientPath=".", inputFilePath = ".", outputFilePath = "./", fileName=None, preprocessOutputDB=preprocessOutputDB):
    """Starting point for preprocess
    """
    start_time = time.time_ns()
    standardFileName = "/" + rawDatahost + "_" + rawDataport + "_" + rawDatabase + "_" + str(start_time)
    if fileName is None:
        fileName = inputFilePath + standardFileName + ".csv"
    inputFileName = fileName
    outputFileName = outputFilePath + standardFileName  + "_out.csv"
    #read data
    csvLoader.influxDBToCsv(inputFileName, query, rawDatahost, rawDataport, rawDatabase, influxClientPath)
    #preprocess the data here
    preprocess(inputFileName, outputFileName, start_time)
    #write data
    csvLoader.CsvToInfluxDB(outputFileName, preprocessOutputDB, time.time_ns())
    print('Waiting.....')
    time.sleep(query_interval)


filePath = "E:/influxdb-api-local/"
csvFileName="collected_data.csv"
query="SELECT * FROM Ax WHERE time > now() - 24h"
rawDatahost="localhost"
rawDataport="8086"
rawDatabase="test1"
influxClientPath="E:\influxdb-1.7.10-1"
#sleep for 10 secs
query_interval=30

while "true":
    loadAndPreprocess(query, query_interval, rawDatahost,rawDataport,rawDatabase,influxClientPath,\
    inputFilePath = "./raw", outputFilePath = "./preprocessed", preprocessOutputDB=preprocessOutputDB)
#preprocess("test.csv", time.time_ns())
