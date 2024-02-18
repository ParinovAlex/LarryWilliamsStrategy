from pandas_datareader import data as pdr
import finplot as fplt
import yfinance as yf
from LarryWilliamsStrategy import Strategy
from order import Reporting
yf.pdr_override() # <== that's all it takes :-)
############################################################################################
# Tickers:
# SP500 -> ^GSPC
# Dow30 -> ^DJI
# BCT   -> BTC-USD
              
def StrategyRunner(_interval, barsInRunRange, coeficientRange, stopRange, yearRange, reporting):
    profit = 0
    maxprofitperYear = 0
    maxlist = []
    maxlistExtended = []
    for bars in barsInRunRange:
            for coef in coeficientRange:
                    for stop in stopRange:
                            for year in yearRange:
                                    datestart = "{}-01-01".format(year)
                                    dateend = "{}-12-31".format(year) 
                                    data = pdr.get_data_yahoo("BTC-USD", start=datestart, end=dateend, interval=_interval, progress=False)
                                    profit = Strategy(data, bars, round(coef/10,1),stop*10, range(0,7),range(0,7), reporting)
                                    #print("Date range: {} - {}\tcoef: {}\tBars in run: {}\tstop: {}\t -> Profit: {}".format(datestart, dateend, round(coef/10,1), bars, stop*10,profit))
                                    maxprofitperYear= maxprofitperYear + profit
                            maxlistExtended.append("Year: {}\tBars in run: {}\tCoef: {}\tStop: {}\t -> Profit: {}".format(year, bars,round(coef/10,1),stop*10, maxprofitperYear))
                            maxlist.append(maxprofitperYear)
                            maxprofitperYear=0
    if reporting.ShortPerYear == True:
            if len(maxlist) > 0:
                for i in maxlist:
                        print(i)

    if reporting.ShortPerYearWithParameters == True:
           if len(maxlistExtended) > 0:
                for i in maxlistExtended:
                        print(i)
    if reporting.PrintDataGraph == True:        
        fplt.candlestick_ochl(data[['Open','Adj Close','High','Low']])
        fplt.show()