import csvLoader
import time
import csv
from influxdb import InfluxDBClient
import configparser
import logging
from pytz import utc


from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logger_config

config = configparser.ConfigParser()
config.read('./config/application.ini')
influxdb_config = config['influxdb']
default_config = config['common']
queries_config = config['queries']

logger = logging.getLogger(__name__)

def preprocess(inputfileName, outputFileName, start_time=None):
    """
    read from the inputfile
    preprocess
    write to outputfile
    starting time of process will stored in outputfile
    """
    ts = time.time()
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
    logger.info("Preprocessed %s in %s seconds", inputfileName, time.time() - ts)
                

preprocessOutputDB = InfluxDBClient(host=influxdb_config['preprocessed_data_host'],
                                    port=influxdb_config['preprocessed_data_port'],
                                    database=influxdb_config['preprocessed_database'])

def loadAndPreprocess(query, rawDatahost="localhost", rawDataport='port', rawDatabase="test1",
                      influxClientPath=".", inputFilePath = ".", outputFilePath = "./", fileName=None, preprocessOutputDB=preprocessOutputDB):
    """Starting point for preprocess
    """
    ts = time.time()
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
    logger.info("Loaded, preprocessed & pushed %s in %s seconds", inputFileName, time.time() - ts)


if __name__ == '__main__':
    logger_config.setup_logging()    
    jobstores = {
        'default': MemoryJobStore()
    }
    executors = {
        'default': ThreadPoolExecutor(20)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 1
    }
    logger.info("Starting preprocessor")
    scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
    for query_key in queries_config:
        kwArgs = {"query": queries_config[query_key], "rawDatahost" : influxdb_config['raw_data_host'], "rawDataport" : influxdb_config['raw_data_port'],
              "rawDatabase" : influxdb_config['raw_database'], "influxClientPath" : influxdb_config['client_path'],
              "inputFilePath" :default_config['raw_file_path'], "outputFilePath" : default_config['preprocessed_file_path'],
              "preprocessOutputDB" : preprocessOutputDB}
        logger.debug(kwArgs)
        logger.info("Adding job to preprocess %s", query_key)
        scheduler.add_job(loadAndPreprocess, 'interval', name=query_key, kwargs=kwArgs,seconds=int(default_config['query_interval']))
    try:
        scheduler.start()
    finally:
        scheduler.shutdown()
    #loadAndPreprocess(default_config['query'], influxdb_config['raw_data_host'],influxdb_config['raw_data_port'],
    #                  influxdb_config['raw_database'],influxdb_config['client_path'],
    #                  inputFilePath = "./raw", outputFilePath = "./preprocessed", preprocessOutputDB=preprocessOutputDB)
    #preprocess("test.csv", time.time_ns())