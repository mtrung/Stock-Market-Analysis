from Moving_Average import movingAverages
from datetime import timedelta
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime, timedelta

import job


def printTitle(header: str):
    print(f'\n------ {header} ------')


def back_test(data, indicators, start_time, end_time):

    num_buy = len(indicators.loc[indicators.positions == 1.0])
    num_sell = len(indicators.loc[indicators.positions == -1.0])
    total_buy = sum(indicators.loc[indicators.positions == 1.0]['price'])
    total_sell = sum(indicators.loc[indicators.positions == -1.0]['price'])
    if num_buy != num_sell:
        # In case there was no sell indicator, so now profit is current value of stock
        total_buy += data['Close'][-1]
    total_profit_trading = total_sell - total_buy + (num_buy - num_sell)
    total_profit_holding = data['Close'][-1] - data['Close'][0]
    # percent_increase = 100 * (total_profit_trading - total_profit_holding) / total_profit_holding
    percent_increase = 100*(total_profit_trading/total_profit_holding-1)

    printTitle('Data With Swing Trading')
    print('Profit = ' + str(round(total_profit_trading, 2)))

    printTitle('Just Buy and Hold')
    print('Profit  = ' + str(round(total_profit_holding, 2)))

    printTitle('Analysis')
    print('Time in years spend trading = ' +
          str(round((end_time - start_time).days / 365, 2)))
    print('Trades made = ' + str(num_buy + num_sell))
    print('Price of Stock =  ' +
          str(data['Close'][0]) + ' now at ' + str(data['Close'][-1]))
    print('Swing Trading did ' +
          str(round(percent_increase, 2)) + '% better than holding')
    return percent_increase


# -------------------- data importing and back testing -------------------------
def sma(stock, toPlot=False):
    printTitle('Simple Moving Average Crossover')
    p = movingAverages(stock, "simple")
    p.pullData(timeDelta)
    indicators = p.get_positions(5, 15)
    data = p.get_data()
    print(str(back_test(data, indicators, p)) + "%")

    # print(p.indicators)
    # convert the column (it's a string) to datetime type
    # print(df)
    if toPlot:
        p.plot()


def ema(stock, toPlot=False):
    printTitle('Exponential Moving Average Crossover')
    p = movingAverages(stock, "exponential")
    p.pullData(timeDelta)
    indicators = p.get_positions(5, 15)
    data = p.get_data()
    print(str(back_test(data, indicators, p)) + "%")

    if toPlot:
        p.plot()


timeDelta = timedelta(days=300)


def getTimeTuple():
    end_time = datetime.today()
    start_time = end_time - timeDelta
    return start_time, end_time


def main(stock='TSLA'):
    # sma(stock, True)

    j = job.Job()
    # end_time = datetime.today()
    # start_time = end_time - timeDelta  # datetime(2014, 1, 1)
    start_time, end_time = getTimeTuple()
    j.add(pdr.DataReader, stock, 'yahoo', start_time, end_time)
    p = movingAverages(stock, "simple")
    j.add(p.get_positions)
    j.add(p.dollarCostAvg)
    df = j.exec()
    print(df)
    df = p.indicators.loc[p.indicators['positions'] ** 2 == 1]
    s = back_test(j.data, df, start_time, end_time)
    print(f'{s}%')
    p.plot()


if __name__ == "__main__":
    import plac
    plac.call(main)
