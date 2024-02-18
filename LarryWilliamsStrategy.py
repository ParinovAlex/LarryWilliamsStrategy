import matplotlib.pyplot as plt
from datetime import datetime
import datetime
from order import *

def GSV(type, data, index):
    ressell = 0
    resbuy = 0
    ressell = data['Open'][index - 4] - data['Low'][index - 4]
    ressell = ressell + data['Open'][index - 3] - data['Low'][index - 3]
    ressell = ressell + data['Open'][index - 2] - data['Low'][index - 2]
    ressell = ressell + data['Open'][index - 1] - data['Low'][index - 1]
    ressell = round( ressell / 4,2)

    resbuy = data['High'][index - 4] - data['Open'][index - 4]
    resbuy = resbuy + data['High'][index - 3] - data['Open'][index - 3]
    resbuy = resbuy + data['High'][index - 2] - data['Open'][index - 2]
    resbuy = resbuy + data['High'][index - 1] - data['Open'][index - 1]
    resbuy = round(resbuy / 4,2)
    if type == "buy":
           return resbuy
    else: 
           return ressell

def Strategy(data, days, coef, stop, buyweekfilter, sellweekfilter, reporting):
    mainBook = OrderBook()

    for index in range(len(data)):
        # Do we have active orders?
        currentDate = data.index[index].strftime('%Y-%m-%d %H:%M:%S')
        date_obj = datetime.datetime.strptime(currentDate, '%Y-%m-%d %H:%M:%S')
        weekday = date_obj.weekday()
        
        if index < 4:
                continue
        if mainBook.IsActiveOrders() == True:
            # check if order profitable
            for order in mainBook.orderList:
                if order.status != "closed":
                    # check for stop out
                    if order.IsStoppedOut(data['Open'][index]) == True:
                        order.CloseAsStoppedOut()
                        continue

                    # close after max bars run criteria
                    if order.barsInRun >= days:
                        if order.IsStoppedOut(data['Open'][index]) == True:
                            order.CloseAsStoppedOut()
                        else:
                            order.Close(data['Open'][index ])
                        order.id = index
                        continue
                    else:
                        order.barsInRun += 1
                    
                    #Check for protection stop

                    
            continue
        
        #If long setup:                
        
        if data['Low'][index-1] < data['Low'][index - 2] and data['Low'][index-1] < data['Low'][index - 3] and data['Low'][index-1] < data['Low'][index - 4] and data['Low'][index-1] < data['Low'][index - 5]:
                
                if data['High'][index] > data['Open'][index ] + coef * GSV("buy",data, index):     
                    if weekday in buyweekfilter:
                        mainBook.orderList.append(Order(len(mainBook.orderList), currentDate,"buy",round(data['Open'][index ],2) + coef * GSV("buy",data, index),stop,0))      
        #If short setup:                
        
        if data['High'][index-1] > data['High'][index - 2] and data['High'][index-1] > data['High'][index - 3] and data['High'][index-1] > data['High'][index - 4] and data['High'][index-1] > data['High'][index - 5]:
                
                if data['Low'][index] < data['Open'][index] - coef * GSV("sell",data, index):      
                    if weekday in sellweekfilter:
                        mainBook.orderList.append(Order(len(mainBook.orderList), currentDate,"sell",round(data['Open'][index ],2) - coef * GSV("sell",data, index),stop,0))                    
                            
    mainBook.OrdersReport(reporting.DetailsReportPerYear,reporting.OrdersDetailsReportPerYear,reporting.OrdersDetailsReportPerYearToFile)
    
    if reporting.AccumulationCurvePerYear == True:  
        # Data for plotting
        y = mainBook.AccumulatedCurve()
        x = range(len(y))
        
        plt.plot(x, y, color="red")
        plt.show()
    return mainBook.Profit()