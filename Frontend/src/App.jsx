import React from 'react';
import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';
import './index.css';

function App() {
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  const handleSubmit = async () => {
    if (!topic) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('https://learn-2pj7.onrender.com/api/topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });

      if (!res.ok) {
        throw new Error('Failed to fetch response from backend');
      }

      const data = await res.json();
      console.log('LLM Response:', data);
      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setResult({
        "History": "Could not generate content.",
        "Why & How": "Could not generate content.",
        "Layman Explanation": "Could not generate content.",
        "Beginner Q&A": "Could not generate content.",
        "error": err.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app-container ${darkMode ? 'dark' : 'light'}`}>
      <div className="mobile-frame">
        <div className="header-section">
          <div className="profile-circle"><img src="https://i.ibb.co/6LJH8qH/tanjiro-kamado-red-5120x2880-22577.png" alt="" /></div>
          <h1 className="main-heading">LaymanLearn<span>Story!</span></h1>
          <p className="sub-heading">Understand any Concept</p>
        </div>

        <div className="input-wrapper">
          <input
            type="text"
            className="prompt-input"
            placeholder="Write your topic here..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
          <button onClick={handleSubmit} disabled={loading} className="generate-button">
            {loading ? (
              <span className="loading-text"><Loader2 className="spinner" /> loading...</span>
            ) : (
              'Submit'
            )}
          </button>
        </div>

        <div className="suggestions">
          <p className="section-label">✨ Get inspiration from others</p>
          <div className="filter-buttons">
            <button className="filter-btn active">For You</button>
            <button className="filter-btn">Trending</button>
            <button className="filter-btn">Popular</button>
          </div>
        </div>

        {result && (
          <div className="results">
            {Object.entries(result).map(([section, content]) => (
              <div key={section} className="result-card">
                <h3 className="result-title">{section}</h3>
                <p className="result-content">{typeof content === 'string' ? content : JSON.stringify(content, null, 2)}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
