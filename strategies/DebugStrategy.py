import backtrader as bt
import pandas as pd

from strategies.DefaultStrategy import DefaultStrategy

from util.bt_logging import get_logger


class DebugStrategy(DefaultStrategy):
    logger = get_logger(__name__)

    params = (
        # Metadata
        ("symbol", ""),
        ("interval", ""),
        ("fromdate", ""),
        ("todate", ""),
        # FAST EMA BAND
        ("ema1", 3),
        ("ema2", 5),
        ("ema3", 8),
        ("ema4", 10),  # ATR Period (standard)
        ("ema5", 12),  # ATR distance for stop price
        ("ema6", 15),
        # SLOW EMA BAND
        ("ema7", 30),
        ("ema8", 35),
        ("ema9", 40),
        ("ema10", 45),
        ("ema11", 50),
        ("ema12", 60),
        ("atrperiod", 14),  # ATR Period (standard)
        ("atrdist", 3.0),  # ATR distance for stop price
    )

    def __init__(self):
        # Main signal
        super().__init__()

        self.strategy_id = "bb_ema12"
        self.logger.debug(f"Strategy is being initiated with id {self.strategy_id}")

        self.ema1 = bt.indicators.ExponentialMovingAverage(period=self.p.ema1)
        self.ema2 = bt.indicators.ExponentialMovingAverage(period=self.p.ema2)
        self.ema3 = bt.indicators.ExponentialMovingAverage(period=self.p.ema3)
        self.ema4 = bt.indicators.ExponentialMovingAverage(period=self.p.ema4)
        self.ema5 = bt.indicators.ExponentialMovingAverage(period=self.p.ema5)
        self.ema6 = bt.indicators.ExponentialMovingAverage(period=self.p.ema6)
        self.ema7 = bt.indicators.ExponentialMovingAverage(period=self.p.ema7)
        self.ema8 = bt.indicators.ExponentialMovingAverage(period=self.p.ema8)
        self.ema9 = bt.indicators.ExponentialMovingAverage(period=self.p.ema9)
        self.ema10 = bt.indicators.ExponentialMovingAverage(period=self.p.ema10)
        self.ema11 = bt.indicators.ExponentialMovingAverage(period=self.p.ema11)
        self.ema12 = bt.indicators.ExponentialMovingAverage(period=self.p.ema12)

        self.bb = bt.indicators.BollingerBands()

        self.debug_df = pd.DataFrame()

    def prenext(self):
        self.debug_df = self.debug_df.append(
            {
                "datetime": f"{self.datas[0].datetime.date()} {self.datas[0].datetime.time()}",
                "close": self.data.close[0],
                "ema1": self.ema1[0],
                "ema2": self.ema2[0],
                "ema3": self.ema3[0],
                "ema4": self.ema4[0],
                "ema5": self.ema5[0],
                "ema6": self.ema6[0],
                "ema7": self.ema7[0],
                "ema8": self.ema8[0],
                "ema9": self.ema9[0],
                "ema10": self.ema10[0],
                "ema11": self.ema11[0],
                "ema12": self.ema12[0],
                "bbup": self.bb.top[0],
                "bblow": self.bb.bot[0],
                "bbmid": self.bb.mid[0],
                "volume": self.data.volume[0],
            },
            ignore_index=True,
        )
        super().next()

    def next(self):
        self.debug_df = self.debug_df.append(
            {
                "datetime": f"{self.datas[0].datetime.date()} {self.datas[0].datetime.time()}",
                "close": self.data.close[0],
                "ema1": self.ema1[0],
                "ema2": self.ema2[0],
                "ema3": self.ema3[0],
                "ema4": self.ema4[0],
                "ema5": self.ema5[0],
                "ema6": self.ema6[0],
                "ema7": self.ema7[0],
                "ema8": self.ema8[0],
                "ema9": self.ema9[0],
                "ema10": self.ema10[0],
                "ema11": self.ema11[0],
                "ema12": self.ema12[0],
                "bbup": self.bb.top[0],
                "bblow": self.bb.bot[0],
                "bbmid": self.bb.mid[0],
                "volume": self.data.volume[0],
            },
            ignore_index=True,
        )
        super().next()

    def stop(self):
        self.debug_df.to_csv(f"{self.p.symbol}_{self.p.interval}_{self.p.fromdate}_{self.p.todate}_{self.strategy_id}.csv", index=False)
        self.log("Simulation ending..")
