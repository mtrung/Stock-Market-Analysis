import pandas_datareader as pdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def pullData(stock, timeDelta: timedelta):
    # -------------------- Getting the data --------------------
    # self.start_time = (date.today() - timedelta(month_window * 365 / 12)).isoformat()
    end_time = datetime.today()
    start_time = end_time - timeDelta #datetime(2014, 1, 1)
    
    # self.end_time = datetime(2020, 1, 28)
    # data = pdr.get_data_yahoo(stock, start=start_time, end=end_time)
    return pdr.DataReader(stock, 'yahoo', start_time, end_time), start_time, end_time

class movingAverages:
    def __init__(self, stock: str, average_type: str):
        self.indicators = None
        self.stock = stock
        self.shortMAName = 'short_MA'
        self.longMAName = 'long_MA'

        # Simple or Exponential Moving Average
        self.average_type = average_type

    def pullData(self, timeDelta: timedelta):
        self.data, self.start_time, self.end_time = pullData(self.stock, timeDelta)

    def get_positions(self, short: int = 5, long: int = 20):
        # Short moving average
        self.short_window = short  #50
        self.shortMAName = f'{self.shortMAName}_{self.short_window}'
        # Long moving average
        self.long_window = long  #200        
        self.longMAName = f'{self.longMAName}_{self.long_window}'

        # -------------- Moving Average Algorithm ---------------
        indicators = pd.DataFrame(index=self.data.index)
        indicators['price'] = self.data['Adj Close']
        indicators['signal'] = 0.0

        # Short and long window average over the data period
        if self.average_type == "simple":
            indicators[self.shortMAName] = self.data['Close'].rolling(window=self.short_window, min_periods=1,
                                                                 center=False).mean()
            indicators[self.longMAName] = self.data['Close'].rolling(window=self.long_window, min_periods=1,
                                                                center=False).mean()
        elif self.average_type == "exponential":
            indicators[self.shortMAName] = self.data['Close'].ewm(span=self.short_window, adjust=False).mean()
            indicators[self.longMAName] = self.data['Close'].ewm(span=self.long_window, adjust=False).mean()

        # Where they cross
        indicators['signal'][self.short_window:] = np.where(
            indicators[self.shortMAName][self.short_window:] > indicators[self.longMAName][self.short_window:],
            1.0, 0.0)

        # Buy vs Sell
        indicators['positions'] = indicators['signal'].diff()
        self.indicators = indicators
        return indicators.loc[indicators['positions'] ** 2 == 1]

    def get_time(self):
        return self.start_time, self.end_time

    def get_data(self):
        return self.data

    def plot(self):
        # -------------------- Plotting -------------------------
        # Get data from object
        indicators = self.indicators
        data = self.data
        # Create the plot
        fig = plt.figure(figsize=(13, 10))

        # Labels for plot
        ax1 = fig.add_subplot(111, ylabel=self.stock)

        # Plot stock price over time
        data['Close'].plot(ax=ax1, color='black', lw=2.)

        # Plot the the short and long moving averages
        indicators[[self.shortMAName, self.longMAName]].plot(ax=ax1, lw=2.)

        # Plot where to buy indicators
        ax1.plot(indicators.loc[indicators.positions == 1.0].index,
                 indicators[self.shortMAName][indicators.positions == 1.0],
                 '^', markersize=10, color='g')

        # Plots where to sell indicators
        ax1.plot(indicators.loc[indicators.positions == -1.0].index,
                 indicators[self.shortMAName][indicators.positions == -1.0],
                 'v', markersize=10, color='r')

        # Show the plot
        plt.show()
