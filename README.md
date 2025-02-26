# DeFi Analytics Framework

A modular framework for analyzing DEX mispricing opportunities using Injective Protocol's indexer and Allora's prediction models. This framework enables real-time monitoring of arbitrage opportunities while leveraging machine learning predictions for enhanced decision making.

## 🌟 Features

### Implemented Features
- ✅ Real-time price monitoring via Injective Indexer
- ✅ Integration with Allora for price movement predictions
- ✅ Configurable trading agent framework
- ✅ Advanced resource management and monitoring
- ✅ Comprehensive logging system
- ✅ Automated risk management
- ✅ Interface-based architecture for modularity
- ✅ HTTP and Blockchain client abstractions

### Planned Features (Not Yet Implemented)
- ⏳ Advanced mispricing detection algorithms
- ⏳ Multi-DEX support
- ⏳ Performance analytics dashboard
- ⏳ Machine learning model integration for custom predictions
- ⏳ Backtesting framework

## 🏗️ Project Structure 

```
defi-analytics/
├── src/
│   ├── agents/
│   │   ├── base_agent.py         # Base trading agent implementation
│   │   └── example_injective_agent.py  # Example Injective-specific agent
│   ├── allora/
│   │   ├── predictor.py         # Price prediction implementation
│   │   ├── client.py           # Allora API client
│   │   └── interfaces.py       # Prediction interfaces
│   ├── blockchain/
│   │   └── injective_client.py # Injective blockchain client implementation
│   ├── config/
│   │   ├── __init__.py        # Configuration exports
│   │   └── config_loader.py    # Configuration management
│   ├── http/
│   │   └── aiohttp_client.py  # HTTP client implementation
│   ├── indexer/
│   │   ├── injective.py       # Injective Protocol integration
│   │   └── interfaces.py      # Indexer interfaces
│   ├── interfaces/
│   │   ├── iagent.py         # Agent interface
│   │   ├── ipredictor.py     # Predictor interface
│   │   ├── ihttp_client.py   # HTTP client interface
│   │   └── iblockchain_client.py # Blockchain client interface
│   └── run_agent.py          # Main runner script with resource management
├── tests/
│   ├── unit/
│   │   ├── agents/           # Agent unit tests
│   │   ├── allora/           # Allora integration tests
│   │   ├── config/           # Configuration tests
│   │   ├── http/            # HTTP client tests
│   │   └── indexer/         # Indexer tests
│   └── conftest.py          # Test fixtures and utilities
├── config/
│   └── settings.yaml        # Application configuration
└── pyproject.toml          # Project metadata and dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Injective Protocol API access
- Allora API credentials
- At least 2GB available RAM
- Stable internet connection

### Setting up Development Environment

1. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. Clone the repository and install dependencies:
```bash
git clone https://github.com/yourusername/defi-analytics.git
cd defi-analytics
pip install -e ".[test]"  # Installs with test dependencies
```

3. Configure your settings in `config/settings.yaml`:
```yaml
injective:
  network: "testnet"  # Use "mainnet" for production
  api_key: "your_injective_api_key"
  markets:
    - id: "INJ/USDT"
      min_trade_size: 100
      max_trade_size: 10000
      risk_parameters:
        max_position_size: 5000
        max_slippage: 0.01  # 1%
        stop_loss: 0.02     # 2%

allora:
  api_key: "your_allora_api_key"
  model_id: "price_prediction_v1"
  base_url: "https://api.allora.com/v1"
  confidence_level: 0.95
  prediction_settings:
    min_confidence: 0.8
    time_horizon: 3600  # 1 hour prediction window
    update_interval: 300  # Update predictions every 5 minutes

monitoring:
  update_interval: 60  # seconds
  min_profit_threshold: 0.01  # 1% minimum profit target
  max_active_positions: 3
  risk_management:
    portfolio_stop_loss: 0.05  # 5% portfolio stop loss
    max_daily_trades: 50
    cooldown_period: 300  # 5 minutes after a loss

logging:
  level: "INFO"
  file_path: "logs/trading.log"
  rotation: "1 day"
  retention: "30 days"
```

## 🔄 Resource Management

The framework includes comprehensive resource management features:

### Memory Management
- Automatic memory monitoring (warning threshold: 1000MB)
- Garbage collection optimization
- Historical data pruning
- Resource cleanup on shutdown

### Performance Monitoring
- Execution time tracking per agent
- Performance degradation detection
- Automatic warning system
- Resource usage statistics

### Error Handling
- Exponential backoff (5s to 5min)
- Circuit breaker implementation
- Graceful shutdown handling
- Proper task cancellation

### Logging System
- Rotating log files (10MB per file)
- Console and file logging
- Structured log format
- Automatic log directory creation

## 🚀 Running the Agent

1. Ensure your configuration is set up in `config/settings.yaml`

2. Run the agent:
```bash
python src/run_agent.py <your_private_key>
```

### Monitoring Your Agent

Monitor your agent through:
1. Console output (real-time logs)
2. Log files at `logs/trading.log`
3. Memory usage warnings (if approaching 1000MB)
4. Performance alerts in logs

### Stopping the Agent

To stop the agent:
- Press Ctrl+C for graceful shutdown
- The agent will complete pending operations and clean up resources

## 🧪 Testing

Run the test suite:

```bash
# Basic test run
pytest tests/

# With coverage report
pytest --cov=src --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
```

## ⚠️ Known Limitations

1. Currently only supports Injective Protocol
2. Single agent per market
3. Limited to spot trading
4. No automated backtesting
5. Memory-only state management (no persistence)

## 🔒 Security Considerations

1. Store API keys securely (not in config files)
2. Monitor system resources regularly
3. Set appropriate risk parameters
4. Review logs for unusual activity
5. Keep dependencies updated

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 🏛️ Architecture

The framework is built on a modular, interface-based architecture that promotes:

### 1. Core Interfaces
- `IAgent`: Base interface for trading agents
- `IPredictor`: Interface for price prediction services
- `IHttpClient`: Abstract HTTP client operations
- `IBlockchainClient`: Abstract blockchain interactions

### 2. Implementation Layers
- **HTTP Layer**: Implements HTTP client interface using `aiohttp`
- **Blockchain Layer**: Implements blockchain client interface for Injective Protocol
- **Prediction Layer**: Implements prediction interface using Allora API
- **Agent Layer**: Implements trading strategies using the base agent interface

### 3. Resource Management
- Memory monitoring and optimization
- Automatic garbage collection
- Performance tracking
- Graceful error handling

### 4. Configuration Management
- YAML-based configuration
- Environment-specific settings
- Risk parameter management
- API credentials management

## 💻 Implementation Details

### HTTP Client
- Asynchronous HTTP operations using `aiohttp`
- Automatic session management
- Configurable retry logic
- Error handling and logging

### Blockchain Client
- Injective Protocol integration
- Market data fetching
- Order management
- Position tracking

### Prediction Service
- Integration with Allora API
- Historical data processing
- Confidence interval calculation
- Market state analysis

### Trading Agent
- Risk management implementation
- Order size calculation
- Position management
- Performance monitoring