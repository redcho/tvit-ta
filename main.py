from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

import pytz
import pandas as pd

from strategies import MACDStrategy
import pytz

AMSTERDAM = pytz.timezone("Europe/Amsterdam")

def load_df():
    symbol = "BNBEUR"

    df = pd.read_csv(f"../binance-crawler/data/{symbol}/20201231_2259-20210401_2259.csv")
    df = df.drop(columns=['ignore', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'quote_asset_volume',
                          'num_trades'])
    df['open_time'] = pd \
        .to_datetime(df['open_time'], unit='ms') \
        .dt.tz_localize('UTC') \
        .dt.tz_convert(AMSTERDAM)

    df['close_time'] = pd \
        .to_datetime(df['close_time'], unit='ms') \
        .dt.tz_localize('UTC') \
        .dt.tz_convert(AMSTERDAM)

    df.set_index('open_time', inplace=True)

    # Filter if necessary
    feb = pd.to_datetime("2021-02-01") \
        .tz_localize(AMSTERDAM)
    month = df[df.index >= feb]

    print(month.info())
    return df


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000.0)
    cerebro.broker.setcommission(commission=0.00075)

    cerebro.addstrategy(MACDStrategy.SignalStrategy)

    data = bt.feeds.PandasData(dataname=load_df(), tz=pytz.timezone('Europe/Amsterdam'))

    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
    # Plot the result
    # cerebro.plot(style='bar')

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())