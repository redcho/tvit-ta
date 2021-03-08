import backtrader as bt

class DefaultMACDStrategy(bt.Strategy):
    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),  # ATR distance for stop price
        # ('smaperiod', 15),  # SMA Period (pretty standard)
        # ('dirperiod', 3),  # Lookback period to consider SMA trend direction
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),  # ATR distance for stop price
    )

    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.pstop = None

        self.dataclose = self.datas[0].close

        # Main signal
        self.macd = bt.indicators.MACDHisto(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.macd_crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        # To set the stop loss order
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

    def log(self, txt):
        ''' Logging function fot this strategy'''
        dt = self.datas[0].datetime.date(0)
        tm = self.datas[0].datetime.time()
        print('%s: %s, %s' % (dt.isoformat(), tm, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))


class SignalStrategy(DefaultMACDStrategy):
    def next(self):
        if self.order:
            return

        if not self.position:
            # We might BUY
            if self.macd_crossover[0] > 0:
                self.order = self.buy()
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist
        else:
            if self.macd_crossover[0] < 0:
                self.order = self.sell()
            elif self.data.close[0] < self.pstop:
                self.order = self.sell()
            else:
                pdist = self.atr[0] * self.p.atrdist
                # Update only if greater than
                self.pstop = max(self.pstop, self.data.close[0] - pdist)


class CrossOverStrategy(DefaultMACDStrategy):
    def next(self):
        if self.order:
            return

        if not self.position:
            if self.macd.histo[0] > 0:
                self.order = self.buy()
        else:
            if self.macd.histo[0] < 0:
                self.order = self.sell()


class FlipStrategy(DefaultMACDStrategy):
    def next(self):
        if self.order:
            return

        if not self.position:
            if self.macd.histo[0] > self.macd.signal[0]:
                self.order = self.buy()
        else:
            if self.macd.histo[0] < self.macd.signal[0]:
                self.order = self.sell()
