import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";

const RANGES = ["1M", "3M", "6M", "1Y", "5Y"];

export default function PriceChart({ instrument, isLme }) {
  const [range, setRange] = useState("6M");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError(null);
    api
      .getHistory(instrument, range)
      .then((res) => {
        if (cancelled) return;
        const points = res.points.map((p) => ({
          date: new Date(p.as_of).toLocaleDateString(),
          price: p.price,
          inr_per_kg: p.inr_per_kg,
        }));
        setData(points);
      })
      .catch((e) => !cancelled && setError(e));
    return () => {
      cancelled = true;
    };
  }, [instrument, range]);

  return (
    <div className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <div className="dim" style={{ fontWeight: 600 }}>Historical price {isLme ? "(USD/tonne)" : ""}</div>
        <div style={{ display: "flex", gap: 4 }}>
          {RANGES.map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              style={{
                background: r === range ? "var(--accent)" : "var(--bg-panel-alt)",
                color: r === range ? "#08111c" : "var(--text-dim)",
                border: "1px solid var(--border)",
                borderRadius: 6,
                padding: "4px 10px",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="dim">Could not load history: {String(error.message || error)}</div>}
      {!error && !data && <div className="dim">Loading chart…</div>}
      {!error && data && data.length === 0 && <div className="dim">No history in this range yet.</div>}
      {!error && data && data.length > 0 && (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fill: "var(--text-faint)", fontSize: 11 }} minTickGap={40} />
            <YAxis yAxisId="left" tick={{ fill: "var(--text-faint)", fontSize: 11 }} domain={["auto", "auto"]} />
            {isLme && <YAxis yAxisId="right" orientation="right" tick={{ fill: "var(--text-faint)", fontSize: 11 }} domain={["auto", "auto"]} />}
            <Tooltip contentStyle={{ background: "var(--bg-panel-alt)", border: "1px solid var(--border)", borderRadius: 8 }} />
            <Line yAxisId="left" type="monotone" dataKey="price" name={isLme ? "USD/tonne" : "price"} stroke="var(--accent)" dot={false} strokeWidth={2} />
            {isLme && (
              <Line yAxisId="right" type="monotone" dataKey="inr_per_kg" name="INR/kg" stroke="var(--bullish)" dot={false} strokeWidth={1.5} strokeDasharray="4 3" />
            )}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
