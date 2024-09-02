import logging
import sys


def setup_logging():
    # 创建一个logger
    logger = logging.getLogger()

    # 如果logger已经有处理器，说明已经设置过，直接返回
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 创建一个handler，用于写入日志文件
    file_handler = logging.FileHandler("trading_bot.log")
    file_handler.setLevel(logging.INFO)

    # 创建一个handler，用于将日志输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 定义handler的输出格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将handler添加到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
