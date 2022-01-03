from __future__ import absolute_import, division, print_function, unicode_literals

import backtrader as bt
import pandas as pd
import pytz
import quantstats
from util.BackTraderIO import BackTraderIO
from util.cerebro_helper import get_cerebro

from strategies import MACDStrategy
from strategies import CombinedStrategy

from strategies.DebugStrategy import DebugStrategy
from util.bt_logging import get_logger


def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)
    print("SQN: {}".format(sqn))


def printTradeAnalysis(analyzer):
    """
    Function to print the Technical Analysis results in a nice format.
    """
    # Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = (total_won / total_closed) * 100
    # Designate the rows
    h1 = ["Total Open", "Total Closed", "Total Won", "Total Lost"]
    h2 = ["Strike Rate", "Win Streak", "Losing Streak", "PnL Net"]
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    # Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    # Print the rows
    print_list = [h1, r1, h2, r2]
    row_format = "{:<18}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format("", *row))


def printCerebroResult(results, symbol):
    printTradeAnalysis(results[0].analyzers.getbyname("trades").get_analysis())
    printSQN(results[0].analyzers.getbyname("sqn").get_analysis())

    portfolio_stats = results[0].analyzers.getbyname("PyFolio")
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    quantstats.reports.html(
        returns, output=f"stats-{symbol}.html", title=f"{symbol} Trading Return Report"
    )


# Deprecate? Possibly to some analysis helper classes and dedicated analysis classes
if __name__ == "__main__":
    logger = get_logger(__name__)

    # logging.basicConfig(filename='app.log', filemode='w',
    #                     format='%(name)s - %(levelname)s - %(message)s')

    symbols = {
        "ETHUSDT": {
            # Data source conf
            "interval": "1h",
            "fromdate": "2021-01-01",
            "todate": "2022-01-01",
            # Trade conf
            "cash": 1000.0,
            "commission": 0.00075,
            "stake": 100,
        },
    }

    tz = pytz.timezone("Europe/Amsterdam")

    for symbol, conf in symbols.items():

        cerebro = get_cerebro(
            symbol,
            conf["interval"],
            conf["fromdate"],
            conf["todate"],
            DebugStrategy,
            cash=conf["cash"],
            commission=conf["commission"],
            stake=conf["stake"],
        )

        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name="PyFolio")
        logger.debug(f"Active analyzers are {cerebro.analyzers}")

        logger.debug("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
        cerebro.addwriter(bt.WriterFile, csv=False, out="a.csv")
        r = cerebro.run()
        logger.debug("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

        # printCerebroResult(r, symbol)

        # cerebro.plot(style='bar', stdstats=True)

        # cerebro.optstrategy(
        #     CombinedStrategy.CombinedStrategy,
        #     kama=range(10,15),
        #     macd2=range(20,30)
        # )

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
