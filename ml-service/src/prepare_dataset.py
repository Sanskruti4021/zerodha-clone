from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DATA_DIR / "stock_features.csv"

FEATURE_COLUMNS = [
    "Return_1D",
    "Return_5D",
    "Return_10D",
    "Price_vs_MA20",
    "Price_vs_MA50",
    "RSI_14",
    "Volatility_20D",
    "Volume_Ratio",
]


# CSV filenames created by download_data.py
STOCK_FILES = {
    "INFY": "INFY.csv",
    "ONGC": "ONGC.csv",
    "TCS": "TCS.csv",
    "KPITTECH": "KPITTECH.csv",
    "QUICKHEAL": "QUICKHEAL.csv",
    "WIPRO": "WIPRO.csv",
    "M&M": "M&M.csv",
    "RELIANCE": "RELIANCE.csv",
    "HUL": "HUL.csv",
}


REQUIRED_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def calculate_rsi(close, period=14):
    """Calculate the Relative Strength Index."""

    price_change = close.diff()

    gains = price_change.clip(lower=0)
    losses = -price_change.clip(upper=0)

    average_gain = gains.rolling(window=period).mean()
    average_loss = losses.rolling(window=period).mean()

    relative_strength = average_gain / average_loss

    rsi = 100 - (100 / (1 + relative_strength))

    # Handle periods with no losses
    rsi = rsi.mask(
        (average_loss == 0) & (average_gain > 0),
        100,
    )

    # Handle periods with neither gains nor losses
    rsi = rsi.mask(
        (average_loss == 0) & (average_gain == 0),
        50,
    )

    return rsi


def prepare_stock_data(symbol, filename, include_latest=False):
    """Load one stock CSV and calculate its ML features."""

    file_path = RAW_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    # Check that the downloaded CSV has the required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{filename} is missing columns: {missing_columns}"
        )

    # Keep the required columns and convert their data types
    df = df[REQUIRED_COLUMNS].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Sort dates and remove invalid or duplicate records
    df = df.dropna(subset=["Date", "Close"])
    df = df.sort_values("Date")
    df = df.drop_duplicates(subset=["Date"], keep="last")
    df = df.reset_index(drop=True)

    # Daily returns
    df["Return_1D"] = df["Close"].pct_change()
    df["Return_5D"] = df["Close"].pct_change(periods=5)
    df["Return_10D"] = df["Close"].pct_change(periods=10)

    # Price relative to moving averages
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()

    df["Price_vs_MA20"] = (df["Close"] / df["MA20"]) - 1
    df["Price_vs_MA50"] = (df["Close"] / df["MA50"]) - 1

    # Momentum indicator
    df["RSI_14"] = calculate_rsi(df["Close"], period=14)

    # Volatility: standard deviation of daily returns
    df["Volatility_20D"] = (
        df["Return_1D"].rolling(window=20).std()
    )

    # Current volume relative to its 20-day average
    df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()

    df["Volume_Ratio"] = (
        df["Volume"] / df["Volume_MA20"]
    )

    # This row has complete historical features but no next-day target.
    latest_features = df.dropna(subset=FEATURE_COLUMNS).tail(1).copy()
    if latest_features.empty:
        raise ValueError(f"{filename} has no complete feature row.")
    latest_features["Symbol"] = symbol

    # Target: will the next trading day's close be higher?
    next_close = df["Close"].shift(-1)

    df["Target"] = (next_close > df["Close"]).astype("int64")

    # The final row has no known next-day closing price.
    # Remove it, along with rows missing rolling features.
    df = df.iloc[:-1].copy()

    feature_columns = [
        "Return_1D",
        "Return_5D",
        "Return_10D",
        "Price_vs_MA20",
        "Price_vs_MA50",
        "RSI_14",
        "Volatility_20D",
        "Volume_Ratio",
    ]

    df = df.dropna(
        subset=FEATURE_COLUMNS + ["Target"]
    )

        # Add the stock symbol BEFORE selecting the columns
    df["Symbol"] = symbol

    # Keep only the fields required for modelling and analysis
    df = df[
        [
            "Date",
            "Symbol",
            "Close",
            "Return_1D",
            "Return_5D",
            "Return_10D",
            "Price_vs_MA20",
            "Price_vs_MA50",
            "RSI_14",
            "Volatility_20D",
            "Volume_Ratio",
            "Target",
        ]
    ].copy()

    if include_latest:
        return df, latest_features[["Date", "Symbol", "Close"] + FEATURE_COLUMNS]

    return df




def main():
    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_stocks = []
    failed_stocks = []

    print("Preparing stock dataset...")
    print("-" * 50)

    for symbol, filename in STOCK_FILES.items():
        try:
            print(f"Processing {symbol}...")

            stock_df = prepare_stock_data(
                symbol,
                filename,
            )

            print(
                f"  Rows prepared: {len(stock_df)}"
            )

            all_stocks.append(stock_df)

        except Exception as error:
            print(f"  Failed: {error}")
            failed_stocks.append(symbol)

    if not all_stocks:
        print("\nNo stock data could be prepared.")
        return

    # Combine all stocks into one dataset
    final_df = pd.concat(
        all_stocks,
        ignore_index=True,
    )

    # Sort the combined dataset by date and symbol
    final_df = final_df.sort_values(
        ["Date", "Symbol"]
    ).reset_index(drop=True)

    # Save the prepared dataset
    final_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n" + "=" * 50)
    print("DATASET PREPARATION SUMMARY")
    print(f"Stocks prepared: {len(all_stocks)}/9")
    print(f"Stocks failed: {len(failed_stocks)}")
    print(f"Total rows: {len(final_df)}")
    print(f"Total columns: {len(final_df.columns)}")
    print(f"Output file: {OUTPUT_FILE}")

    print("\nTarget distribution:")
    print(
        final_df["Target"]
        .value_counts()
        .sort_index()
        .rename(index={
            0: "0 = Next close not higher",
            1: "1 = Next close higher",
        })
        .to_string()
    )

    if failed_stocks:
        print(
            "\nStocks with errors:",
            ", ".join(failed_stocks),
        )
    else:
        print("\nAll stocks prepared successfully!")


if __name__ == "__main__":
    main()