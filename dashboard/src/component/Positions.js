import React, { useState, useEffect } from "react";

const Positions = () => {
  const [allPositions, setAllPositions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        // Get JWT from Local Storage
        const token = localStorage.getItem("token");

        if (!token) {
          setError("Please log in to view your positions.");
          return;
        }

        // Fetch positions with JWT authentication
        const response = await fetch(
          "http://localhost:3002/allPositions",
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.message || "Failed to fetch positions"
          );
        }

        setAllPositions(data);
      } catch (error) {
        console.error("Positions error:", error);
        setError(error.message || "Unable to fetch positions.");
      }
    };

    fetchPositions();
  }, []);

  return (
    <>
      <h3 className="title">
        Positions ({allPositions.length})
      </h3>

      {error && <p className="error">{error}</p>}

      <div className="order-table">
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Instrument</th>
              <th>Qty.</th>
              <th>Avg.</th>
              <th>LTP</th>
              <th>P&amp;L</th>
              <th>Chg.</th>
            </tr>
          </thead>

          <tbody>
            {allPositions.map((stock, index) => {
              const curValue = stock.price * stock.qty;
              const profit = curValue - stock.avg * stock.qty;

              const profClass = profit >= 0 ? "profit" : "loss";
              const dayClass = stock.isLoss ? "loss" : "profit";

              return (
                <tr key={stock._id || index}>
                  <td>{stock.product}</td>
                  <td>{stock.name}</td>
                  <td>{stock.qty}</td>
                  <td>{stock.avg.toFixed(2)}</td>
                  <td>{stock.price.toFixed(2)}</td>

                  <td className={profClass}>
                    {profit.toFixed(2)}
                  </td>

                  <td className={dayClass}>{stock.day}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
};

export default Positions;