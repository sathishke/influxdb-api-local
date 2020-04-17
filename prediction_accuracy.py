# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 12:41:38 2020

@author: Sathish
"""
from configparser import ConfigParser, ExtendedInterpolation

import pandas as pd
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from fbprophet.plot import plot_cross_validation_metric
from influxdb import DataFrameClient

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('./config/application.ini')
influxdb_config = config['influxdb']

preprocess_db = DataFrameClient(host=influxdb_config['preprocessed_data_host'],
                                    port=influxdb_config['preprocessed_data_port'],
                                    database=influxdb_config['preprocessed_database'])

def measure_accuracy(input_db = preprocess_db):
    
    print("Starting prediction")
    #get latest 300 points from last 24 hours of data and measure accuracy
    res = input_db.query('select * from Ax where time > now()- 24h order by time desc limit 300')
    measurement = next(iter(res))
    ret = res[measurement]
    df = pd.DataFrame.from_dict(ret)
    df['ds'] =df.index.astype(str).str[:-6]
    df['y'] = df['value']
    print(df)
    
    m = Prophet()
    m.fit(df)
    df_cv = cross_validation(m, period='1 seconds', horizon = '60 seconds')
    print(df_cv)
    df_p = performance_metrics(df_cv)
    df_p.head()
    #plot mean squared error
    #refer https://facebook.github.io/prophet/docs/diagnostics.html
    plot_cross_validation_metric(df_cv, metric='mse')
    
if __name__ == '__main__':
    measure_accuracy(preprocess_db)