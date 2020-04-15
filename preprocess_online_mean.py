from influxdb import InfluxDBClient
from configparser import ConfigParser, ExtendedInterpolation
import logging
from pytz import utc

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logger_config

#config = configparser.ConfigParser()
config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('./config/application.ini')
influxdb_config = config['influxdb']
default_config = config['common']
queries_config = config['queries_mean']
online_mean_config = config['online_mean_config']


logger = logging.getLogger(__name__)

preprocessOutputDB = InfluxDBClient(host=influxdb_config['preprocessed_data_host'],
                                    port=influxdb_config['preprocessed_data_port'],
                                    database=influxdb_config['preprocessed_database'])
rawDataDB = InfluxDBClient(host=influxdb_config['raw_data_host'], 
                           port=influxdb_config['raw_data_port'], 
                           database=influxdb_config['raw_database'])

forecast_db = InfluxDBClient(host=influxdb_config['forecast_db_host'],
                                    port=influxdb_config['forecast_db_port'],
                                    database=influxdb_config['forecast_db'])

def loadAndPreprocess(query, rawDataDB=rawDataDB, preprocessOutputDB=preprocessOutputDB):
    """Starting point for preprocess
    """
    res = rawDataDB.query(query)
    meanPoints = res.get_points()
    for meanPoint in meanPoints:
        if(meanPoint['count'] >= int(online_mean_config['having'])):
            meanValue = meanPoint['mean']
            mean = [
            {
                "measurement": res.keys()[0][0],
                "fields": {
                    "value": meanValue
                },
                "time": meanPoint['time']
            }
            ]
            #just for viewing in console
            if(res.keys()[0][0] == 'Ax'):
                print(mean)
            preprocessOutputDB.write_points(mean)
            forecast_db.write_points(mean)
        # else:
        #     forecast.forecast(res.keys()[0][0])

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
        kwArgs = {"query": queries_config[query_key], "rawDataDB" : rawDataDB, "preprocessOutputDB" : preprocessOutputDB}
        logger.debug(kwArgs)
        logger.info("Adding job to preprocess %s", query_key)
        scheduler.add_job(loadAndPreprocess, 'interval', name=query_key, kwargs=kwArgs,seconds=int(default_config['query_mean_interval']))
    try:
        scheduler.start()
    finally:
        scheduler.shutdown()