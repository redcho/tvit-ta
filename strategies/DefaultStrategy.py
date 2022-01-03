import backtrader as bt
from util.bt_logging import get_logger


class DefaultStrategy(bt.Strategy):
    logger = get_logger(__name__)

    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.pstop = None

        self.dataclose = self.datas[0].close

    def log(self, txt):
        """Logging function fot this strategy"""
        dt = self.datas[0].datetime.date()
        tm = self.datas[0].datetime.time()
        self.logger.debug("%s: %s, %s" % (dt.isoformat(), tm, txt))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log("Close, %.2f" % self.dataclose[0])

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
