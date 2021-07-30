
%matplotlib inline
#  #추가 설치
import pandas as pd
import pandas_datareader.data as web # 추가설치
import datetime
import backtrader as bt
import numpy as np
import matplotlib.pyplot as plt
import pyfolio as pf
import quantstats
import math


plt.rcParams["figure.figsize"] = (10, 6) # (w, h)

start = '2002-08-02'
end = '2021-03-11'
vti = web.DataReader("VTI", 'yahoo', start, end)['Adj Close'].to_frame("vti_Close")
ief = web.DataReader("IEF", 'yahoo', start, end)['Adj Close'].to_frame("ief_Close")




print("############1#############")
print(vti.head())
print("############2#############")
print(ief.head())



vti_return = vti.pct_change(periods=1)
ief_return = ief.pct_change(periods=1)
df_return = pd.concat([vti_return, ief_return], axis=1)

print("############3#############")
print(df_return.head())


df_return['6040_return'] = df_return['vti_Close']*0.6 + df_return['ief_Close']*0.4

print("############4#############")
print(df_return.head())

print("############5#############")
quantstats.reports.plots(df_return['6040_return'], mode='basic')

print("############6#############")
quantstats.reports.metrics(df_return['6040_return'], mode='full')





vti = vti.rename({'vti_Close':'Close'}, axis='columns')
ief = ief.rename({'ief_Close':'Close'}, axis='columns')

for column in ['Open', 'High', "Low"]:
    vti[column] = vti["Close"]
    ief[column] = ief["Close"]

print("############7#############")
print(vti.head())


############################################################

class AssetAllocation_6040(bt.Strategy):
    params = (
        ('equity',0.6),
    )
    def __init__(self):
        self.VTI = self.datas[0]
        self.IEF = self.datas[1]
        self.counter = 0
        
    def next(self):
        if  self.counter % 20 == 0:
            self.order_target_percent(self.VTI, target=self.params.equity)
            self.order_target_percent(self.IEF, target=(1 - self.params.equity))
        self.counter += 1

cerebro = bt.Cerebro()

cerebro.broker.setcash(1000000)

VTI = bt.feeds.PandasData(dataname = vti)
IEF = bt.feeds.PandasData(dataname = ief)

cerebro.adddata(VTI)
cerebro.adddata(IEF)

cerebro.addstrategy(AssetAllocation_6040)

cerebro.addanalyzer(bt.analyzers.PyFolio, _name = 'PyFolio')

results = cerebro.run()
strat = results[0]

portfolio_stats = strat.analyzers.getbyname('PyFolio')
returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
returns.index = returns.index.tz_convert(None)

#quantstats.reports.html(returns, output = 'Report_AssetAllocation_6040.html', title='AssetAllocation_6040')

quantstats.reports.plots(returns, mode='basic')

quantstats.reports.metrics(df_return, mode='full')

"""
MonthlyReturn = pd.read_excel('MonthlyAssetClassReturn.xlsx')


print(MonthlyReturn.head())

MonthlyReturn = MonthlyReturn.set_index('Data Index')

print(MonthlyReturn.head())


Monthly_6040 = MonthlyReturn.loc[:, ['S&P 500 Total return', 'US 10 YR']]
print(Monthly_6040.head())


Monthly_6040['Monthly_6040'] = Monthly_6040['S&P 500 Total return'] * 0.6 + Monthly_6040['US 10 YR'] * 0.4
print(Monthly_6040.head())


quantstats.stats.sharpe(Monthly_6040['Monthly_6040'])/math.sqrt(252/12)



quantstats.reports.plots(Monthly_6040['Monthly_6040'], mode='basic')


quantstats.reports.metrics(Monthly_6040['Monthly_6040'], mode='full')
"""