import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class movingAverages:
    def __init__(self, stock: str, average_type: str):
        self.indicators = None
        self.stock = stock
        self.shortMAName = 'short_MA'
        self.longMAName = 'long_MA'

        # Simple or Exponential Moving Average
        self.average_type = average_type

    def __call__(self, df):
        return self.get_positions(df)

    def get_positions(self, data, short: int = 5, long: int = 20):
        self.data = data

        # Short moving average
        self.short_window = short  # 50
        self.shortMAName = f'{self.shortMAName}_{self.short_window}'
        # Long moving average
        self.long_window = long  # 200
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
            indicators[self.shortMAName] = self.data['Close'].ewm(
                span=self.short_window, adjust=False).mean()
            indicators[self.longMAName] = self.data['Close'].ewm(
                span=self.long_window, adjust=False).mean()

        # Where they cross
        indicators['signal'][self.short_window:] = np.where(
            indicators[self.shortMAName][self.short_window:
                                         ] > indicators[self.longMAName][self.short_window:],
            1.0, 0.0)

        # Buy vs Sell
        indicators['positions'] = indicators['signal'].diff()

        self.indicators = indicators
        # return indicators.loc[indicators['positions'] ** 2 == 1]
        return indicators

    def dollarCostAvg(self, indicators):
        # day 15 of the month
        indicators['positions'][indicators.index.day == 15] = 1.0
        return indicators

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
