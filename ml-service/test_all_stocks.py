"""Test all nine stocks against the ML service."""
import requests

BASE = "http://127.0.0.1:8000"

STOCKS = ["INFY", "ONGC", "TCS", "KPITTECH", "QUICKHEAL", "WIPRO", "M%26M", "RELIANCE", "HUL"]
NAMES = ["INFY", "ONGC", "TCS", "KPITTECH", "QUICKHEAL", "WIPRO", "M&M", "RELIANCE", "HUL"]

print("=" * 70)
print("NINE-STOCK ML VALIDATION")
print("=" * 70)

# Health check
try:
    r = requests.get(f"{BASE}/health", timeout=10)
    print(f"Health: {r.json()}")
except Exception as e:
    print(f"Health FAILED: {e}")

print()

# Stocks list
try:
    r = requests.get(f"{BASE}/api/stocks", timeout=10)
    print(f"Stocks endpoint: {r.json()}")
except Exception as e:
    print(f"Stocks FAILED: {e}")

print()

# Test each stock
results = []
for url_symbol, display_name in zip(STOCKS, NAMES):
    try:
        r = requests.get(f"{BASE}/api/insights/{url_symbol}", timeout=30)
        if r.status_code == 200:
            d = r.json()
            close = d.get("latestClose", "?")
            date = d.get("predictionDate", "?")
            direction = d.get("direction", "?")
            prob_up = d.get("probabilityUp", 0)
            model = d.get("selectedModel", "?")
            disclaimer = "YES" if d.get("disclaimer") else "NO"
            history_len = len(d.get("history", []))
            indicators = d.get("indicators", {})

            print(f"  {display_name:12} | Close: {close:>10} | Date: {date} | "
                  f"Dir: {direction:>4} | P(UP): {prob_up:.3f} | "
                  f"Model: {model} | History: {history_len} | Disclaimer: {disclaimer}")

            # Validate response structure
            assert d.get("symbol") is not None, "Missing symbol"
            assert d.get("latestClose") is not None, "Missing latestClose"
            assert d.get("predictionDate") is not None, "Missing predictionDate"
            assert d.get("direction") in ("UP", "DOWN"), "Invalid direction"
            assert 0 <= prob_up <= 1, "Invalid probability"
            assert d.get("predictions") is not None, "Missing predictions"
            assert d.get("disclaimer") is not None, "Missing disclaimer"

            results.append((display_name, "PASS"))
        else:
            print(f"  {display_name:12} | ERROR {r.status_code}: {r.text[:80]}")
            results.append((display_name, f"FAIL ({r.status_code})"))
    except Exception as e:
        print(f"  {display_name:12} | EXCEPTION: {e}")
        results.append((display_name, f"FAIL ({e})"))

# Test unsupported symbol
print()
try:
    r = requests.get(f"{BASE}/api/insights/FAKESYMBOL", timeout=10)
    if r.status_code == 404:
        print(f"  Unsupported symbol test: PASS (got 404)")
    else:
        print(f"  Unsupported symbol test: WARN (got {r.status_code})")
except Exception as e:
    print(f"  Unsupported symbol test: FAIL ({e})")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
passed = sum(1 for _, s in results if s == "PASS")
print(f"Passed: {passed}/{len(results)}")
for name, status in results:
    print(f"  {name:12} {status}")
print()
