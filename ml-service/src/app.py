from pathlib import Path
import json

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from src.prepare_dataset import FEATURE_COLUMNS, STOCK_FILES, prepare_stock_data


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stock_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"

LOGISTIC_MODEL_FILE = (
    MODEL_DIR / "logistic_regression.joblib"
)

RANDOM_FOREST_MODEL_FILE = (
    MODEL_DIR / "random_forest.joblib"
)

FEATURES_FILE = MODEL_DIR / "feature_columns.json"


# --------------------------------------------------
# 2. CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Zerodha Clone ML API",
    description=(
        "Experimental stock insights and "
        "next-day direction predictions."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# 3. LOAD DATA AND MODELS
# --------------------------------------------------

def load_resources():
    required_files = [
        DATA_FILE,
        LOGISTIC_MODEL_FILE,
        RANDOM_FOREST_MODEL_FILE,
        FEATURES_FILE,
    ]

    for file_path in required_files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {file_path}"
            )

    data = pd.read_csv(DATA_FILE)
    data["Date"] = pd.to_datetime(data["Date"])

    with open(
        FEATURES_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        features = json.load(file)

    logistic_model = joblib.load(
        LOGISTIC_MODEL_FILE
    )

    random_forest_model = joblib.load(
        RANDOM_FOREST_MODEL_FILE
    )

    return (
        data,
        features,
        logistic_model,
        random_forest_model,
    )


try:
    (
        stock_data,
        feature_columns,
        logistic_model,
        random_forest_model,
    ) = load_resources()

    print("ML data and models loaded successfully.")

except Exception as error:
    print(f"Failed to load ML resources: {error}")
    raise


# --------------------------------------------------
# 4. HELPER: CONVERT NUMPY VALUES TO PYTHON VALUES
# --------------------------------------------------

def safe_float(value):
    """Convert a value to a JSON-friendly float."""

    if pd.isna(value):
        return None

    return float(value)


def get_latest_inference_row(symbol):
    """Generate an unlabelled feature row from the newest raw OHLCV record."""
    try:
        _, latest_features = prepare_stock_data(
            symbol,
            STOCK_FILES[symbol],
            include_latest=True,
        )
    except (FileNotFoundError, ValueError, KeyError) as error:
        raise HTTPException(
            status_code=503,
            detail=f"Latest ML features for '{symbol}' are unavailable: {error}",
        ) from error

    if feature_columns != FEATURE_COLUMNS:
        raise HTTPException(status_code=500, detail="Saved feature order is incompatible.")

    return latest_features.iloc[-1], latest_features[feature_columns].iloc[[-1]]
# --------------------------------------------------
# 5. HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Zerodha Clone ML API",
        "stocks_loaded": int(
            stock_data["Symbol"].nunique()
        ),
        "models_loaded": [
            "Logistic Regression",
            "Random Forest",
        ],
    }


# --------------------------------------------------
# 6. LIST AVAILABLE STOCKS
# --------------------------------------------------

@app.get("/api/stocks")
def get_stocks():
    symbols = sorted(
        stock_data["Symbol"].unique().tolist()
    )

    return {
        "stocks": symbols,
        "count": len(symbols),
    }


# --------------------------------------------------
# 7. STOCK INSIGHTS AND PREDICTIONS
# --------------------------------------------------

@app.get("/api/insights/{symbol}")
def get_stock_insights(symbol: str):
    symbol = symbol.upper()

    # Select the requested stock
    df = stock_data[
        stock_data["Symbol"] == symbol
    ].copy()

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Stock '{symbol}' was not found.",
        )

    df = df.sort_values("Date").reset_index(drop=True)

    # Generate the newest unlabelled feature row directly from raw OHLCV data.
    latest, model_input = get_latest_inference_row(symbol)

    # Get probability of the next-day direction being UP
    logistic_probability = float(
        logistic_model.predict_proba(
            model_input
        )[0][1]
    )

    random_forest_probability = float(
        random_forest_model.predict_proba(
            model_input
        )[0][1]
    )

    # Return approximately the latest 120 trading sessions
    history_df = df.tail(120).copy()

    history = []

    for _, row in history_df.iterrows():
        history.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close": safe_float(row["Close"]),
            "return1d": safe_float(row["Return_1D"]),
            "ma20": safe_float(
                row["Close"]
                * (1 + row["Price_vs_MA20"])
            ),
            "ma50": safe_float(
                row["Close"]
                * (1 + row["Price_vs_MA50"])
            ),
            "rsi14": safe_float(row["RSI_14"]),
            "volatility20d": safe_float(
                row["Volatility_20D"]
            ),
        })

    return {
        "symbol": symbol,
        "latestDate": latest["Date"].strftime(
            "%Y-%m-%d"
        ),
        "latestClose": safe_float(latest["Close"]),
        "predictionDate": latest["Date"].strftime("%Y-%m-%d"),
        "selectedModel": "Random Forest",
        "probabilityUp": random_forest_probability,
        "probabilityDown": 1 - random_forest_probability,
        "direction": "UP" if random_forest_probability >= 0.5 else "DOWN",
        "indicators": {
            "rsi14": safe_float(latest["RSI_14"]),
            "ma20": safe_float(
                latest["Close"]
                * (1 + latest["Price_vs_MA20"])
            ),
            "ma50": safe_float(
                latest["Close"]
                * (1 + latest["Price_vs_MA50"])
            ),
            "volatility20d": safe_float(
                latest["Volatility_20D"]
            ),
        },
        "predictions": {
            "logisticRegression": {
                "probabilityUp": logistic_probability,
                "probabilityDown": (
                    1 - logistic_probability
                ),
            },
            "randomForest": {
                "probabilityUp": random_forest_probability,
                "probabilityDown": (
                    1 - random_forest_probability
                ),
            },
        },
        "history": history,
        "disclaimer": (
            "Experimental model estimates based on historical "
            "data. Not investment advice or a guarantee of "
            "future performance. Historical data may be delayed."
        ),
    }