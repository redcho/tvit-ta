from yaml import load, FullLoader

from util.constants import CONF_FILE
from strategies.DebugStrategy import DebugStrategy

from util.bt_logging import get_logger
from util.cerebro_helper import get_cerebro

logger = get_logger(__name__)

if __name__ == "__main__":

    with open(CONF_FILE, "r") as f:
        d = load(f.read(), Loader=FullLoader)

        SYMBOL = "symbol"

        m = d['metadata']

        for symbol in d[SYMBOL]:
            logger.debug(f"Requesting cerebro for {symbol} with following conf {m}")
            bt_core = get_cerebro(
                symbol, m["interval"], m["fromdate"], m["todate"], DebugStrategy
            )
            bt_core.run()
