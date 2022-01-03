import backtrader as bt


class SuperTrendBand(bt.Indicator):
    """
    Helper inidcator for Supertrend indicator
    """

    params = (("period", 7), ("multiplier", 3))
    lines = ("basic_ub", "basic_lb", "final_ub", "final_lb")

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.p.period)
        self.l.basic_ub = ((self.data.high + self.data.low) / 2) + (
            self.atr * self.p.multiplier
        )
        self.l.basic_lb = ((self.data.high + self.data.low) / 2) - (
            self.atr * self.p.multiplier
        )

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.final_ub[0] = self.l.basic_ub[0]
            self.l.final_lb[0] = self.l.basic_lb[0]
        else:
            # =IF(OR(basic_ub<final_ub*,close*>final_ub*),basic_ub,final_ub*)
            if (
                self.l.basic_ub[0] < self.l.final_ub[-1]
                or self.data.close[-1] > self.l.final_ub[-1]
            ):
                self.l.final_ub[0] = self.l.basic_ub[0]
            else:
                self.l.final_ub[0] = self.l.final_ub[-1]

            # =IF(OR(baisc_lb > final_lb *, close * < final_lb *), basic_lb *, final_lb *)
            if (
                self.l.basic_lb[0] > self.l.final_lb[-1]
                or self.data.close[-1] < self.l.final_lb[-1]
            ):
                self.l.final_lb[0] = self.l.basic_lb[0]
            else:
                self.l.final_lb[0] = self.l.final_lb[-1]


class SuperTrend(bt.Indicator):
    """
    Super Trend indicator
    """

    params = (("period", 7), ("multiplier", 3))
    lines = ("super_trend",)
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.stb = SuperTrendBand(period=self.p.period, multiplier=self.p.multiplier)

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.super_trend[0] = self.stb.final_ub[0]
            return

        if self.l.super_trend[-1] == self.stb.final_ub[-1]:
            if self.data.close[0] <= self.stb.final_ub[0]:
                self.l.super_trend[0] = self.stb.final_ub[0]
            else:
                self.l.super_trend[0] = self.stb.final_lb[0]

        if self.l.super_trend[-1] == self.stb.final_lb[-1]:
            if self.data.close[0] >= self.stb.final_lb[0]:
                self.l.super_trend[0] = self.stb.final_lb[0]
            else:
                self.l.super_trend[0] = self.stb.final_ub[0]


class DefaultMACDStrategy(bt.Strategy):
    params = (
        # Standard MACD Parameters
        ("macd1", 12),
        ("macd2", 26),
        ("macdsig", 9),
        ("atrperiod", 14),  # ATR Period (standard)
        ("atrdist", 3.0),  # ATR distance for stop price
        # ('smaperiod', 15),  # SMA Period (pretty standard)
        # ('dirperiod', 3),  # Lookback period to consider SMA trend direction
        ("atrperiod", 14),  # ATR Period (standard)
        ("atrdist", 3.0),  # ATR distance for stop price
    )

    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.pstop = None

        self.dataclose = self.datas[0].close

        # Main signal
        self.macd = bt.indicators.MACDHisto(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig,
        )
        self.macd_crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        # To set the stop loss order
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

    def log(self, txt):
        """Logging function fot this strategy"""
        dt = self.datas[0].datetime.date(0)
        tm = self.datas[0].datetime.time()
        print("%s: %s, %s" % (dt.isoformat(), tm, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(
            "OPERATION PROFIT, GROSS %.5f, NET %.5f, STOP_LOSS %.5f"
            % (trade.pnl, trade.pnlcomm, self.pstop)
        )


class SignalStrategy(DefaultMACDStrategy):
    def next(self):
        if self.order:
            return

        if not self.position:
            # We might BUY
            # if self.macd_crossover[0] > 0:
            if self.macd_crossover[0] > 0:
                self.order = self.buy()
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist
        else:
            if self.macd_crossover[0] < 0:
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
            # We might BUY
            if self.macd.histo[0] > 0:
                self.order = self.buy()
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist
        else:
            if self.macd.histo[0] < 0:
                self.order = self.sell()
            elif self.data.close[0] < self.pstop:
                self.order = self.sell()
            else:
                pdist = self.atr[0] * self.p.atrdist
                # Update only if greater than
                self.pstop = max(self.pstop, self.data.close[0] - pdist)


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
