import React, { useState } from "react";
import "./App.css";

function App() {
  const [buyingPower, setBuyingPower] = useState("");
  const [portfolioFile, setPortfolioFile] = useState(null);
  const [recommendation, setRecommendation] = useState("");

  const handleFileChange = (e) => {
    setPortfolioFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("buying_power", buyingPower);
    formData.append("portfolio", portfolioFile);

    const response = await fetch("http://localhost:8000/recommend", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    setRecommendation(data);
    console.log(data);
  };

  return (
    <div className="App">
      <h1>Stock Recommendations</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Buying Power:
          <input
            type="number"
            value={buyingPower}
            onChange={(e) => setBuyingPower(e.target.value)}
          />
        </label>
        <br />
        <label>
          Portfolio CSV File:
          <input type="file" accept=".csv" onChange={handleFileChange} />
        </label>
        <br />
        <button type="submit">Get Recommendation</button>
      </form>
      {recommendation && (
        <div>
          <h2>Portfolio Recommendations</h2>
          <h3>Buy:</h3>
          <ul>
            {recommendation.buy.map((rec, idx) => (
              <li key={idx}>
                {rec[2]} shares of {rec[0]} at ${rec[1].toFixed(2)}
              </li>
            ))}
          </ul>
          <h3>Sell:</h3>
          <ul>
            {recommendation.sell.map((rec, idx) => (
              <li key={idx}>
                {rec[1]} shares of {rec[0]}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
