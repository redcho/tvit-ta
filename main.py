from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import pandas as pd
import pytz

from strategies import MACDStrategy

AMSTERDAM = pytz.timezone("Europe/Amsterdam")

def load_df():
    symbol = "BNBEUR"

    df = pd.read_csv(f"../binance-crawler/data/{symbol}/20201231_2259-20210401_2259.csv")

    df['datetime'] = pd \
        .to_datetime(df['open_time'], unit='ms') \
        .dt.tz_localize('UTC') \
        .dt.tz_convert(AMSTERDAM)

    df = df.drop(columns=['ignore', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'quote_asset_volume',
                          'num_trades', 'open_time', 'close_time'])

    # df['close_time'] = pd \
    #     .to_datetime(df['close_time'], unit='ms') \
    #     .dt.tz_localize('UTC') \
    #     .dt.tz_convert(AMSTERDAM)

    df.set_index('datetime', inplace=True)

    # Filter if necessary
    feb = pd.to_datetime("2021-01-31 15:40:00", format='%Y-%m-%d %H:%M:%S') \
        .tz_localize(AMSTERDAM)
    month = df[df.index >= feb]

    # DEBUG
    # now = pd.to_datetime("2021-02-01 00:00:00", format='%Y-%m-%d %H:%M:%S') \
    #     .tz_localize(AMSTERDAM)
    # now_r = df.loc[ now , : ]
    # print(now_r)

    print(month.head())
    return month


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(250.0)
    cerebro.broker.setcommission(commission=0.00075)

    cerebro.addstrategy(MACDStrategy.SignalStrategy)

    data = bt.feeds.PandasData(dataname=load_df(), tz=pytz.timezone('Europe/Amsterdam'))

    cerebro.adddata(data)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    print(results[0].analyzers.getbyname("trades").get_analysis())

    # Plot the result
    # cerebro.plot(style='bar')

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
