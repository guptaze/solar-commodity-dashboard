import { useEffect, useState } from "react";
import { api } from "../api";

export default function AlertsPanel({ onAlertsLoaded }) {
  const [alerts, setAlerts] = useState(null);
  const [error, setError] = useState(null);

  const load = () =>
    api
      .getAlerts()
      .then((res) => {
        setAlerts(res);
        onAlertsLoaded && onAlertsLoaded(res);
      })
      .catch(setError);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const save = async (instrument, patch) => {
    const current = alerts.find((a) => a.instrument === instrument);
    await api.updateAlert(instrument, {
      threshold_pct: patch.threshold_pct ?? current.threshold_pct,
      window_days: patch.window_days ?? current.window_days,
      enabled: patch.enabled ?? current.enabled,
    });
    load();
  };

  return (
    <div className="panel">
      <div className="dim" style={{ fontWeight: 600, marginBottom: 4 }}>Threshold alerts</div>
      <div className="faint" style={{ marginBottom: 10 }}>
        Configure a move-size trigger per instrument (e.g. "flag if copper moves &gt;5% in 30 days") to signal a procurement/hedging decision point.
      </div>
      {error && <div className="dim">Could not load: {String(error.message || error)}</div>}
      {!alerts && !error && <div className="dim">Loading…</div>}
      {alerts && (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ textAlign: "left", color: "var(--text-faint)", fontSize: 11, textTransform: "uppercase" }}>
              <th style={{ padding: "4px 0" }}>Instrument</th>
              <th>Threshold</th>
              <th>Window</th>
              <th>Actual move</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.instrument} style={{ borderTop: "1px solid var(--border)" }}>
                <td className="mono" style={{ padding: "8px 0" }}>{a.instrument}</td>
                <td>
                  <input
                    type="number"
                    defaultValue={a.threshold_pct}
                    onBlur={(e) => save(a.instrument, { threshold_pct: parseFloat(e.target.value) })}
                    style={{ width: 50, background: "var(--bg-panel-alt)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", padding: "3px 5px" }}
                  />
                  %
                </td>
                <td>
                  <input
                    type="number"
                    defaultValue={a.window_days}
                    onBlur={(e) => save(a.instrument, { window_days: parseInt(e.target.value, 10) })}
                    style={{ width: 50, background: "var(--bg-panel-alt)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", padding: "3px 5px" }}
                  />
                  d
                </td>
                <td className={a.change_pct > 0 ? "" : ""} style={{ color: a.change_pct > 0 ? "var(--bullish)" : "var(--bearish)" }}>
                  {a.change_pct !== null ? `${a.change_pct > 0 ? "+" : ""}${a.change_pct}%` : "n/a"}
                </td>
                <td>
                  {a.triggered ? <span className="tag tag-bearish">TRIGGERED</span> : <span className="tag tag-neutral">ok</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
