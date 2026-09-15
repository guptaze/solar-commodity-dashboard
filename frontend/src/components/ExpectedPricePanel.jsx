import { useEffect, useState } from "react";
import { api } from "../api";

const LEAN_CLASS = { bullish: "tag-bullish", bearish: "tag-bearish", neutral: "tag-neutral" };

function MA({ label, value }) {
  return (
    <div style={{ textAlign: "center", flex: 1 }}>
      <div className="faint">{label}</div>
      <div className="mono" style={{ fontWeight: 600 }}>{value !== null && value !== undefined ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "n/a"}</div>
    </div>
  );
}

export default function ExpectedPricePanel({ instrument }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setData(null);
    setError(null);
    api.getExpectedPrice(instrument).then(setData).catch(setError);
  }, [instrument]);

  return (
    <div className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div className="dim" style={{ fontWeight: 600 }}>Expected price view</div>
        {data && <span className={`tag ${LEAN_CLASS[data.lean]}`}>{data.lean}</span>}
      </div>

      {error && <div className="dim">Could not load: {String(error.message || error)}</div>}
      {!error && !data && <div className="dim">Loading…</div>}
      {data && (
        <>
          <div style={{ display: "flex", marginTop: 12, marginBottom: 12 }}>
            <MA label="20D MA" value={data.ma20} />
            <MA label="50D MA" value={data.ma50} />
            <MA label="200D MA" value={data.ma200} />
          </div>
          <div className="dim" style={{ marginBottom: 4 }}>
            Trend: <strong style={{ textTransform: "capitalize" }}>{data.trend}</strong> · Factor tally: {data.bullish_factors} bullish / {data.bearish_factors} bearish / {data.neutral_factors} neutral
          </div>
          <div className="faint">{data.disclaimer}</div>
        </>
      )}
    </div>
  );
}
