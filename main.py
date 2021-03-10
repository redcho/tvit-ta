from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import pandas as pd
import pytz
import quantstats

from strategies import MACDStrategy
from strategies import CombinedStrategy

AMSTERDAM = pytz.timezone("Europe/Amsterdam")

def load_df(symbol="BNBEUR"):
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
    # filt = pd.to_datetime("2021-02-28 15:40:00", format='%Y-%m-%d %H:%M:%S') \
    #     .tz_localize(AMSTERDAM)
    # filtered = df[df.index >= filt]

    # DEBUG
    # now = pd.to_datetime("2021-02-01 00:00:00", format='%Y-%m-%d %H:%M:%S') \
    #     .tz_localize(AMSTERDAM)
    # now_r = df.loc[ now , : ]
    # print(now_r)

    # print(df.head())
    return df


def printSQN(analyzer):
    sqn = round(analyzer.sqn,2)
    print('SQN: {}'.format(sqn))


def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total,2)
    strike_rate = (total_won / total_closed) * 100
    #Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate','Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed,total_won,total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    print_list = [h1,r1,h2,r2]
    row_format ="{:<18}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))


def printCerebroResult(results, symbol):
    printTradeAnalysis(results[0].analyzers.getbyname("trades").get_analysis())
    printSQN(results[0].analyzers.getbyname("sqn").get_analysis())

    portfolio_stats = results[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    quantstats.reports.html(returns, output=f'stats-{symbol}.html', title=f'{symbol} Trading Return Report')


if __name__ == '__main__':

    symbols = {
        # "BNBEUR": {
        #     "cash": 300.0,
        #     "commission": 0.00075,
        #     "stake": 1
        # },
        # "BTCUSDT": {
        #     "cash": 70000.0,
        #     "commission": 0.00075,
        #     "stake": 1
        # },
        # "ETHEUR": {
        #     "cash": 2000.0,
        #     "commission": 0.00075,
        #     "stake": 1
        # },
        "XEMUSDT": {
            "cash": 1000.0,
            "commission": 0.00075,
            "stake": 100
        }
    }

    for symbol, conf in symbols.items():
        cerebro = bt.Cerebro()

        cerebro.broker.setcash(conf['cash'])
        cerebro.broker.setcommission(commission=conf['commission'])

        cerebro.addsizer(bt.sizers.SizerFix, stake=conf['stake'])

        # params = (
        #     # Standard MACD Parameters
        #     ('macd1', 12),
        #     ('macd2', 26),
        #     ('macdsig', 9),
        #     ('atrperiod', 14),  # ATR Period (standard)
        #     ('atrdist', 3.0),  # ATR distance for stop price
        #     # ('smaperiod', 15),  # SMA Period (pretty standard)
        #     # ('dirperiod', 3),  # Lookback period to consider SMA trend direction
        #     ('atrperiod', 14),  # ATR Period (standard)
        #     ('atrdist', 3.0),  # ATR distance for stop price
        #     ('kama', 10),
        #     supertrend
        # )

        # cerebro.optstrategy(
        #     CombinedStrategy.CombinedStrategy,
        #     kama=range(10,15),
        #     macd2=range(20,30)
        # )

        cerebro.addstrategy(CombinedStrategy.CombinedStrategy)

        data = bt.feeds.PandasData(dataname=load_df(symbol=symbol), tz=AMSTERDAM)

        cerebro.adddata(data)

        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

        r = cerebro.run()
        printCerebroResult(r, symbol)
        # cerebro.plot(style='bar', stdstats=True)



        # import pyfolio as pf
        # pf.create_full_tear_sheet(
        #     returns,
        #     positions=positions,
        #     transactions=transactions,
        #     # gross_lev=gross_lev,
        #     live_start_date='2008-01-01',  # This date is sample specific
        #     round_trips=True)
        # pf.create_simple_tear_sheet(returns)
        # pf.create_returns_tear_sheet(returns)

        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
