# DeFi Analytics Framework

A modular framework for analyzing DEX mispricing opportunities using Injective Protocol's indexer and Allora's prediction models. This framework enables real-time monitoring of arbitrage opportunities while leveraging machine learning predictions for enhanced decision making.

## 🌟 Features

- Real-time price monitoring across multiple DEXes via Injective Indexer
- Advanced mispricing detection algorithms
- Integration with Allora for price movement predictions
- Configurable reporting system with multiple output formats
- Modular architecture for easy extension
- Async-first design for optimal performance

## 🏗️ Project Structure 

```
defi-analytics/
├── src/
│   ├── indexer/              # Data collection from DEXes
│   │   ├── injective.py      # Injective Protocol integration
│   │   └── interfaces.py     # Abstract interfaces for indexers
│   ├── analysis/             # Analysis modules
│   │   ├── mispricing.py     # Mispricing detection logic
│   │   └── metrics.py        # Performance metrics calculation
│   ├── agents/               # Autonomous agents
│   │   ├── reporter.py       # Report generation
│   │   └── monitor.py        # Continuous monitoring
│   ├── allora/               # Allora integration
│   │   ├── predictor.py      # Price prediction logic
│   │   └── models.py         # ML model configurations
│   └── output/               # Output formatting
│       ├── formatters.py     # Data formatting utilities
│       └── publishers.py     # Publishing to different platforms
├── config/
│   └── settings.yaml         # Configuration settings
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Injective Protocol API access
- Allora API credentials

### Installation

1. Clone the repository: 
```bash
git clone https://github.com/yourusername/defi-analytics.git
cd defi-analytics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings in `config/settings.yaml`:
```yaml
injective:
  network: "mainnet"
  api_key: "your_api_key"

allora:
  model_id: "price_prediction_v1"
  api_key: "your_allora_api_key"

monitoring:
  update_interval: 60  # seconds
  token_pairs:
    - "INJ/USDT"
    - "ETH/USDT"
    # Add more pairs as needed
```

## 📊 Usage

### Basic Usage

```python
from defi_analytics.indexer import InjectiveIndexer
from defi_analytics.analysis import MispricingAnalyzer
from defi_analytics.agents import MispricingReporter
from defi_analytics.allora import AlloraPredictor

# Initialize components
indexer = InjectiveIndexer()
predictor = AlloraPredictor(model_config={...})
analyzer = MispricingAnalyzer([indexer], predictor)
reporter = MispricingReporter(analyzer)

# Generate report
report = await reporter.generate_report(["INJ/USDT"])
print(report.format_report())
```

### Running the Monitor

```bash
python -m defi_analytics.agents.monitor
```

## 📈 Output Example

```json
{
  "timestamp": "2024-03-14T12:00:00Z",
  "opportunities": [
    {
      "token_pair": "INJ/USDT",
      "dex_a": "Injective",
      "dex_b": "OtherDEX",
      "price_difference": 0.015,
      "confidence": 0.95,
      "estimated_profit": 120.50,
      "liquidity_constraints": {
        "max_trade_size": 10000,
        "slippage_estimate": 0.001
      }
    }
  ],
  "market_conditions": {
    "volatility": "medium",
    "trend": "upward"
  },
  "predictions": {
    "price_direction": "up",
    "confidence_interval": [45.2, 46.8]
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Injective Protocol team for their excellent indexer
- Allora team for their prediction models
- The DeFi community for continuous inspiration

## ⚠️ Disclaimer

This software is for educational purposes only. Always perform your own research and risk assessment before trading.