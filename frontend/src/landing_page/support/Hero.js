import React from "react";

function Hero() {
  return (
    <section
      className="container-fluid"
      id="supportHero"
      style={{
        backgroundColor: "#387ed1",
        color: "white",
        minHeight: "400px",
      }}
    >
      <div
        className="p-5"
        id="supportWrapper"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          maxWidth: "950px",
          margin: "0 auto",
        }}
      >
        <h4>Support Portal</h4>

        <a href="" style={{ color: "white" }}>
          Track Tickets
        </a>
      </div>

      <div
        className="row p-5"
        style={{
          maxWidth: "950px",
          margin: "0 auto",
        }}
      >
        <div className="col-md-6 p-3">
          <h1 className="fs-3 mb-3">
            Search for an answer or browse help topics
            to create a ticket
          </h1>

          <input
            type="text"
            placeholder="Eg: how do I activate F&O, why is my order getting rejected..."
            className="form-control p-3 mb-3"
            style={{
              width: "100%",
              maxWidth: "500px",
              height: "65px",
            }}
          />

          <div className="d-flex flex-wrap gap-3">
            <a href="" style={{ color: "white" }}>
              Track account opening
            </a>

            <a href="" style={{ color: "white" }}>
              Track segment activation
            </a>

            <a href="" style={{ color: "white" }}>
              Intraday margins
            </a>

            <a href="" style={{ color: "white" }}>
              Kite user manual
            </a>
          </div>
        </div>

        <div className="col-md-6 p-3">
          <h1 className="fs-3 mb-3">Featured</h1>

          <ol>
            <li className="mb-3">
              <a href="" style={{ color: "white" }}>
                Current Takeovers and Delisting - January 2024
              </a>
            </li>

            <li>
              <a href="" style={{ color: "white" }}>
                Latest Intraday leverages - MIS & CO
              </a>
            </li>
          </ol>
        </div>
      </div>
    </section>
  );
}

export default Hero;