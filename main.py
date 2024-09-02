import time
from okx_api import OkxAPI
from trading_strategy import TradingStrategy
from utils import setup_logging

logger = setup_logging()


def main():
    okx = OkxAPI()
    okx.start_websocket()
    strategy = TradingStrategy(okx)

    try:
        while True:
            strategy.execute()
            time.sleep(1)  # 每秒检查一次
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    finally:
        okx.stop_websocket()


if __name__ == "__main__":
    main()
