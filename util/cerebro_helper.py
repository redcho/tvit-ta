import backtrader as bt
from util.bt_logging import get_logger
import pytz
from util.BackTraderIO import BackTraderIO

logger = get_logger(__name__)
tz = pytz.timezone("Europe/Amsterdam")


def get_cerebro(
    symbol,
    interval,
    fromdate,
    todate,
    strategy,
    cash=None,
    commission=None,
    stake=None,
):
    cerebro = bt.Cerebro()
    logger.debug("Cerebro created..")

    if cash is not None:
        cerebro.broker.setcash(cash)
        logger.debug(f"Initial cash amount is set to {cash}")

    if commission is not None:
        cerebro.broker.setcommission(commission=commission)
        logger.debug(f"Broker commission is set to {commission}")

    if stake is not None:
        cerebro.addsizer(bt.sizers.SizerFix, stake=stake)
        logger.debug(f"Position size is fixed to {stake}")

    try:
        cerebro.addstrategy(strategy, symbol=symbol, interval=interval, fromdate=fromdate, todate=todate)
        logger.debug(f"Strategy added to cerebro")
    except Exception as e:
        logger.error(f"Encountered an error trying to add strategy")
        raise

    try:
        bt_data = BackTraderIO(symbol, interval, fromdate, todate).get_data()
        logger.debug(
            f"Data loaded from {fromdate} to {todate} for {symbol} per {interval}"
        )

        data = bt.feeds.PandasData(dataname=bt_data, tz=tz)
        cerebro.adddata(data)
        cerebro.addtz(tz)
        logger.debug(f"Data feed added to the simulation feed")
    except Exception as e:
        logger.error(f"Encountered an error trying to add data")

    return cerebro
