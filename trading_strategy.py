import time
import pandas as pd
import numpy as np
from config import (
    PRICE_CHANGE_1S_THRESHOLD,
    PRICE_CHANGE_3S_THRESHOLD,
    PRICE_CHANGE_5S_THRESHOLD,
    PRICE_CHANGE_10S_THRESHOLD,
    PRICE_CHANGE_30S_THRESHOLD,
    PRICE_CHANGE_1M_THRESHOLD,
    TRADE_AMOUNT,
    STOP_LOSS_THRESHOLD,
)
from utils import setup_logging

logger = setup_logging()


class TradingStrategy:
    def __init__(self, okx_api):
        self.okx_api = okx_api
        self.price_history = []
        self.position = 0  # 当前持仓量，正数表示多头，负数表示空头
        self.entry_price = None  # 入场价格
        self.last_trade_time = time.time()  # 上一次交易时间
        self.total_profit = 0  # 总收益

    def check_stop_loss(self, current_price):
        if self.position != 0 and self.entry_price is not None:
            loss_percentage = (
                (self.entry_price - current_price)
                / self.entry_price
                * (1 if self.position > 0 else -1)
            )
            if loss_percentage > STOP_LOSS_THRESHOLD:
                try:
                    if self.position > 0:
                        order = self.okx_api.create_market_sell_order(
                            abs(self.position)
                        )
                        logger.info(f"触发止损，执行卖出操作: {order}")
                    else:
                        order = self.okx_api.create_market_buy_order(abs(self.position))
                        logger.info(f"触发止损，执行买入操作: {order}")
                    self.position = 0
                    self.entry_price = None
                except Exception as e:
                    logger.error(f"止损操作失败: {str(e)}")

    def execute(self):
        current_price = self.okx_api.get_latest_price()
        if current_price is None:
            return  # 等待WebSocket获取价格数据
        # self.check_stop_loss(current_price)
        self.price_history.append(current_price)

        if len(self.price_history) > 60:  # 保留最近60个价格点
            self.price_history.pop(0)

        if len(self.price_history) < 60:
            return  # 等待收集足够的数据

        df = pd.DataFrame(self.price_history, columns=["price"])
        pre_price = df["price"].iloc[-1]
        # 计算涨幅（最近60个价格点的变化百分比）
        price_change_1s = (current_price - df["price"].iloc[-2]) / df["price"].iloc[-2]
        price_change_3s = (current_price - df["price"].iloc[-3]) / df["price"].iloc[-3]
        price_change_5s = (current_price - df["price"].iloc[-5]) / df["price"].iloc[-5]
        price_change_10s = (current_price - df["price"].iloc[-10]) / df["price"].iloc[
            -10
        ]
        price_change_30s = (current_price - df["price"].iloc[-30]) / df["price"].iloc[
            -30
        ]
        price_change_1m = (current_price - df["price"].iloc[-60]) / df["price"].iloc[
            -60
        ]
        # 计算最大涨幅
        max_price = df["price"].max()
        min_price = df["price"].min()
        max_price_change = (max_price - min_price) / max_price
        # 计算回撤涨幅
        start_price = df["price"].iloc[-60]
        if current_price > start_price:
            back_price_change = (max_price - current_price) / (max_price - min_price)
        else:
            back_price_change = (current_price - min_price) / (max_price - min_price)
        # 计算方向
        if current_price > start_price:
            direction = "up"
        else:
            direction = "down"
        # 持仓信息
        if self.position != 0:
            logger.info(
                f"持仓数量: {self.position} - 持仓价格: {self.entry_price:.2f} 当前价格:{current_price:.2f} - 当前涨幅: {(current_price - self.entry_price)/self.entry_price*100:.2f}% total_profit: {self.total_profit:.2f}"
            )
        else:
            logger.info(
                f"当前无持仓 {current_price} - {pre_price} - {max_price} - {min_price} m: {max_price_change*100:.2f}% b: {back_price_change*100:.2f}% total_profit: {self.total_profit:.2f}"
            )

        if (
            max_price_change > 0.001
            and back_price_change > 0.5
            and time.time() - self.last_trade_time > 60
        ):
            # self.okx_api.create_market_buy_order(TRADE_AMOUNT)
            old_position = self.position
            if direction == "up":
                self.position -= TRADE_AMOUNT
            else:
                self.position += TRADE_AMOUNT
            # 更新持仓均价
            if self.entry_price is None:
                self.entry_price = current_price
            elif self.position == 0:
                if old_position > 0:
                    self.total_profit += (
                        current_price - self.entry_price
                    ) * old_position
                else:
                    self.total_profit += (
                        self.entry_price - current_price
                    ) * -old_position
                self.entry_price = None
            else:
                self.entry_price = (
                    self.entry_price * old_position
                    + current_price * (self.position - old_position)
                ) / self.position
            logger.info(
                f"{direction=='up' and '卖出' or '买入'} {current_price} - {pre_price} - {max_price} - {min_price} 1s: {price_change_1s*100:.2f}% 3s: {price_change_3s*100:.2f}% 5s: {price_change_5s*100:.2f}% 10s: {price_change_10s*100:.2f}% 30s: {price_change_30s*100:.2f}% 1m: {price_change_1m*100:.2f}% m: {max_price_change*100:.2f}% b: {back_price_change*100:.2f}%"
            )
            self.last_trade_time = time.time()  # 更新上一次交易时间
