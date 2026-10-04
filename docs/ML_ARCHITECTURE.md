# ML Architecture

## Overview

The ML system predicts next-trading-day price direction (UP / DOWN) for nine Indian stocks using historical market data, feature engineering, and trained classification models.

## Data Flow

```
Yahoo Finance (yfinance)
        ↓
Raw OHLCV CSV files (ml-service/data/raw/)
        ↓
Feature Engineering (prepare_dataset.py)
        ↓
Processed Dataset (ml-service/data/processed/stock_features.csv)
        ↓
Chronological Train / Test Split
        ↓
Model Training (train_models.py)
        ↓
Saved Models (ml-service/models/*.joblib)
        ↓
FastAPI Inference Service (app.py, port 8000)
        ↓
Express Backend Proxy (backend/index.js, port 3002)
        ↓
Dashboard Analytics Dialog (WatchList.js)
```

## Supported Stocks

| Symbol | Yahoo Finance Ticker | NSE Name |
|--------|---------------------|----------|
| INFY | INFY.NS | Infosys |
| ONGC | ONGC.NS | Oil & Natural Gas Corp |
| TCS | TCS.NS | Tata Consultancy Services |
| KPITTECH | KPITTECH.NS | KPIT Technologies |
| QUICKHEAL | QUICKHEAL.NS | Quick Heal Technologies |
| WIPRO | WIPRO.NS | Wipro |
| M&M | M&M.NS | Mahindra & Mahindra |
| RELIANCE | RELIANCE.NS | Reliance Industries |
| HUL | HINDUNILVR.NS | Hindustan Unilever |

## Features (8 Indicators)

| Feature | Description |
|---------|-------------|
| Return_1D | 1-day percentage return |
| Return_5D | 5-day percentage return |
| Return_10D | 10-day percentage return |
| Price_vs_MA20 | Price deviation from 20-day moving average |
| Price_vs_MA50 | Price deviation from 50-day moving average |
| RSI_14 | 14-period Relative Strength Index |
| Volatility_20D | 20-day rolling standard deviation of daily returns |
| Volume_Ratio | Current volume / 20-day average volume |

## Target Variable

- **Binary classification**: Next trading day's direction
- `1` = Next trading day's close > current day's close (UP)
- `0` = Next trading day's close ≤ current day's close (DOWN)
- Only uses information available at prediction time (no future data leakage)

## Models

### Logistic Regression
- Uses `sklearn.pipeline.Pipeline` with `StandardScaler` + `LogisticRegression`
- Scaler fitted only on training data
- Serves as a linear baseline

### Random Forest
- `RandomForestClassifier` with 200 estimators, max depth 12
- `class_weight="balanced"` to handle class imbalance
- Selected as primary model for the API response

## Training Process

1. **Data Download** (`download_data.py`): Downloads ~10 years of daily OHLCV data from Yahoo Finance
2. **Feature Preparation** (`prepare_dataset.py`): Calculates 8 features, creates target, drops NaN rows
3. **Training** (`train_models.py`):
   - Loads processed dataset
   - Performs **chronological split** (80% train / 20% test by date)
   - Leaves one-date gap between train and test sets
   - Trains Logistic Regression and Random Forest
   - Evaluates against two baselines:
     - Majority-class baseline
     - Repeat-direction baseline
   - Saves models to `ml-service/models/`
   - Saves metrics to `ml-service/results/metrics.json`

## Chronological Evaluation

- Time-series data is **never randomly shuffled**
- Older dates are used for training; newer dates for testing
- A one-date gap prevents information leakage at the boundary
- The scaler (Logistic Regression pipeline) is fitted only on training data

## Latest Inference Logic

When a prediction is requested:

1. `prepare_stock_data(symbol, filename, include_latest=True)` is called
2. It reads the raw CSV, computes all features for every row
3. The **latest row with complete features** is extracted before labelling
4. This row has no target (its next-day close is unknown — that's what we're predicting)
5. The trained model's `predict_proba()` is called on this row
6. The prediction date in the response is the date of this latest data row

This ensures the model uses the most recent available data, not the last training example.

## API Endpoints

### FastAPI ML Service (port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with loaded model info |
| `/api/stocks` | GET | List supported stock symbols |
| `/api/insights/{symbol}` | GET | Full prediction + indicators + history |

### Express Backend Proxy (port 3002)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/ml/stocks` | GET | JWT | Proxy to ML `/api/stocks` |
| `/api/ml/insights/:symbol` | GET | JWT | Proxy to ML `/api/insights/{symbol}` |

### Insight Response Schema

```json
{
  "symbol": "INFY",
  "latestDate": "2026-10-03",
  "latestClose": 1555.45,
  "predictionDate": "2026-10-03",
  "selectedModel": "Random Forest",
  "probabilityUp": 0.62,
  "probabilityDown": 0.38,
  "direction": "UP",
  "indicators": {
    "rsi14": 54.3,
    "ma20": 1540.12,
    "ma50": 1520.88,
    "volatility20d": 0.015
  },
  "predictions": {
    "logisticRegression": { "probabilityUp": 0.58, "probabilityDown": 0.42 },
    "randomForest": { "probabilityUp": 0.62, "probabilityDown": 0.38 }
  },
  "history": [...],
  "disclaimer": "Experimental model estimates..."
}
```

## Model Storage

- Saved models: `ml-service/models/`
  - `logistic_regression.joblib` — Logistic Regression pipeline
  - `random_forest.joblib` — Random Forest classifier
  - `feature_columns.json` — Ordered list of feature names
- Models are loaded once at FastAPI startup, not on every request

## Leakage Prevention

1. Target is computed from `shift(-1)` on Close — only uses future close for labelling, not as a feature
2. The last raw data row (with unknown next-day close) is excluded from training but used for inference
3. Chronological split ensures the model never sees future data during training
4. The scaler is fitted only on training data

## Limitations

- Models are trained on historical data and may not generalize to future market conditions
- Accuracy is close to baseline (~49% Random Forest on test set) — typical for short-term stock prediction
- Models do not account for news, earnings, macro events, or market sentiment
- Historical data from Yahoo Finance may have delays or gaps
- No automatic retraining pipeline — models must be retrained manually

## Disclaimer

**Predictions are for informational and educational purposes only.** They are NOT financial advice and do NOT guarantee future performance. Past performance of the model on historical data is not indicative of future results. Users should not make investment decisions based solely on these predictions.
