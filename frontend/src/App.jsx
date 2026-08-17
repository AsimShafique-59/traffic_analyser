import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function fmtHour(h) {
  const suffix = h < 12 ? "am" : "pm";
  const h12 = h % 12 || 12;
  return `${h12}${suffix}`;
}

function BarChart({ hourly, threshold }) {
  const [tableView, setTableView] = useState(false);
  const maxRatio = Math.max(...hourly.map((p) => p.ratio), threshold);
  const scale = (ratio) => `${(Math.max(0, ratio - 1) / (maxRatio - 1)) * 100}%`;
  const thresholdPos = `${(Math.max(0, threshold - 1) / (maxRatio - 1)) * 100}%`;

  if (tableView) {
    return (
      <div className="chart-card">
        <button className="toggle-view" onClick={() => setTableView(false)}>
          Show chart
        </button>
        <table className="hourly-table">
          <thead>
            <tr>
              <th>Hour</th>
              <th>Ratio</th>
              <th>Status</th>
              <th>Weather</th>
            </tr>
          </thead>
          <tbody>
            {hourly.map((p) => (
              <tr key={p.hour}>
                <td>{fmtHour(p.hour)}</td>
                <td>{p.ratio.toFixed(2)}</td>
                <td>{p.congested ? "Congested" : "Normal"}</td>
                <td>{p.weather || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="chart-card">
      <button className="toggle-view" onClick={() => setTableView(true)}>
        Show table
      </button>
      <div className="bar-chart">
        <div className="threshold-line" style={{ bottom: thresholdPos }}>
          <span className="threshold-label">congestion threshold</span>
        </div>
        {hourly.map((p) => (
          <div className="bar-wrap" key={p.hour}>
            <div className="bar-tooltip">
              {fmtHour(p.hour)} — ratio {p.ratio.toFixed(2)} —{" "}
              {p.congested ? "Congested" : "Normal"}
              {p.weather && ` — ${p.weather}`}
            </div>
            <div
              className={`bar ${p.congested ? "bar-congested" : ""}`}
              style={{ height: scale(p.ratio) }}
            />
            <div className="bar-axis-label">{p.hour}</div>
          </div>
        ))}
      </div>
      <p className="chart-caption">
        Bars start at normal (no-traffic) travel time. Red bars cross the
        congestion threshold ({threshold.toFixed(2)}×).
      </p>
    </div>
  );
}

export default function App() {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/api/rush-hours`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ origin, destination }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <h1>Rush Hour Agent</h1>
      <p className="subtitle">
        Enter a route to see predicted traffic congestion by hour.
      </p>

      <form onSubmit={handleSubmit} className="route-form">
        <input
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          placeholder="Origin, e.g. Samanabad, Lahore"
          required
        />
        <input
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder="Destination, e.g. Lahore Ring Road"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Checking traffic…" : "Check rush hours"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section>
          <p className="summary">{result.summary}</p>
          <BarChart hourly={result.hourly} threshold={1.15} />
        </section>
      )}
    </main>
  );
}
