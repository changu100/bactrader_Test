from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import argparse
import datetime
import random

import backtrader as bt


from DB.DB import databasepool
import pandas as pd


class SMACross(bt.Strategy):
    param = [ 5 , 20 ]
    def __init__(self):
        sma1 = bt.ind.SMA(period=self.param[0]) # fast moving average 
        sma2 = bt.ind.SMA(period=self.param[1]) # slow moving average 
        self.crossover = bt.ind.CrossOver(sma1, sma2) # crossover signal 
        self.holding = 0

  
    def next(self): 
        if not self.position: # not in the market 
            if self.crossover > 0: # if fast crosses slow to the upside 
                close = self.data.close[0] # 종가 값 
                size = int(self.broker.getcash() / close)  # 최대 구매 가능 개수 
                self.buy(size=size) # 매수 size = 구매 개수 설정 
                
                dt = self.datas[0].datetime.date(0)
                print('%s' % (dt.isoformat()),"buy : ",self.data.close[0])
        elif self.crossover < 0: # in the market & cross to the downside 
            
            dt = self.datas[0].datetime.date(0)
            print('%s' % (dt.isoformat()),"sell : ",self.data.close[0])
            self.close() # 매도
        #print(self.data.close[0])
    
    def notify_order(self, order):
        if order.status not in [order.Completed]:
            return
        ftest = 0
        if order.isbuy():
            action = 'Buy'
            ftest=1
        elif order.issell():
            action = 'Sell'
            ftest=2
        stock_price = self.data.close[0]
        cash = self.broker.getcash()
        value = self.broker.getvalue()
        self.holding += order.size
        """
        if ftest == 1:
            print("buy : ",stock_price)
        if ftest == 2:
            print("sell : ",stock_price)
        """
        print('%s[%d] holding[%d] price[%d] cash[%.2f] value[%.2f]'
              % (action, abs(order.size), self.holding, stock_price, cash, value))



def getDBData(ticker, start, end = None):
        DBClass = databasepool()
        conn = DBClass.getConn()
        if DBClass:
            query = "select stock_date, open_price, high_price, low_price, close_price, volume from daily_stock"
            query += " where \"ticker\" = \'"+ticker+"\' order by stock_date asc;"
            
            df = DBClass.selectDataframe(conn,query)
            df["stock_date"] = pd.to_datetime(df["stock_date"], format='%Y-%m-%d')
            df = df.set_index("stock_date")
            df = df.sort_values(by=['stock_date'], axis=0, ascending=True)

            df.rename(columns={
                "open_price":"Open"	,
                "high_price":"High"	,
                "low_price":"Low",
                "close_price":'Close'	,
                "volume":"Volume"
            },inplace = True)

            res = []
            if end == None or end == '':
                res = df[str(pd.to_datetime(start, format='%Y-%m-%d')) : ]
            else:
                res = df[str(pd.to_datetime(start, format='%Y-%m-%d')) :str(pd.to_datetime(end, format='%Y-%m-%d')) ]

            DBClass.putConn(conn)

            return res
        return "error"


def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(10000000)

    #data0 = bt.feeds.BacktraderCSVData(dataname=args.data0, **dkwargs)
    data0 = bt.feeds.PandasData(dataname = getDBData("005930","20190730",))
    cerebro.adddata(data0, name='005930')

    #data1 = bt.feeds.BacktraderCSVData(dataname=args.data1, **dkwargs)
    data1 = bt.feeds.PandasData(dataname = getDBData("066570","20190730",))
    cerebro.adddata(data1, name='066570')

    #data2 = bt.feeds.BacktraderCSVData(dataname=args.data2, **dkwargs)
    data2 = bt.feeds.PandasData(dataname = getDBData("005380","20190730",))
    cerebro.adddata(data2, name='005380')

    cerebro.addstrategy(SMACross)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    results = cerebro.run()
    #if not args.no_pyfolio:
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    #if args.printout:

    print("********\n"*5)
    print('-- RETURNS')
    print(returns)
    print('-- POSITIONS')
    print(positions)
    print('-- TRANSACTIONS')
    print(transactions)
    print('-- GROSS LEVERAGE')
    print(gross_lev)

    cerebro.plot(style='bar')
    import pyfolio as pf
    
    pf.create_full_tear_sheet(
        returns,
        positions=positions,
        transactions=transactions,
        gross_lev=gross_lev,
        live_start_date='2019-07-30',
        round_trips=True)



def parse_args(args=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for pivot point and cross plotting')

    parser.add_argument('--data0', required=False,
                        default='../../datas/yhoo-1996-2015.txt',
                        help='Data to be read in')

    parser.add_argument('--data1', required=False,
                        default='../../datas/orcl-1995-2014.txt',
                        help='Data to be read in')

    parser.add_argument('--data2', required=False,
                        default='../../datas/nvda-1999-2014.txt',
                        help='Data to be read in')

    parser.add_argument('--fromdate', required=False,
                        default='2005-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False,
                        default='2006-12-31',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--printout', required=False, action='store_true',
                        help=('Print data lines'))

    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=50000,
                        help=('Cash to start with'))

    parser.add_argument('--plot', required=False, action='store_true',
                        help=('Plot the result'))

    parser.add_argument('--plot-style', required=False, action='store',
                        default='bar', choices=['bar', 'candle', 'line'],
                        help=('Plot style'))

    parser.add_argument('--no-pyfolio', required=False, action='store_true',
                        help=('Do not do pyfolio things'))

    import sys
    aargs = args if args is not None else sys.argv[1:]
    return parser.parse_args(aargs)


    

if __name__ == "__main__": 
    data = {'ticker': '005930', 'startTime': '20170101', 'endTime': '', 'strategyCode': '0', 'investPrice': '10000000', 'tradingStrategyCode': '0', 'tradingStrategyDetailSettingCode': '0'}
    runstrat()
