from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# 1. PROJECT PATHS AND SETTINGS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stock_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"

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

TARGET_COLUMN = "Target"

TEST_SIZE = 0.20
RANDOM_STATE = 42


# --------------------------------------------------
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_dataset():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"])

    required_columns = (
        ["Date", "Symbol", "Return_1D", TARGET_COLUMN]
        + FEATURE_COLUMNS
    )

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = df.dropna(
        subset=FEATURE_COLUMNS + [TARGET_COLUMN]
    )

    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)

    df = df.sort_values(
        ["Date", "Symbol"]
    ).reset_index(drop=True)

    if df[TARGET_COLUMN].nunique() != 2:
        raise ValueError(
            "The dataset must contain both target classes, 0 and 1."
        )

    return df


# --------------------------------------------------
# 3. CHRONOLOGICAL TRAIN / TEST SPLIT
# --------------------------------------------------

def chronological_split(df):
    unique_dates = sorted(df["Date"].unique())

    if len(unique_dates) < 10:
        raise ValueError(
            "Not enough unique dates for a reliable split."
        )

    split_index = int(
        len(unique_dates) * (1 - TEST_SIZE)
    )

    # Leave one complete date out as a gap
    train_dates = unique_dates[:split_index]
    test_dates = unique_dates[split_index + 1:]

    if not train_dates or not test_dates:
        raise ValueError(
            "The train/test split produced an empty set."
        )

    train_df = df[
        df["Date"].isin(train_dates)
    ].copy()

    test_df = df[
        df["Date"].isin(test_dates)
    ].copy()

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    print("\nCHRONOLOGICAL SPLIT")
    print("-" * 50)
    print(f"Training rows: {len(train_df)}")
    print(f"Testing rows:  {len(test_df)}")
    print(
        f"Training dates: {train_df['Date'].min().date()} "
        f"to {train_df['Date'].max().date()}"
    )
    print(
        f"Testing dates:  {test_df['Date'].min().date()} "
        f"to {test_df['Date'].max().date()}"
    )
    print("One date excluded between training and testing.")

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        train_df,
        test_df,
    )


# --------------------------------------------------
# 4. EVALUATE A MODEL
# --------------------------------------------------

def evaluate_model(name, y_true, y_pred):
    metrics = {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "precision": float(
            precision_score(
                y_true, y_pred, zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                y_true, y_pred, zero_division=0
            )
        ),
        "f1_score": float(
            f1_score(
                y_true, y_pred, zero_division=0
            )
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
            labels=[0, 1],
        ).tolist(),
    }

    print(f"\n{name}")
    print("-" * 50)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1-score:  {metrics['f1_score']:.4f}")
    print("Confusion matrix [[TN, FP], [FN, TP]]:")
    print(metrics["confusion_matrix"])

    return metrics


# --------------------------------------------------
# 5. TRAIN MODELS AND BASELINES
# --------------------------------------------------

def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading prepared dataset...")
    df = load_dataset()

    print(f"Dataset rows: {len(df)}")
    print(f"Stocks: {df['Symbol'].nunique()}")
    print(f"Features: {len(FEATURE_COLUMNS)}")

    (
        X_train,
        X_test,
        y_train,
        y_test,
        train_df,
        test_df,
    ) = chronological_split(df)

    results = {}

    # ----------------------------------------------
    # Baseline 1: Always predict the training majority
    # ----------------------------------------------

    majority_class = int(
        y_train.value_counts().idxmax()
    )

    majority_predictions = [
        majority_class
    ] * len(y_test)

    results["Majority Class Baseline"] = evaluate_model(
        "Majority Class Baseline",
        y_test,
        majority_predictions,
    )

    # ----------------------------------------------
    # Baseline 2: Repeat today's price direction
    # ----------------------------------------------

    repeat_predictions = (
        X_test["Return_1D"] > 0
    ).astype(int)

    results["Repeat Today's Direction"] = evaluate_model(
        "Repeat Today's Direction Baseline",
        y_test,
        repeat_predictions,
    )

    # ----------------------------------------------
    # Model 1: Logistic Regression
    # ----------------------------------------------

    logistic_model = Pipeline([
        ("scaler", StandardScaler()),
        (
            "model",
            LogisticRegression(
                max_iter=2000,
                random_state=RANDOM_STATE,
            ),
        ),
    ])

    print("\nTraining Logistic Regression...")
    logistic_model.fit(X_train, y_train)

    logistic_predictions = logistic_model.predict(X_test)

    results["Logistic Regression"] = evaluate_model(
        "Logistic Regression",
        y_test,
        logistic_predictions,
    )

    # ----------------------------------------------
    # Model 2: Random Forest
    # ----------------------------------------------

    random_forest_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("\nTraining Random Forest...")
    random_forest_model.fit(X_train, y_train)

    rf_predictions = random_forest_model.predict(X_test)

    results["Random Forest"] = evaluate_model(
        "Random Forest",
        y_test,
        rf_predictions,
    )

    # ----------------------------------------------
    # Save trained models
    # ----------------------------------------------

    joblib.dump(
        logistic_model,
        MODEL_DIR / "logistic_regression.joblib",
    )

    joblib.dump(
        random_forest_model,
        MODEL_DIR / "random_forest.joblib",
    )

    # Save feature names for later API use
    with open(
        MODEL_DIR / "feature_columns.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(FEATURE_COLUMNS, file, indent=4)

    # ----------------------------------------------
    # Save metrics
    # ----------------------------------------------

    with open(
        RESULTS_DIR / "metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(results, file, indent=4)

    # ----------------------------------------------
    # Save test predictions
    # ----------------------------------------------

    predictions_df = test_df[
        ["Date", "Symbol", "Close", TARGET_COLUMN]
    ].copy()

    predictions_df = predictions_df.rename(
        columns={TARGET_COLUMN: "Actual"}
    )

    predictions_df["Majority_Baseline"] = (
        majority_predictions
    )

    predictions_df["Repeat_Direction_Baseline"] = (
        repeat_predictions.to_numpy()
    )

    predictions_df["Logistic_Regression"] = (
        logistic_predictions
    )

    predictions_df["Logistic_Probability_Up"] = (
        logistic_model.predict_proba(X_test)[:, 1]
    )

    predictions_df["Random_Forest"] = rf_predictions

    predictions_df["Random_Forest_Probability_Up"] = (
        random_forest_model.predict_proba(X_test)[:, 1]
    )

    predictions_df.to_csv(
        RESULTS_DIR / "test_predictions.csv",
        index=False,
    )

    # ----------------------------------------------
    # Final summary
    # ----------------------------------------------

    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)

    print("\nAccuracy summary:")
    for name, metrics in results.items():
        print(
            f"{name}: {metrics['accuracy']:.4f}"
        )

    print(f"\nModels saved in: {MODEL_DIR}")
    print(f"Metrics saved in: {RESULTS_DIR / 'metrics.json'}")
    print(
        "Predictions saved in: "
        f"{RESULTS_DIR / 'test_predictions.csv'}"
    )

    print(
        "\nNote: These are experimental historical results, "
        "not a guarantee of future performance."
    )


if __name__ == "__main__":
    main()