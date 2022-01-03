import pandas as pd
import pytz


class BackTraderIO:
    def __init__(
        self, symbol, interval, fromdate, todate, tz=pytz.timezone("Europe/Amsterdam")
    ):
        self.symbol = symbol
        self.interval = interval
        self.fromdate = fromdate
        self.todate = todate
        self.tz = tz

        self.bt_df = self._binance_to_bt_df(self._read_df())

    def _read_df(self):
        # TODO After the crawler daily shards implementation, load in here using params
        date_range = "20220103"

        return pd.read_csv(
            f"~/data/binance/{self.symbol}/{self.interval}/{date_range}.csv"
        )

    def _binance_to_bt_df(self, df):
        df["datetime"] = (
            pd.to_datetime(df["OpenTime"], unit="ms")
            .dt.tz_localize("UTC")
            .dt.tz_convert(self.tz)
        )

        COLUMNS = [
            "datetime",
            "Open",
            "Close",
            "High",
            "Low",
            "Volume",
            "NumberOfTrades",
        ]

        bt_source = df[COLUMNS].copy()
        bt_source.set_index("datetime", inplace=True)

        return bt_source

    def filter(self, dt="2021-02-28 15:40:00"):
        filt = pd.to_datetime(dt, format="%Y-%m-%d %H:%M:%S").tz_localize(self.tz)
        return self.bt_df[self.bt_df.index >= filt]

    def get_data(self):
        return self.bt_df
