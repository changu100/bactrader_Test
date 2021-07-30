
import pandas as pd
import pandas_datareader.data as web
import datetime
import backtrader as bt
import numpy as np
%matplotlib inline
import matplotlib.pyplot as plt
import pyfolio as pf
import quantstats
import math


plt.rcParams["figure.figsize"] = (10, 6) # (w, h)

start = '2002-08-02'
end = '2021-03-11'
vti = web.DataReader("VTI", 'yahoo', start, end)['Adj Close'].to_frame("vti_Close")
ief = web.DataReader("IEF", 'yahoo', start, end)['Adj Close'].to_frame("ief_Close")




vti.head()