"""Environment check for the ML service.

Run from the ml-service folder:
    python src/check_environment.py
"""

import importlib
import platform
import sys
from importlib.metadata import PackageNotFoundError, version

# (import name, package name on PyPI)
PACKAGES = [
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("sklearn", "scikit-learn"),
    ("joblib", "joblib"),
    ("yfinance", "yfinance"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("dotenv", "python-dotenv"),
    ("pytest", "pytest"),
]


def check_imports():
    """Import every package and print its version. Returns the failures."""
    failures = []
    for import_name, package_name in PACKAGES:
        try:
            importlib.import_module(import_name)
            try:
                found = version(package_name)
            except PackageNotFoundError:
                found = "installed (version unknown)"
            print(f"  {package_name:<14} {found}")
        except Exception as error:  # broad on purpose: show any import problem
            failures.append(package_name)
            print(f"  {package_name:<14} FAILED -> {error}")
    return failures


def smoke_test():
    """Train a tiny model on random data to prove the ML stack works."""
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression

    rng = np.random.default_rng(42)
    features = pd.DataFrame(rng.normal(size=(200, 3)), columns=["a", "b", "c"])
    labels = (features["a"] + rng.normal(scale=0.5, size=200) > 0).astype(int)

    model = LogisticRegression().fit(features, labels)
    print(f"  Accuracy on random practice data: {model.score(features, labels):.2f}")


def main():
    print(f"Python {sys.version.split()[0]} on {platform.system()} {platform.machine()}")
    print("\nChecking packages:")
    failures = check_imports()

    if failures:
        print(f"\nProblem: could not import {', '.join(failures)}.")
        return 1

    print("\nSmoke test:")
    smoke_test()
    print("\nEnvironment looks good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
