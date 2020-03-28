import csvLoader
import time
import csv
from datetime import datetime
from influxdb import InfluxDBClient
import configparser

config = configparser.ConfigParser()
config.read('./config/config.ini')
influxdb_config = config['influxdb']
default_config = config['DEFAULT']

def preprocess(inputfileName, outputFileName, start_time=None):
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
                    #measurementName =row[0]
                    #tagNames=''
                    fieldNames=row[2]
                    isFirstLine = 0
                else:
                    measurement = row[0]
                    tags = ''
                    fields = row[2]
                    customtimestamp = row[1] if start_time == None else str(start_time)
                    line_data = measurement + '~' + tags + "~" + fieldNames+ "=" + fields + '~' + customtimestamp
                    outputFile.write(line_data + '\n')

preprocessOutputDB = InfluxDBClient(host=influxdb_config['preprocessed_data_host'],
                                    port=influxdb_config['preprocessed_data_port'],
                                    database=influxdb_config['preprocessed_database'])

def loadAndPreprocess(query, query_interval, rawDatahost="localhost", rawDataport='port', rawDatabase="test1",
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
    preprocess(inputFileName, outputFileName)
    #write data
    csvLoader.CsvToInfluxDB(outputFileName, preprocessOutputDB)
    print('Waiting.....')
    time.sleep(query_interval)

#sleep for 30 secs
query_interval=int(default_config['query_interval'])

while "true":
    loadAndPreprocess(default_config['query'], query_interval, influxdb_config['raw_data_host'],influxdb_config['raw_data_port'],
                      influxdb_config['raw_database'],influxdb_config['client_path'],
                      inputFilePath = "./raw", outputFilePath = "./preprocessed", preprocessOutputDB=preprocessOutputDB)
#preprocess("test.csv", time.time_ns())