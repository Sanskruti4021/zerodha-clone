from pathlib import Path

import yfinance as yf


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Yahoo Finance ticker : CSV filename
STOCKS = {
    "INFY.NS": "INFY.csv",
    "ONGC.NS": "ONGC.csv",
    "TCS.NS": "TCS.csv",
    "KPITTECH.NS": "KPITTECH.csv",
    "QUICKHEAL.NS": "QUICKHEAL.csv",
    "WIPRO.NS": "WIPRO.csv",
    "M&M.NS": "M&M.csv",
    "RELIANCE.NS": "RELIANCE.csv",
    "HINDUNILVR.NS": "HUL.csv",
}

REQUIRED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def main():
    # Create the folder if it does not exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading historical stock data...")
    print("Period: Approximately 10 years")
    print("-" * 45)

    successful = 0
    failed = []

    for ticker, filename in STOCKS.items():
        try:
            print(f"Downloading {ticker}...")

            # Use adjusted prices for consistent historical analysis.
            # auto_adjust=True adjusts OHLC prices for corporate actions.
            data = yf.download(
                ticker,
                period="10y",
                interval="1d",
                auto_adjust=True,
                progress=False,
                multi_level_index=False,
            )

            if data.empty:
                raise ValueError("No historical data was returned.")

            # Handle MultiIndex columns if returned by yfinance
            if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:
                data.columns = data.columns.get_level_values(0)

            # Check that all required columns exist
            missing = [
                column
                for column in REQUIRED_COLUMNS
                if column not in data.columns
            ]

            if missing:
                raise ValueError(f"Missing columns: {missing}")

            # Keep only the required columns
            data = data[REQUIRED_COLUMNS].copy()

            # Move the trading date from the index into a column
            data.index.name = "Date"
            data = data.reset_index()

            # Save the CSV
            output_path = DATA_DIR / filename
            data.to_csv(output_path, index=False)

            print(f"Saved {filename} ({len(data)} rows)")
            successful += 1

        except Exception as error:
            print(f"Failed: {ticker} - {error}")
            failed.append(ticker)

    print("\n" + "=" * 45)
    print("DOWNLOAD SUMMARY")
    print(f"Successful: {successful}/{len(STOCKS)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("Failed tickers:", ", ".join(failed))
    else:
        print("All stocks downloaded successfully!")

    print(f"\nCSV files are saved in:\n{DATA_DIR}")


if __name__ == "__main__":
    main()