"""
/*
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Created on Thu Mar 26 15:19:27 2020
 */
"""

# Short_fft - to find peaks in freq domain
#Inputs:
#1) df - contains timestamps and sensor values
#2) fs - Sensor Node app sends a data point every 70ms. So fs=1000/70. Setting as default for the time being.
#Outputs:
#1) xf (Freq vector in posetive side)
#2) yf (fft of y)
#3) yf_scaled (yf Scaled, ready to be outputed.)
#4) peaks_number - no. of desired peaks
#5) peaks- Index of Frequencies with highest peaks
#NOTE Frequency at which peaks occur: xf[peaks]
#NOTE Amplitude of peaks: yf_scaled[peaks]

#Imports necessary for Short_fft_to_work
import matplotlib.pyplot as plt
import numpy as np
from pull_data_from_influx import pull_data_from_influx

#your_query='SELECT value FROM "autogen"."Ax" WHERE time > now() - 10s;'

#df=pull_data_from_influx(your_query,database_name="test1",IP_of_influx="127.0.0.1",port=8086)

def return_peaks(peaks_number, a): 
    return np.argsort(a)[-peaks_number:]

def Short_fft(df, peaks_number, fs=1000/70):
    
    y=df['value'].values
    N=len(y)
    T=1/fs
    y=y*np.hamming(N)
    yf = np.fft.fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    yf[0]=0 #Setting 0 Hz peak to zero as we are not interested in the 0hz Peak.
    yf_scaled=2.0/N * np.abs(yf[0:N//2])
    peaks=return_peaks(peaks_number,a=yf_scaled)
    return [xf, yf, yf_scaled, N, peaks]

# How to use this function
# [xf, yf, yf_scaled, N, peaks]=Short_fft(df, peaks_number=5, fs=1000/70 ) 


# To plot freq spectrum 
# plt.scatter(xf[peaks],yf_scaled[peaks])
# plt.plot(xf, yf_scaled)
# plt.grid()
# plt.show()
