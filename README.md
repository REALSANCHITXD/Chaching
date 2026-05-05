# 📈 Asynchronous Algorithmic Trading Engine

An advanced, event-driven algorithmic trading bot built in Python. This engine provides real-time market data ingestion, asynchronous quantitative analysis, and high-frequency trade execution across multiple financial markets. It features an intelligent decision engine, dynamic risk management, and a comprehensive real-time live dashboard.

## 🚀 Key Features

- **⚡ Asynchronous Event Loop:** Built entirely on Python's `asyncio` and `ThreadPoolExecutor` for zero-blocking I/O requests and sub-second execution latency.
- **🌍 Multi-Market Support:** Seamlessly integrates with **Alpaca** for US Stocks and **Binance** for Cryptocurrencies.
- **🧠 Machine Learning Integration:** Utilizes Hugging Face's `FinBERT` transformer model to perform live Natural Language Processing (NLP) sentiment analysis on financial news.
- **📊 Quantitative Indicators:** Vectorized real-time computation of RSI, MACD, EMA, and Bollinger Bands using `pandas`.
- **🎯 Dynamic Risk Management:** Automatically sizes positions based on risk ceilings and executes strict stop-loss/take-profit parameters.
- **💻 Modern UI:** Beautiful, decoupled local dashboard built with Flask and Chart.js for real-time WebSocket-style tracking.

## 📈 Real-Time Portfolio Analytics
The dashboard features an integrated math engine that calculates institutional-grade risk metrics in real-time as the bot executes paper/live trades:
- **Live Sharpe Ratio:** Dynamically calculates annualized risk-adjusted returns based on tick-by-tick equity curve variance.
- **Max Drawdown:** Monitors peak-to-trough equity drops in real-time to visualize the effectiveness of the dynamic stop-loss system.
- **Dynamic PnL Tracking:** Millisecond-accurate unrealized and realized profit tracking across all open positions.

## 📋 Table of Contents
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Decision Engine System](#decision-engine-system)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

## 🏗️ Architecture

The system is decoupled into isolated, highly cohesive components:

### Backend (Python/Asyncio)
The backend core runs a continuous asynchronous event loop.

**Core Components:**
- **`main.py`**: The central orchestrator. Manages the lifecycle, initializes executors, and triggers the `asyncio` data ingestion loop.
- **`async_fetcher.py`**: Handles concurrent API requests to Alpaca and Binance.
- **`indicator_logic.py`**: The vectorized math engine calculating price momentum and volatility.
- **`sentiment_finbert.py`**: The NLP inference layer processing qualitative market news.
- **`decision_engine.py`**: The central brain that scores normalized inputs and generates algorithmic trade execution signals.

### Frontend (Flask/Chart.js)
A lightweight web server (`dashboard.py`) designed to visualize the bot's memory state without polluting the main trading loop.
- Features real-time PnL tracking and dynamic Candlestick/Line charts.
- Pulls live snapshots via REST endpoints.

## 🚀 Quick Start

### Backend Setup
Install the required dependencies:
```bash
pip install -r requirements.txt
```

Set up your `config.yaml` file with your preferred API keys and assets:
```yaml
mode: paper  # Options: paper, live_crypto, live_stocks
crypto_assets:
  - BTCUSDT
  - ETHUSDT
```

### Running the System
Start the live dashboard visualization server in one terminal:
```bash
python dashboard.py
```
Start the core trading engine in a separate terminal:
```bash
python main.py
```
The dashboard will be available at `http://localhost:5000`

## 🧠 Decision Engine System

The algorithmic brain provides intelligent, multi-factor signal analysis.

### Signal Generation Flow
1. **Data Ingestion:** Concurrent fetching of live order book data.
2. **Indicator Computation:** Vectorized calculation of RSI and MACD.
3. **Sentiment Analysis:** FinBERT categorizes news into Positive/Negative/Neutral.
4. **Scoring:** The engine calculates a normalized `total_score` based on quantitative metrics and NLP sentiment.
5. **Execution:** If the score breaches the confidence threshold, a Buy/Sell signal is passed to the Executor.

## ⚙️ Configuration

The `config.yaml` file allows complete control over the bot's behavior:

- **Mode Configuration:**
  - `paper`: Tracks real prices but executes simulated trades using fake money.
  - `live_crypto`: Executes real trades on Binance.
  - `live_stocks`: Executes real trades on Alpaca.
- **Risk Management:** Define max risk per trade, stop-loss percentages, and take-profit percentages.
- **Asset Selection:** Define the exact tickers to track.

## 📁 Project Structure

```text
TradingBot/
├── main.py                    # Core execution loop
├── dashboard.py               # Flask frontend server
├── config.yaml                # System configuration
├── requirements.txt           # Python dependencies
│
├── data_sources/              # API Integrations
│   ├── alpaca_feed.py
│   ├── binance_feed.py
│   └── sentiment_finbert.py
│
├── strategies/                # Logic & Math
│   ├── decision_engine.py
│   └── indicator_logic.py
│
├── utils/                     # Helpers
│   ├── async_fetcher.py
│   ├── cache_manager.py
│   └── risk_manager.py
│
└── templates/                 # Frontend
    └── dashboard.html         # UI template
```

## 🗺️ Roadmap & Future Enhancements
The architecture is specifically designed to be extensible. Planned future modules include:
- **🗄️ Permanent Database Integration:** Hooking up PostgreSQL/SQLAlchemy to persist historical trade logs and equity curves.
- **⚡ WebSockets Upgrade:** Transitioning from REST polling to Binance/Alpaca WebSockets for zero-latency streaming tick data.
- **🌍 Global Markets Integration:** Adding new `data_sources` to tap into the London Stock Exchange (LSE) and Singapore Exchange (SGX) for cross-border arbitrage.
- **🧠 Custom ML Models:** Training an LSTM neural network in PyTorch for predictive volume analysis to supersede standard MACD indicators.
- **⏪ Historical Backtesting Engine:** A standalone script to simulate the `decision_engine` logic over 5 years of historical data.

## ⚠️ Disclaimer
IMPORTANT: This application is for educational and research purposes only. It is NOT financial advice. The `live_trading` modes will execute real financial transactions using your connected brokerage accounts. Use at your own risk.
