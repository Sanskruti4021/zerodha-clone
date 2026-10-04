# Zerodha Clone — Stock Prediction Platform

A full-stack web application inspired by [Zerodha](https://zerodha.com/) with integrated ML-based stock prediction. The platform combines a React frontend, React dashboard, Express.js backend, MongoDB database, and a Python FastAPI ML service for next-day stock direction predictions.

## Project Structure

```
Zerodha Clone/
├── frontend/          # React landing page (port 3000)
├── backend/           # Express.js API + auth (port 3002)
├── dashboard/         # React trading dashboard (port 3001)
├── ml-service/        # Python FastAPI ML service (port 8000)
│   ├── src/
│   │   ├── app.py              # FastAPI server
│   │   ├── download_data.py    # Yahoo Finance data download
│   │   ├── prepare_dataset.py  # Feature engineering
│   │   ├── train_models.py     # Model training
│   │   └── check_environment.py
│   ├── data/
│   │   ├── raw/                # Raw OHLCV CSVs
│   │   └── processed/         # Feature-engineered dataset
│   ├── models/                 # Saved trained models
│   └── results/                # Evaluation metrics
├── docs/
│   ├── ARCHITECTURE_AUDIT.md   # Architecture analysis
│   ├── ML_ARCHITECTURE.md      # ML pipeline documentation
│   └── Stock_Prediction_Platform_SRS.md
├── run.py                      # Master launcher
└── README.md
```

## Prerequisites

- **Node.js** v18+ and npm
- **Python** 3.11+ (3.14 recommended)
- **MongoDB** (Atlas or local instance)
- **Git**

## Quick Start

### 1. Clone and Install

```bash
# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend && npm install && cd ..

# Install dashboard dependencies
cd dashboard && npm install && cd ..

# Set up ML service virtual environment
cd ml-service
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
# source .venv/bin/activate

pip install -r requirements.txt
cd ..
```

### 2. Configure Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your MongoDB URL and JWT secret
```

Required backend variables:
| Variable | Description |
|----------|-------------|
| `MONGO_URL` | MongoDB connection string |
| `JWT_SECRET` | JWT signing secret (random string) |
| `PORT` | Express server port (default: 3002) |
| `ML_SERVICE_URL` | ML service URL (default: http://127.0.0.1:8000) |

### 3. ML Setup (First Time Only)

```bash
cd ml-service

# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Download historical data (~10 years from Yahoo Finance)
python src/download_data.py

# Prepare features
python src/prepare_dataset.py

# Train models
python src/train_models.py

cd ..
```

### 4. Start Everything

```bash
python run.py
```

This starts all four services:

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Dashboard | 3001 | http://localhost:3001 |
| Backend | 3002 | http://localhost:3002 |
| ML Service | 8000 | http://localhost:8000 |

Press **Ctrl+C** to shut down all services.

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Landing page with navigation, signup |
| Dashboard | 3001 | Trading dashboard with watchlist, analytics |
| Backend API | 3002 | REST API, auth, ML proxy |
| ML Service | 8000 | FastAPI predictions |

## Starting Services Individually

```bash
# ML Service
cd ml-service
.venv\Scripts\activate
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000

# Backend
cd backend
npm start

# Dashboard
cd dashboard
set PORT=3001 && npm start

# Frontend
cd frontend
npm start
```

## How ML Works

1. **Data**: ~10 years of daily OHLCV data from Yahoo Finance for 9 Indian stocks
2. **Features**: 8 technical indicators (returns, moving averages, RSI, volatility, volume ratio)
3. **Target**: Binary — will next trading day's close be higher? (1=UP, 0=DOWN)
4. **Models**: Logistic Regression (with StandardScaler) and Random Forest
5. **Split**: Chronological 80/20 — no random shuffling of time-series data
6. **Inference**: Uses the latest available raw data row to predict next-day direction

## How Analytics Works

1. User hovers over a stock in the Dashboard watchlist
2. Clicks the **Analytics** button (bar chart icon)
3. A dialog opens showing loading state
4. Dashboard requests `GET /api/ml/insights/:symbol` from the backend (authenticated)
5. Backend proxies to the ML service `GET /api/insights/{symbol}`
6. ML service loads the latest raw data, computes features, runs prediction
7. Result displays: direction, probabilities, indicators, historical chart, disclaimer

## Supported Stocks

| # | Symbol | Yahoo Ticker |
|---|--------|-------------|
| 1 | INFY | INFY.NS |
| 2 | ONGC | ONGC.NS |
| 3 | TCS | TCS.NS |
| 4 | KPITTECH | KPITTECH.NS |
| 5 | QUICKHEAL | QUICKHEAL.NS |
| 6 | WIPRO | WIPRO.NS |
| 7 | M&M | M&M.NS |
| 8 | RELIANCE | RELIANCE.NS |
| 9 | HUL | HINDUNILVR.NS |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/login` | Login, receive JWT |
| GET | `/profile` | Get user profile (auth) |

### Trading
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/allHoldings` | Get holdings (auth) |
| GET | `/allPositions` | Get positions (auth) |
| POST | `/newOrder` | Create new order |

### ML Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ml/stocks` | List supported stocks (auth) |
| GET | `/api/ml/insights/:symbol` | Get prediction (auth) |

### ML Service (Internal)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/stocks` | List stocks |
| GET | `/api/insights/{symbol}` | Full prediction |

## Testing

### ML Service
```bash
# Health check
curl http://localhost:8000/health

# List stocks
curl http://localhost:8000/api/stocks

# Get prediction for INFY
curl http://localhost:8000/api/insights/INFY
```

### Backend (requires JWT token)
```bash
# Login first
curl -X POST http://localhost:3002/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# Use returned token
curl http://localhost:3002/api/ml/insights/INFY \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ML service won't start | Check virtual environment is activated and dependencies installed |
| Models not found | Run `python src/train_models.py` in ml-service |
| Backend won't connect to DB | Check `MONGO_URL` in `backend/.env` |
| Dashboard shows "Unable to connect" | Ensure backend and ML service are running |
| Port already in use | Kill the process using the port or change the port |

## ML Limitations

- Model accuracy is close to baseline (~49-50%) — typical for short-term stock prediction
- Does not account for news, earnings, or macro events
- Historical data may have delays or gaps
- No automatic retraining pipeline
- **Predictions are for educational purposes only and are NOT financial advice**

## Documentation

- [Architecture Audit](docs/ARCHITECTURE_AUDIT.md)
- [ML Architecture](docs/ML_ARCHITECTURE.md)
- [SRS Document](docs/Stock_Prediction_Platform_SRS.md)
