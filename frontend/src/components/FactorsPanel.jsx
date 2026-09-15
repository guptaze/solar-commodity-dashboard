import { useEffect, useState } from "react";
import { api } from "../api";

const LEAN_CLASS = { bullish: "tag-bullish", bearish: "tag-bearish", neutral: "tag-neutral" };

export default function FactorsPanel({ instrument }) {
  const [factors, setFactors] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setFactors(null);
    setError(null);
    api.getFactors(instrument).then((r) => setFactors(r.factors)).catch(setError);
  }, [instrument]);

  return (
    <div className="panel">
      <div className="dim" style={{ fontWeight: 600, marginBottom: 8 }}>Macro / fundamental factors</div>
      {error && <div className="dim">Could not load factors: {String(error.message || error)}</div>}
      {!error && !factors && <div className="dim">Loading…</div>}
      {factors && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {factors.map((f) => (
            <div key={f.name} style={{ borderBottom: "1px solid var(--border)", paddingBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <strong>{f.name}</strong>
                <span className={`tag ${LEAN_CLASS[f.direction]}`}>{f.direction}</span>
              </div>
              <div className="dim" style={{ fontSize: 13 }}>{f.mechanism}</div>
              <div className="faint" style={{ marginTop: 2 }}>Precedent: {f.evidence}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
