# OKX 永续合约量化交易机器人(摇钱树)

监控USDT/BTC, 当波动速率超过阈值并且回撤幅度超过阈值时, 自动买入卖出

## 依赖

- python 3.10+

## 安装

```bash
git clone https://github.com/niostack/okx-yqs.git
cd okx-yqs
pip install -r requirements.txt
```

## 配置

1. 在项目根目录创建 `.env` 文件
2. 在 `.env` 文件中添加以下内容:

```bash
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
```

## 运行

```bash
python main.py
```

## 注意事项

- 请确保了解交易风险后再使用本程序
- 建议先在OKX的测试网络中测试程序
- 可以根据需要调整 `config.py` 中的参数
