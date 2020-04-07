##!/usr/bin/env python3
## -*- coding: utf-8 -*-
#"""
#Created on Mon Mar 30 15:59:31 2020
#
#@author: aj_heartnett
#"""
#
#import pandas as pd
#import csv
#import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib import pyplot as plt
#import plotly.express as px
#

#import scipy.io
#import numpy as np
#import matplotlib.pyplot as plt
#

# We convert matlab file to csv
#data = scipy.io.loadmat("I-A-1.mat")
#
#for i in data:
#    if '__' not in i and 'readme' not in i:
#        np.savetxt(("Converted_file_IA1.csv"),data[i],delimiter=',')
#        
#plt.show()
#


import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from scipy import stats
#%matplotlib inline
import matplotlib.font_manager
from datetime import datetime

# Import models
from pyod.models.abod import ABOD
from pyod.models.cblof import CBLOF
from pyod.models.feature_bagging import FeatureBagging
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF

from sklearn.preprocessing import MinMaxScaler


# Reading the data
df = pd.read_csv("Acceleration_X-Dir.csv")
print(df.shape)
print(df.info())

df.describe()

print(df)

#utc = datetime.utcnow()
#utc = datetime.strptime('3/25/2020 8:31:12.602000000 PM', '%m/%d/%Y %I:%M:%S.%f %p')

#Let's Separate the Day and Month Values to see if there is correlation
#between Day of week/month with absence 
print(type(df['date'][0]))
df['date']= pd.to_datetime(df['date'], format='%m/%d/%Y %I:%M:%S.%f %p')

print(df['date']) 

print(type(df['date'][0]))

##Extracting the Month Value 
#print(df['date'][0].month)
#
#list_months=[] 
#
#print(list_months)
#
#print(df.shape)

#for i in range(df.shape[0]): 
#    list_months.append(df['date'][i].month)
#    print(list_months)
#    print(len(list_months)) 
#
##Let's Create a Month Value Column for df 
#df['Month Value']= list_months
#print(df.head())
#
##Now let's extract the day of the week from date 
#df['date'][699].weekday()
#
#def date_to_weekday(date_value): 
#    return date_value.weekday()
#
#df['Day of the Week']= df['date'].apply(date_to_weekday)
#print(df.head())
#df= df.drop(['date'], axis=1)
#print(df.columns.values)

# df.plot.scatter('date','value')

df.plot.scatter(df['date'], df['value'])

# Note: If you don’t want the visualization, 
# you can use the same scale to predict whether a point is an outlier or not.


scaler = MinMaxScaler(feature_range=(0, 1))
df[['date','value']] = scaler.fit_transform(df[['date','value']])
df[['date','value']].head()


# Store these values in the NumPy array for using in our models later:

X1 = df['date'].values.reshape(-1,1)
X2 = df['value'].values.reshape(-1,1)

X = np.concatenate((X1,X2),axis=1)

# Again, we will create a dictionary. 
# But this time, we will add some more models to it and see how each model predicts outliers.

# You can set the value of the outlier fraction according to your problem and your understanding of the data. 
# In our example, I want to detect 5% observations that are not similar to the rest of the data. 
# So, I’m going to set the value of outlier fraction as 0.05.

random_state = np.random.RandomState(42)
outliers_fraction = 0.05
# Define seven outlier detection tools to be compared
classifiers = {
        'Angle-based Outlier Detector (ABOD)': ABOD(contamination=outliers_fraction),
        'Cluster-based Local Outlier Factor (CBLOF)':CBLOF(contamination=outliers_fraction,check_estimator=False, random_state=random_state),
        'Feature Bagging':FeatureBagging(LOF(n_neighbors=35),contamination=outliers_fraction,check_estimator=False,random_state=random_state),
        'Histogram-base Outlier Detection (HBOS)': HBOS(contamination=outliers_fraction),
        'Isolation Forest': IForest(contamination=outliers_fraction,random_state=random_state),
        'K Nearest Neighbors (KNN)': KNN(contamination=outliers_fraction),
        'Average KNN': KNN(method='mean',contamination=outliers_fraction)
}

# Now, we will fit the data to each model one by one and see how differently each model predicts the outliers.


xx , yy = np.meshgrid(np.linspace(0,1 , 200), np.linspace(0, 1, 200))

for i, (clf_name, clf) in enumerate(classifiers.items()):
    clf.fit(X)
    # predict raw anomaly score
    scores_pred = clf.decision_function(X) * -1
        
    # prediction of a datapoint category outlier or inlier
    y_pred = clf.predict(X)
    n_inliers = len(y_pred) - np.count_nonzero(y_pred)
    n_outliers = np.count_nonzero(y_pred == 1)
    plt.figure(figsize=(10, 10))
    
    # copy of dataframe
    dfx = df
    dfx['outlier'] = y_pred.tolist()
    
    # IX1 - inlier feature 1,  IX2 - inlier feature 2
    IX1 =  np.array(dfx['date'][dfx['outlier'] == 0]).reshape(-1,1)
    IX2 =  np.array(dfx['value'][dfx['outlier'] == 0]).reshape(-1,1)
    
    # OX1 - outlier feature 1, OX2 - outlier feature 2
    OX1 =  dfx['date'][dfx['outlier'] == 1].values.reshape(-1,1)
    OX2 =  dfx['value'][dfx['outlier'] == 1].values.reshape(-1,1)
         
    print('OUTLIERS : ',n_outliers,'INLIERS : ',n_inliers, clf_name)
        
    # threshold value to consider a datapoint inlier or outlier
    threshold = stats.scoreatpercentile(scores_pred,100 * outliers_fraction)
        
    # decision function calculates the raw anomaly score for every point
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()]) * -1
    Z = Z.reshape(xx.shape)
          
    # fill blue map colormap from minimum anomaly score to threshold value
    plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), threshold, 7),cmap=plt.cm.Blues_r)
        
    # draw red contour line where anomaly score is equal to thresold
    a = plt.contour(xx, yy, Z, levels=[threshold],linewidths=2, colors='red')
        
    # fill orange contour lines where range of anomaly score is from threshold to maximum anomaly score
    plt.contourf(xx, yy, Z, levels=[threshold, Z.max()],colors='orange')
        
    b = plt.scatter(IX1,IX2, c='white',s=20, edgecolor='k')
    
    c = plt.scatter(OX1,OX2, c='black',s=20, edgecolor='k')
       
    plt.axis('tight')  
    
    # loc=2 is used for the top left corner 
    plt.legend(
        [a.collections[0], b,c],
        ['learned decision function', 'inliers','outliers'],
        prop=matplotlib.font_manager.FontProperties(size=20),
        loc=2)
      
    plt.xlim((0, 1))
    plt.ylim((0, 1))
    plt.title(clf_name)
    plt.show()
