"""
/* Proprietary and confidential
 * Written by AJ, Created on Sun Mar 22 15:43:43 2020
 */
"""
#Imports
# Note: Need a way to remove the in function imports to speed up the fuction runtime
import influxdb
import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# Input Args:
# your_query: Use this arg to pass the query to Influxdb
#       Example: q='SELECT Value FROM "autogen"."Ax" WHERE time > now() - 5m;'
#
# database_name: Name of database
# IP_of_influx: IP address of the influxdb, defaults to localhost
# port: Port of influxdb, defaults to 8086
#
# Output:
# df: the pandas dataframe of needed measurement with date, Time and datetime.
# =============================================================================

def pull_data_from_influx(your_query,database_name,IP_of_influx="127.0.0.1",port=8086):
    #Initiating the client
    client = influxdb.DataFrameClient(IP_of_influx, port, database=database_name)
    #query returns data to dfs_dict
    dfs_dict = client.query(your_query)
    #Finding out the measurement name
    measurement = next(iter(dfs_dict))
    #Extracting the measurement data of use
    ret = dfs_dict[measurement]
    #Storing the measurement data as a pandas dataframe
    df = pd.DataFrame.from_dict(ret)
    #Resetting index
    df = df.reset_index()
    #Renaming index as datetime
    df.rename( columns={'index':'datetime'}, inplace=True )
    #print(df)
    #Parsing datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    #Parsing time from datetime
    df['Time'] = df['datetime'].dt.time
    #parsing Time from datetime
    df['date'] = df['datetime'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    #setting index as date
    df = df.set_index(['date'])

    return df

# =============================================================================
# Use the code below to run the function
your_query='SELECT value FROM "autogen"."Ax" WHERE time > now() - 24h;'
df=pull_data_from_influx(your_query,database_name="sensors",IP_of_influx="127.0.0.1",port=8086)
print(df)
df.plot(x ='datetime', y='value', kind = 'line')
plt.show()
# =============================================================================
