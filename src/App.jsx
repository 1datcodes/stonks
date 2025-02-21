import React, { useState } from 'react'
import './App.css'

function App() {
  const [buyingPower, setBuyingPower] = useState('')
  const [portfolio, setPortfolio] = useState('')
  const [newsQuery, setNewsQuery] = useState('')
  const [recommendation, setRecommendation] = useState("")

  const handleSubmit = async (e) => {
    e.preventDefault()
    const portfolioSymbols = portfolio.split(',').map(sym => sym.trim())
    const portfolioData = {}
    portfolioSymbols.forEach(sym => portfolioData[sym] = true)

    const payload = {
      buying_power: buyingPower,
      portfolio: portfolioData,
      news_query: newsQuery
    }
    console.log(payload)
    const response = await fetch("http://localhost:8000/recommend", {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    const data = await response.json()
    console.log(data)
    setRecommendation(data)
    console.log(data.buy)
    console.log(data.sell)
  }

  return (
    <div className='App'>
      <h1>Stock Recommendations</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Buying Power:
          <input 
            type='number'
            value={buyingPower}
            onChange={e => setBuyingPower(e.target.value)}
          />
        </label>  
        <br />
        <label>
          Portfolio (comma-separated symbols):
          <input
            type='text'
            value={portfolio}
            onChange={e => setPortfolio(e.target.value)}
          />
        </label>
        <br />
        <button type='submit'>Get Recommendation</button>
      </form>
      {recommendation && (
        <div>
          <h2>Recommendations</h2>
          <h3>Buy:</h3>
          <ul>
            {recommendation.buy.map((rec, idx) => (
              <li key={idx}>{rec[0]} at ${rec[2]}</li>
            ))}
          </ul>
          <h3>Sell:</h3>
          <ul>
            {recommendation.sell.map((rec, idx) => (
              <li key={idx}>{rec.stock} at ${rec.price}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
