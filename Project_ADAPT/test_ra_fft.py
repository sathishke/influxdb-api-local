from ra_fft import *
import matplotlib.pyplot as plt


your_query='SELECT value FROM "autogen"."Ax" WHERE time > now() - 10s;'

df=pull_data_from_influx(your_query,database_name="test1",IP_of_influx="127.0.0.1",port=8086)

[xf, yf, yf_scaled, N, peaks]=Short_fft(df, peaks_number=5, fs=1000/70 ) 


# To plot freq spectrum 
plt.scatter(xf[peaks],yf_scaled[peaks])
plt.plot(xf, yf_scaled)
plt.grid()
plt.show()