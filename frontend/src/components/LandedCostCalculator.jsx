import { useEffect, useState } from "react";
import { api } from "../api";

function Field({ label, value, onChange, suffix }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12 }}>
      <span className="faint">{label}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <input
          type="number"
          step="0.1"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          style={{
            width: 90, background: "var(--bg-panel-alt)", border: "1px solid var(--border)",
            borderRadius: 6, color: "var(--text)", padding: "4px 6px",
          }}
        />
        <span className="faint">{suffix}</span>
      </div>
    </label>
  );
}

export default function LandedCostCalculator({ instrument }) {
  const [calc, setCalc] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setError(null);
    api.getLandedCost(instrument).then(setCalc).catch(setError);
  };

  useEffect(() => {
    setCalc(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [instrument]);

  const updateInput = async (field, value) => {
    if (Number.isNaN(value)) return;
    setSaving(true);
    try {
      await api.updateLandedCost(instrument, { [field]: value });
      load();
    } catch (e) {
      setError(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="panel">
      <div className="dim" style={{ fontWeight: 600, marginBottom: 8 }}>Landed cost calculator</div>
      {error && <div className="dim">Could not load: {String(error.message || error)}</div>}
      {!calc && !error && <div className="dim">Loading…</div>}
      {calc && (
        <>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 12 }}>
            <Field label="Freight + insurance" value={calc.inputs.freight_insurance_pct} suffix="%" onChange={(v) => updateInput("freight_insurance_pct", v)} />
            <Field label="Customs duty" value={calc.inputs.customs_duty_pct} suffix="%" onChange={(v) => updateInput("customs_duty_pct", v)} />
            <Field label="GST" value={calc.inputs.gst_pct} suffix="%" onChange={(v) => updateInput("gst_pct", v)} />
            <Field label="Trader premium" value={calc.inputs.trader_premium_inr_per_kg} suffix="₹/kg" onChange={(v) => updateInput("trader_premium_inr_per_kg", v)} />
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <tbody>
              <Row label="Base (LME/MCX → INR/kg)" value={calc.base_inr_per_kg} />
              <Row label="+ Freight & insurance" value={calc.after_freight_insurance} />
              <Row label="+ Customs duty" value={calc.after_customs_duty} />
              <Row label="+ Trader premium" value={calc.after_trader_premium} />
              <Row label="+ GST → Landed cost" value={calc.landed_cost_inr_per_kg} strong />
            </tbody>
          </table>
          <div className="faint" style={{ marginTop: 8 }}>
            Based on price as of {new Date(calc.price_as_of).toLocaleString()} ({calc.price_source}
            {calc.price_is_stale ? ", stale" : ""}). {saving && "Saving…"}
          </div>
        </>
      )}
    </div>
  );
}

function Row({ label, value, strong }) {
  return (
    <tr style={{ borderTop: "1px solid var(--border)" }}>
      <td style={{ padding: "6px 0", color: strong ? "var(--text)" : "var(--text-dim)", fontWeight: strong ? 700 : 400 }}>{label}</td>
      <td className="mono" style={{ padding: "6px 0", textAlign: "right", fontWeight: strong ? 700 : 400 }}>₹{value.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
    </tr>
  );
}
