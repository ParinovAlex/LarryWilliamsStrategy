from strategy_runner import StrategyRunner
from order import Reporting
reporting = Reporting(True, False, False, False, False, False, True, False)
""" 
DetailsReportPerYear 
OrdersDetailsReportPerYear
OrdersDetailsReportPerYearToFile
AccumulationCurvePerYear
TotalProfitForPeriod
ShortPerYear
ShortPerYearWithParameters
PrintDataGraph """

""" intervals
[1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]  """

StrategyRunner("5m",range(4, 5), range(1, 2), range(1, 2), range(2024,2025), reporting)
