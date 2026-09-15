import { useEffect, useState } from "react";
import { api } from "../api";

export default function BomExposure() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);
  const [savingKey, setSavingKey] = useState(null);

  const load = () => api.getBomWeights().then(setRows).catch(setError);

  useEffect(() => {
    load();
  }, []);

  const onEdit = async (row, value) => {
    if (Number.isNaN(value)) return;
    const key = `${row.instrument}:${row.component}`;
    setSavingKey(key);
    try {
      await api.updateBomWeight({ instrument: row.instrument, component: row.component, weight_pct_of_module_cost: value, notes: row.notes });
      await load();
    } catch (e) {
      setError(e);
    } finally {
      setSavingKey(null);
    }
  };

  return (
    <div className="panel">
      <div className="dim" style={{ fontWeight: 600, marginBottom: 4 }}>Solar EPC BOM exposure mapping</div>
      <div className="faint" style={{ marginBottom: 10 }}>
        Approximate weight of each commodity in total module/BOS cost. Editable — adjust to match your own project's bill of materials.
      </div>
      {error && <div className="dim">Could not load: {String(error.message || error)}</div>}
      {!rows && !error && <div className="dim">Loading…</div>}
      {rows && (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ textAlign: "left", color: "var(--text-faint)", fontSize: 11, textTransform: "uppercase" }}>
              <th style={{ padding: "4px 0" }}>Instrument</th>
              <th>BOM component</th>
              <th style={{ textAlign: "right" }}>Weight (% of module cost)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const key = `${row.instrument}:${row.component}`;
              return (
                <tr key={key} style={{ borderTop: "1px solid var(--border)" }}>
                  <td className="mono" style={{ padding: "8px 0" }}>{row.instrument}</td>
                  <td style={{ paddingRight: 8 }}>
                    {row.component}
                    <div className="faint">{row.notes}</div>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <input
                      type="number"
                      step="0.1"
                      defaultValue={row.weight_pct_of_module_cost}
                      onBlur={(e) => onEdit(row, parseFloat(e.target.value))}
                      style={{
                        width: 70, textAlign: "right", background: "var(--bg-panel-alt)",
                        border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", padding: "4px 6px",
                      }}
                    />
                    {savingKey === key && <span className="faint"> saving…</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
