import React from "react";
import Menu from "./Menu";

const TopBar = () => {
  const handleLogout = () => {
    // Remove the saved login token
    localStorage.removeItem("token");

    // Redirect to the login page
    window.location.href = "/apps";
  };

  return (
    <div className="topbar-container">
      <div className="indices-container">
        <div className="nifty">
          <p className="index">NIFTY 50</p>
          <p className="index-points">{100.2}</p>
          <p className="percent"></p>
        </div>

        <div className="sensex">
          <p className="index">SENSEX</p>
          <p className="index-points">{100.2}</p>
          <p className="percent"></p>
        </div>
      </div>

      <Menu />

      <button
        onClick={handleLogout}
        style={{
          marginLeft: "20px",
          padding: "8px 16px",
          backgroundColor: "#ff4b4b",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Logout
      </button>
    </div>
  );
};

export default TopBar;