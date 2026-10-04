import React, { useState, useContext } from "react";

import axios from "axios";

import GeneralContext from "./GeneralContext";

import { Tooltip, Grow } from "@mui/material";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  CircularProgress,
  IconButton,
} from "@mui/material";

import CloseIcon from "@mui/icons-material/Close";
import { Line } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip as ChartTooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ChartTooltip,
  Legend
);

import {
  BarChartOutlined,
  KeyboardArrowDown,
  KeyboardArrowUp,
  MoreHoriz,
} from "@mui/icons-material";

import { watchlist } from "../data/data";
import { DoughnutChart } from "./DoughnoutChart";

const labels = watchlist.map((subArray) => subArray["name"]);

const WatchList = () => {
  const data = {
    labels,
    datasets: [
      {
        label: "Price",
        data: watchlist.map((stock) => stock.price),
        backgroundColor: [
          "rgba(255, 99, 132, 0.5)",
          "rgba(54, 162, 235, 0.5)",
          "rgba(255, 206, 86, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(153, 102, 255, 0.5)",
          "rgba(255, 159, 64, 0.5)",
        ],
        borderColor: [
          "rgba(255, 99, 132, 1)",
          "rgba(54, 162, 235, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(75, 192, 192, 1)",
          "rgba(153, 102, 255, 1)",
          "rgba(255, 159, 64, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="watchlist-container">
      <div className="search-container">
        <input
          type="text"
          name="search"
          id="search"
          placeholder="Search eg:infy, bse, nifty fut weekly, gold mcx"
          className="search"
        />
        <span className="counts"> {watchlist.length} / 50</span>
      </div>

      <ul className="list">
        {watchlist.map((stock, index) => {
          return <WatchListItem stock={stock} key={index} />;
        })}
      </ul>

      <DoughnutChart data={data} />
    </div>
  );
};

export default WatchList;

const WatchListItem = ({ stock }) => {
  const [showWatchlistActions, setShowWatchlistActions] = useState(false);

  const handleMouseEnter = (e) => {
    setShowWatchlistActions(true);
  };

  const handleMouseLeave = (e) => {
    setShowWatchlistActions(false);
  };

  return (
    <li onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
      <div className="item">
        <p className={stock.isDown ? "down" : "up"}>{stock.name}</p>
        <div className="itemInfo">
          <span className="percent">{stock.percent}</span>
          {stock.isDown ? (
            <KeyboardArrowDown className="down" />
          ) : (
            <KeyboardArrowUp className="down" />
          )}
          <span className="price">{stock.price}</span>
        </div>
      </div>
      {showWatchlistActions && <WatchListActions uid={stock.name} />}
    </li>
  );
};

const WatchListActions = ({ uid }) => {
  const generalContext = useContext(GeneralContext);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);

  const handleBuyClick = () => {
    generalContext.openBuyWindow(uid);
  };

  const handleAnalyticsClick = () => {
    setAnalyticsOpen(true);
  };

  const handleAnalyticsClose = () => {
    setAnalyticsOpen(false);
  };

  return (
    <span className="actions">
      <span>
        <Tooltip
          title="Buy (B)"
          placement="top"
          arrow
          TransitionComponent={Grow}
          onClick={handleBuyClick}
        >
          <button className="buy">Buy</button>
        </Tooltip>
        <Tooltip
          title="Sell (S)"
          placement="top"
          arrow
          TransitionComponent={Grow}
        >
          <button className="sell">Sell</button>
        </Tooltip>
        <Tooltip
          title="Analytics (A)"
          placement="top"
          arrow
          TransitionComponent={Grow}
        >
          <button className="action" onClick={handleAnalyticsClick}>
            <BarChartOutlined className="icon" />
          </button>
        </Tooltip>
        <Tooltip title="More" placement="top" arrow TransitionComponent={Grow}>
          <button className="action">
            <MoreHoriz className="icon" />
          </button>
        </Tooltip>
      </span>

      {analyticsOpen && (
        <AnalyticsDialog
          symbol={uid}
          open={analyticsOpen}
          onClose={handleAnalyticsClose}
        />
      )}
    </span>
  );
};

// ─── ML Analytics Dialog ────────────────────────────────────

const SUPPORTED_SYMBOLS = [
  "INFY", "ONGC", "TCS", "KPITTECH", "QUICKHEAL",
  "WIPRO", "M&M", "RELIANCE", "HUL",
];

const AnalyticsDialog = ({ symbol, open, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState(null);

  React.useEffect(() => {
    if (!open) return;

    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      setInsights(null);

      if (!SUPPORTED_SYMBOLS.includes(symbol)) {
        setError(`"${symbol}" is not supported for ML predictions.`);
        setLoading(false);
        return;
      }

      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          `http://localhost:3002/api/ml/insights/${encodeURIComponent(symbol)}`,
          {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            timeout: 30000,
          }
        );
        setInsights(response.data);
      } catch (err) {
        if (err.response) {
          setError(
            err.response.data?.message ||
            `ML service error (${err.response.status})`
          );
        } else if (err.code === "ECONNABORTED") {
          setError("Request timed out. Please try again.");
        } else {
          setError("Unable to connect to the prediction service.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [open, symbol]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        style: {
          borderRadius: 12,
          padding: 0,
          maxHeight: "85vh",
        },
      }}
    >
      <DialogTitle
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "#1a1a2e",
          color: "#fff",
          padding: "14px 20px",
          fontSize: "1rem",
          fontWeight: 600,
          letterSpacing: 0.5,
        }}
      >
        <span>ANALYTICS — {symbol}</span>
        <IconButton onClick={onClose} size="small" style={{ color: "#fff" }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent
        style={{
          padding: "20px",
          background: "#f9f9fb",
          overflowY: "auto",
        }}
      >
        {loading && (
          <div style={{ textAlign: "center", padding: "40px 0" }}>
            <CircularProgress size={36} style={{ color: "#4184f3" }} />
            <p style={{ marginTop: 14, color: "#888", fontSize: "0.85rem" }}>
              Fetching prediction for {symbol}…
            </p>
          </div>
        )}

        {error && !loading && (
          <div
            style={{
              textAlign: "center",
              padding: "30px 10px",
              color: "#d32f2f",
            }}
          >
            <p style={{ fontSize: "0.95rem", fontWeight: 500 }}>
              Unable to load prediction
            </p>
            <p style={{ fontSize: "0.8rem", marginTop: 6, color: "#888" }}>
              {error}
            </p>
          </div>
        )}

        {insights && !loading && !error && (
          <AnalyticsContent insights={insights} />
        )}
      </DialogContent>
    </Dialog>
  );
};

// ─── Analytics Content ──────────────────────────────────────

const AnalyticsContent = ({ insights }) => {
  const isUp = insights.direction === "UP";
  const probUp = (insights.probabilityUp * 100).toFixed(1);
  const probDown = (insights.probabilityDown * 100).toFixed(1);

  // Build chart data from history
  const chartLabels = (insights.history || []).map((h) => h.date);
  const chartClose = (insights.history || []).map((h) => h.close);
  const chartMA20 = (insights.history || []).map((h) => h.ma20);
  const chartMA50 = (insights.history || []).map((h) => h.ma50);

  const chartData = {
    labels: chartLabels,
    datasets: [
      {
        label: "Close",
        data: chartClose,
        borderColor: "#4184f3",
        backgroundColor: "rgba(65,132,243,0.08)",
        borderWidth: 1.8,
        pointRadius: 0,
        tension: 0.3,
        fill: true,
      },
      {
        label: "MA20",
        data: chartMA20,
        borderColor: "#f59e0b",
        borderWidth: 1.2,
        borderDash: [4, 3],
        pointRadius: 0,
        tension: 0.3,
        fill: false,
      },
      {
        label: "MA50",
        data: chartMA50,
        borderColor: "#ef4444",
        borderWidth: 1.2,
        borderDash: [6, 3],
        pointRadius: 0,
        tension: 0.3,
        fill: false,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
        labels: { font: { size: 10 }, boxWidth: 14 },
      },
    },
    scales: {
      x: {
        display: true,
        ticks: {
          maxTicksLimit: 6,
          font: { size: 9 },
          color: "#999",
        },
        grid: { display: false },
      },
      y: {
        display: true,
        ticks: { font: { size: 9 }, color: "#999" },
        grid: { color: "#eee" },
      },
    },
  };

  const sectionStyle = {
    marginBottom: 16,
    padding: "14px 16px",
    background: "#fff",
    borderRadius: 8,
    border: "1px solid #eee",
  };

  const labelStyle = {
    fontSize: "0.7rem",
    color: "#999",
    textTransform: "uppercase",
    letterSpacing: 0.8,
    marginBottom: 4,
  };

  const valueStyle = {
    fontSize: "1.1rem",
    fontWeight: 600,
    color: "#333",
  };

  return (
    <div>
      {/* Price and date */}
      <div style={sectionStyle}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div>
            <p style={labelStyle}>Latest Close</p>
            <p style={valueStyle}>
              ₹{insights.latestClose?.toLocaleString("en-IN") ?? "—"}
            </p>
          </div>
          <div style={{ textAlign: "right" }}>
            <p style={labelStyle}>Prediction Date</p>
            <p style={{ ...valueStyle, fontSize: "0.95rem" }}>
              {insights.predictionDate ?? "—"}
            </p>
          </div>
        </div>
      </div>

      {/* Direction */}
      <div
        style={{
          ...sectionStyle,
          textAlign: "center",
          background: isUp ? "#e8f5e9" : "#fce4ec",
          border: isUp ? "1px solid #a5d6a7" : "1px solid #ef9a9a",
        }}
      >
        <p style={{ ...labelStyle, marginBottom: 6 }}>Prediction</p>
        <p
          style={{
            fontSize: "1.8rem",
            fontWeight: 700,
            color: isUp ? "#2e7d32" : "#c62828",
            margin: 0,
          }}
        >
          {isUp ? "▲ UP" : "▼ DOWN"}
        </p>
      </div>

      {/* Probabilities */}
      <div style={sectionStyle}>
        <p style={{ ...labelStyle, marginBottom: 10 }}>Probability</p>
        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <div style={{ textAlign: "center" }}>
            <p style={{ fontSize: "1.3rem", fontWeight: 600, color: "#2e7d32" }}>
              {probUp}%
            </p>
            <p style={{ fontSize: "0.75rem", color: "#888" }}>UP</p>
          </div>
          <div
            style={{
              width: 1,
              background: "#e0e0e0",
              margin: "0 10px",
            }}
          />
          <div style={{ textAlign: "center" }}>
            <p style={{ fontSize: "1.3rem", fontWeight: 600, color: "#c62828" }}>
              {probDown}%
            </p>
            <p style={{ fontSize: "0.75rem", color: "#888" }}>DOWN</p>
          </div>
        </div>
      </div>

      {/* Model */}
      <div style={sectionStyle}>
        <p style={labelStyle}>Model</p>
        <p style={{ ...valueStyle, fontSize: "0.95rem" }}>
          {insights.selectedModel ?? "—"}
        </p>
      </div>

      {/* Indicators */}
      {insights.indicators && (
        <div style={sectionStyle}>
          <p style={{ ...labelStyle, marginBottom: 10 }}>Key Indicators</p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "8px 16px",
            }}
          >
            {insights.indicators.rsi14 != null && (
              <div>
                <p style={{ fontSize: "0.7rem", color: "#aaa" }}>RSI (14)</p>
                <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                  {insights.indicators.rsi14.toFixed(2)}
                </p>
              </div>
            )}
            {insights.indicators.ma20 != null && (
              <div>
                <p style={{ fontSize: "0.7rem", color: "#aaa" }}>MA20</p>
                <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                  ₹{insights.indicators.ma20.toFixed(2)}
                </p>
              </div>
            )}
            {insights.indicators.ma50 != null && (
              <div>
                <p style={{ fontSize: "0.7rem", color: "#aaa" }}>MA50</p>
                <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                  ₹{insights.indicators.ma50.toFixed(2)}
                </p>
              </div>
            )}
            {insights.indicators.volatility20d != null && (
              <div>
                <p style={{ fontSize: "0.7rem", color: "#aaa" }}>
                  Volatility (20D)
                </p>
                <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                  {(insights.indicators.volatility20d * 100).toFixed(2)}%
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Historical Chart */}
      {insights.history && insights.history.length > 0 && (
        <div style={{ ...sectionStyle, padding: "14px 10px" }}>
          <p style={{ ...labelStyle, marginBottom: 10, paddingLeft: 6 }}>
            Historical Chart (≈120 sessions)
          </p>
          <div style={{ height: 200 }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}

      {/* Both model comparisons */}
      {insights.predictions && (
        <div style={sectionStyle}>
          <p style={{ ...labelStyle, marginBottom: 10 }}>Model Comparison</p>
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: "0.7rem", color: "#aaa", marginBottom: 4 }}>
                Logistic Regression
              </p>
              <p style={{ fontSize: "1rem", fontWeight: 600, color: "#2e7d32" }}>
                ↑{" "}
                {(
                  insights.predictions.logisticRegression.probabilityUp * 100
                ).toFixed(1)}
                %
              </p>
              <p style={{ fontSize: "0.85rem", color: "#c62828" }}>
                ↓{" "}
                {(
                  insights.predictions.logisticRegression.probabilityDown * 100
                ).toFixed(1)}
                %
              </p>
            </div>
            <div
              style={{
                width: 1,
                background: "#e0e0e0",
                margin: "0 10px",
              }}
            />
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: "0.7rem", color: "#aaa", marginBottom: 4 }}>
                Random Forest
              </p>
              <p style={{ fontSize: "1rem", fontWeight: 600, color: "#2e7d32" }}>
                ↑{" "}
                {(
                  insights.predictions.randomForest.probabilityUp * 100
                ).toFixed(1)}
                %
              </p>
              <p style={{ fontSize: "0.85rem", color: "#c62828" }}>
                ↓{" "}
                {(
                  insights.predictions.randomForest.probabilityDown * 100
                ).toFixed(1)}
                %
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div
        style={{
          padding: "10px 14px",
          background: "#fff8e1",
          borderRadius: 6,
          border: "1px solid #ffe082",
          marginTop: 8,
        }}
      >
        <p
          style={{
            fontSize: "0.7rem",
            color: "#6d4c00",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          ⚠️ {insights.disclaimer ||
            "Predictions are for informational and educational purposes only " +
            "and are NOT financial advice. Past performance does not guarantee " +
            "future results."}
        </p>
      </div>
    </div>
  );
};
