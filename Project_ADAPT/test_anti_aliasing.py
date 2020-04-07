import numpy as np
from scipy.signal import butter, lfilter, freqz
#import time
from Anti_Aliasing import *
from pull_data_from_influx import *
import matplotlib.pyplot as plt

# # Filter requirements.
# order = 10 # ORDER OF FILTER
# fs = 1000/70       # sample rate, Hz
# cutoff = 3  # desired cutoff frequency of the filter, Hz

# # Get the filter coefficients so we can check its frequency response.
# b, a = butter_lowpass(cutoff, fs, order)

# # Plot the frequency response.
# w, h = freqz(b, a, worN=8000)
# plt.subplot(2, 1, 1)
# plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
# plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
# plt.axvline(cutoff, color='k')
# plt.xlim(0, 0.5*fs)
# plt.title("Lowpass Filter Frequency Response")
# plt.xlabel('Frequency [Hz]')
# plt.grid()

# Demonstrate the use of the filter.
# First make some data to be filtered.
your_query='SELECT value FROM "autogen"."Ax" WHERE time > now() - 10s;'

df=pull_data_from_influx(your_query,database_name="test1",IP_of_influx="127.0.0.1",port=8086)

#T = 10         # seconds
t = df['datetime'].values
# "Noisy" data.  We want to recover the 1.2 Hz signal from this.
y =df['value'].values
#n =len(data)# total number of samples

#window=30
#dataroll=GetShiftingWindows(data, window)[i]
filtered=butter_lowpass_filter(data=y, cutoff=3, fs=1000/70, order=15)
#print(len(filtered))
# plt.subplot(2, 1, 2)
plt.plot(t, y, 'b-', label='data')
plt.plot(t, filtered, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()
plt.show()
