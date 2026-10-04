# Architecture Audit

## Existing Project Structure

```
Zerodha Clone/
├── frontend/          # React landing page (port 3000)
├── backend/           # Express.js API server (port 3002)
├── dashboard/         # React trading dashboard (port 3001)
├── ml-service/        # Python FastAPI ML prediction service (port 8000)
├── package.json       # Root workspace (MUI dependencies)
└── .gitignore
```

## Component Analysis

### Frontend (React, port 3000)
- **Framework**: React 19 with react-scripts (CRA)
- **Router**: react-router-dom v7
- **Pages**: Home, Signup, About, Products, Pricing, Support, NotFound
- **Components**: Navbar, Footer, landing page sections
- **Status**: ✅ Fully implemented

### Backend (Express.js, port 3002)
- **Framework**: Express 5 with Mongoose 9
- **Database**: MongoDB Atlas (zerodha cluster)
- **Auth**: JWT (jsonwebtoken) + bcryptjs password hashing
- **Models**: Users, Holdings, Positions, Orders
- **Endpoints**:
  - `POST /signup` — user registration
  - `POST /login` — JWT authentication
  - `GET /profile` — authenticated user profile
  - `GET /allHoldings` — authenticated holdings
  - `GET /allPositions` — authenticated positions
  - `POST /newOrder` — create order
  - `GET /api/ml/stocks` — proxy ML stock list
  - `GET /api/ml/insights/:symbol` — proxy ML insights
- **ML Proxy**: Already implemented with `ML_SERVICE_URL` env var
- **Status**: ✅ Fully implemented, ML proxy routes exist

### Dashboard (React, port 3001)
- **Framework**: React 18 with react-scripts (CRA)
- **UI**: Material UI v5, Chart.js, react-chartjs-2
- **Components**: Home, TopBar, Menu, Dashboard, WatchList, Summary, Holdings, Positions, Orders, Funds, Apps, Login, BuyActionWindow
- **Watchlist**: 9 stocks defined in `src/data/data.js`
- **Analytics button**: Present in WatchListActions (BarChartOutlined icon) but NOT wired to any handler
- **Status**: ✅ Mostly implemented, Analytics button needs handler

### ML Service (Python/FastAPI, port 8000)
- **Framework**: FastAPI + Uvicorn
- **Virtual Environment**: `.venv/` exists
- **Data Pipeline**:
  - `download_data.py` — downloads 10y Yahoo Finance data for 9 stocks
  - `prepare_dataset.py` — feature engineering (8 features + target)
  - `train_models.py` — chronological split, Logistic Regression + Random Forest
- **Saved Models**: `logistic_regression.joblib`, `random_forest.joblib` (exist)
- **Raw Data**: CSVs for all 9 stocks (exist)
- **Processed Data**: `stock_features.csv` (exists)
- **API Endpoints**:
  - `GET /health`
  - `GET /api/stocks`
  - `GET /api/insights/{symbol}` — includes latest inference row logic
- **Status**: ✅ Largely implemented

## Nine Stocks

| Symbol | Yahoo Ticker | Raw CSV | In Watchlist | In ML |
|--------|-------------|---------|--------------|-------|
| INFY | INFY.NS | ✅ | ✅ | ✅ |
| ONGC | ONGC.NS | ✅ | ✅ | ✅ |
| TCS | TCS.NS | ✅ | ✅ | ✅ |
| KPITTECH | KPITTECH.NS | ✅ | ✅ | ✅ |
| QUICKHEAL | QUICKHEAL.NS | ✅ | ✅ | ✅ |
| WIPRO | WIPRO.NS | ✅ | ✅ | ✅ |
| M&M | M&M.NS | ✅ | ✅ | ✅ |
| RELIANCE | RELIANCE.NS | ✅ | ✅ | ✅ |
| HUL | HINDUNILVR.NS | ✅ | ✅ | ✅ |

## Issues Found

### WatchList.js — Duplicate Import
- `useEffect` is imported twice (line 1 and line 9) — will cause a build error
- Several imports (Dialog, DialogTitle, DialogContent, CircularProgress, CloseIcon, Line, ChartJS registrations) are present but the Analytics dialog is not implemented

### WatchList.js — Analytics Button Not Wired
- The BarChartOutlined button exists but has no `onClick` handler
- No Analytics dialog/modal component exists yet

### prepare_dataset.py — Dead Code After Return
- Lines 209-211 contain unreachable code after `return df` on line 207

### ML Service — `predictionDate` vs Freshness
- The `predictionDate` field currently returns the date of the latest raw data row, which is the "as of" date rather than the predicted next trading day
- This is acceptable as the SRS asks for the prediction date to be exposed

### Security — .env Contains Real Credentials
- `backend/.env` contains actual MongoDB credentials and JWT secret
- These should be in `.env.example` with placeholder values
- The existing `.env` will be preserved but not committed

## Changes Required

1. **Fix WatchList.js** — Remove duplicate `useEffect` import, implement Analytics dialog
2. **Add Analytics Dialog** — New component showing ML predictions when Analytics button is clicked
3. **Fix prepare_dataset.py** — Remove dead code after return
4. **Create run.py** — Master launcher for all services
5. **Create .env.example** — Backend environment template (without secrets)
6. **Update documentation** — README.md, ML_ARCHITECTURE.md
