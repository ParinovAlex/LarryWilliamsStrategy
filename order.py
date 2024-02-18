class Order:
    def __init__(self, id, date, type,openPrice,stop,profit):
        self.id = id
        self.date = date
        self.type = type # buy, sell
        self.openPrice = openPrice
        self.stop = stop
        self.profit = profit
        self.status = "active" # active, closed
        self.value = 0
        self.closePrice = 0
        self.barsInRun = 1
    
    def ValidateProfit(self, price):
        res = 0
        if self.type == "buy":
               return price - self.openPrice 
        
        if self.type == "sell":
               return self.openPrice - price
        return res
    
    def IsStoppedOut(self, price):
        if self.type == "buy":
            if price < self.openPrice - self.stop:
                return True
        if self.type == "sell":
            if price > self.openPrice + self.stop:
                return True
        return False

    def CloseAsStoppedOut(self):
        self.status = "closed"
        if self.type == "buy":
            self.closePrice = round(self.openPrice - self.stop,2)
        if self.type == "sell":
            self.closePrice = round(self.openPrice + self.stop,2)
        
        self.value = round(self.ValidateProfit(self.closePrice),2)
        return True

    def Close(self, price):
        self.status = "closed"
        self.value = round(self.ValidateProfit(price),2)
        self.closePrice = price

class Reporting:
    def __init__(self, DetailsReportPerYear = False, OrdersDetailsReportPerYear = False, OrdersDetailsReportPerYearToFile = False, AccumulationCurvePerYear = False, TotalProfitForPeriod = False, ShortPerYear = False, ShortPerYearWithParameters = False, PrintDataGraph = False):
        self.id = 0
        self.DetailsReportPerYear = DetailsReportPerYear
        self.OrdersDetailsReportPerYear = OrdersDetailsReportPerYear
        self.OrdersDetailsReportPerYearToFile = OrdersDetailsReportPerYearToFile
        self.AccumulationCurvePerYear = AccumulationCurvePerYear
        self.TotalProfitForPeriod = TotalProfitForPeriod
        self.ShortPerYear = ShortPerYear
        self.ShortPerYearWithParameters = ShortPerYearWithParameters
        self.PrintDataGraph = PrintDataGraph

class OrderBook:
    def __init__(self):
        self.orderList = []

        pass
    def NumberOfOrders(self, type): # type = buy, all, sell, profitable, nonprofitable, breakeven
        count = 0
        
        if(type == "all"):
            return len(self.orderList)
        
        if(type == "profitable"):
            for order in self.orderList:
                if order.status == "closed" and order.value > 0:
                    count += 1
            return count

        if(type == "nonprofitable"):
            for order in self.orderList:
                if order.status == "closed" and order.value < 0:
                    count += 1
                return count
            
        if(type == "breakeven"):
            for order in self.orderList:
                if order.status == "closed" and order.value == 0:
                    count += 1
            return count
        
        for order in self.orderList:
                if order.type == type:
                        count += 1
        return count
    
    def IsActiveOrders(self):
        for order in self.orderList:
            if order.status == "active":
                return True
        return False
    
    def TotalLoss(self):
        res = 0
        for order in self.orderList:
            if order.status == "closed" and order.value < 0:
                res = res + order.value     
        return round(res,2)
    
    def TotalProfit(self):
        res = 0
        for order in self.orderList:
            if order.status == "closed" and order.value > 0:
                res = res + order.value
        return res
    
    def Profit(self):                
        return round(self.TotalProfit() + self.TotalLoss(),2)
    
    def WinRate(self):                
        return round(self.NumberOfOrders("profitable")/self.NumberOfOrders("all") * 100,2)
    
    def MaxProfitOrder(self):
        res = 0
        for order in self.orderList:
            if order.status == "closed" and order.value > 0:
                if order.value > res:
                    res = order.value
        return res
    
    def AverageProfit(self):
        res = 0
        for order in self.orderList:
            if order.status == "closed" and order.value > 0:
                if order.value > res:
                    res = order.value
        return round(res,2)
    
    def MaxLossOrder(self):
        res = 0
        for order in self.orderList:
            if order.status == "closed" and order.value < 0:
                if order.value < res:
                    res = order.value
        return res
    
    def MaxConsequtiveWinsAndLoss(self):
        wins = []
        loss = []
        res = []
        count = 0
        for order in self.orderList:
            if order.status == "closed" and order.value > 0:
                count += 1
            else:
                wins.append(count)
                count = 0
        count = 0
        for order in self.orderList:
            if order.status == "closed" and order.value < 0:
                count += 1
            else:
                loss.append(count)
                count = 0
        cw = 0
        for i in wins:
            if i > cw:
                cw = i
        res.append(cw)
        cl = 0
        for i in loss:
            if i > cl:
                cl = i
        res.append(cl)        
        return res
    
    def MaxDrawnDown(self):
        res = 0
        minval = 0
        for order in self.orderList:
            if order.status == "closed":
                res = res + order.value
                if res < minval:
                    minval = res
        return round(minval,2)
    
    def AccumulatedCurve(self):
        res = []
        profit = 0
        for order in self.orderList:
            if order.status == "closed":
                profit = profit + order.value
                res.append(profit)
        return res
            
    def LogOrders(self):
        print("Date\t\tType\tOpen price \tStop\tProfit\tStatus\tValue\tClosePrice \tDays")
        
        for order in self.orderList:
            print("{}\t{}\t{} \t{}\t{}\t{}\t{}\t{} \t{}".format(order.date,order.type,round(order.openPrice,2),order.stop,order.profit,order.status,order.value,order.closePrice,order.barsInRun))

    def LogOrdersToFile(self):
        with open('order_report.csv', 'w') as f:
            f.write("Date;Type;Open price;Stop;Profit;Status;Value;ClosePrice;Days\n")
        
            for order in self.orderList:
                f.write("{};{};{};{};{};{};{};{};{}\n".format(order.date,order.type,round(order.openPrice,2),order.stop,order.profit,order.status,order.value,order.closePrice,order.barsInRun))


    def OrdersReport(self, DetailsforYear, showorders,savetofile):
        if DetailsforYear == True:
            print("Number of all orders: {}".format(self.NumberOfOrders("all"))) # type = buy, all, sell, profitable, nonprofitable, breakeven
            print("Number of profitable orders: {}".format(self.NumberOfOrders("profitable")))
            print("Number of loss orders: {}".format(self.NumberOfOrders("nonprofitable")))
            print("Profit: {}".format(self.Profit()))
            print("Total profit: {}".format(self.TotalProfit()))
            print("Total loss: {}".format(self.TotalLoss()))
            print("Win Rate: {}%".format(self.WinRate()))
            print("Max win: {}".format(self.MaxProfitOrder()))
            print("Max loss: {}".format(self.MaxLossOrder()))
            NoF = self.NumberOfOrders("profitable")
            if NoF == 0:
                NoF = 0.001
            print("Average win: {}".format(round(self.TotalProfit()/NoF,2)))
            print("Average Loss: {}".format(round(self.TotalLoss()/NoF,2)))
            cons = self.MaxConsequtiveWinsAndLoss()
            print("Max consequtive wins: {}".format(cons[0]))
            print("Max consequtive loss: {}".format(cons[1]))
            print("Max drawn down: {}".format(round(self.MaxDrawnDown(),2)))
        if showorders == True:
            self.LogOrders()
        if savetofile == True:
            self.LogOrdersToFile()
    