import { useEffect, useState } from "react";
import { api } from "./api";
import CommodityView from "./components/CommodityView";
import BomExposure from "./components/BomExposure";
import AlertsPanel from "./components/AlertsPanel";
import AlertBanner from "./components/AlertBanner";
import ExportButton from "./components/ExportButton";

const GROUPS = [
  { label: "LME (3M, USD/tonne)", market: "LME" },
  { label: "MCX (near-month, INR/kg)", market: "MCX" },
  { label: "NALCO (domestic, INR/kg)", market: "NALCO" },
];

export default function App() {
  const [instruments, setInstruments] = useState(null);
  const [active, setActive] = useState(null);
  const [view, setView] = useState("commodity"); // "commodity" | "epc"
  const [triggeredAlerts, setTriggeredAlerts] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listInstruments()
      .then((list) => {
        setInstruments(list);
        setActive(list[0]?.code);
      })
      .catch(setError);
  }, []);

  if (error) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Could not reach the API</h2>
        <p className="dim">{String(error.message || error)}</p>
        <p className="faint">Is the backend running at the URL in VITE_API_BASE_URL?</p>
      </div>
    );
  }

  if (!instruments) return <div style={{ padding: 40 }}>Loading…</div>;

  const activeMeta = instruments.find((i) => i.code === active);

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "20px 20px 60px" }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, marginBottom: 2 }}>Solar EPC Commodity Intelligence</h1>
        <p className="faint">
          Delayed / periodic pricing (not real-time) for non-ferrous metals relevant to solar EPC &amp; BESS cost structures.
        </p>
      </header>

      <AlertBanner triggered={triggeredAlerts} />
      {/* keep alert state warm globally so the banner works regardless of active tab */}
      <div style={{ display: "none" }}>
        <AlertsPanel onAlertsLoaded={(all) => setTriggeredAlerts(all.filter((a) => a.triggered))} />
      </div>

      <nav style={{ display: "flex", gap: 8, marginBottom: 16, borderBottom: "1px solid var(--border)", paddingBottom: 12, flexWrap: "wrap" }}>
        <button
          onClick={() => setView("epc")}
          style={{
            background: view === "epc" ? "var(--accent)" : "var(--bg-panel)", color: view === "epc" ? "#08111c" : "var(--text)",
            border: "1px solid var(--border)", borderRadius: 8, padding: "6px 14px", fontWeight: 600, fontSize: 13,
          }}
        >
          EPC Tools
        </button>
        <span style={{ width: 1, background: "var(--border)", margin: "0 4px" }} />
        {GROUPS.map((g) => (
          <div key={g.market} style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <span className="faint" style={{ marginRight: 2 }}>{g.label}</span>
            {instruments
              .filter((i) => i.market === g.market)
              .map((i) => (
                <button
                  key={i.code}
                  onClick={() => {
                    setActive(i.code);
                    setView("commodity");
                  }}
                  style={{
                    background: view === "commodity" && active === i.code ? "var(--accent)" : "var(--bg-panel)",
                    color: view === "commodity" && active === i.code ? "#08111c" : "var(--text)",
                    border: "1px solid var(--border)", borderRadius: 8, padding: "6px 12px", fontWeight: 600, fontSize: 13,
                  }}
                >
                  {i.name.replace(/ \(.*\)/, "").replace(/^LME |^MCX |^NALCO /, "")}
                </button>
              ))}
          </div>
        ))}
      </nav>

      {view === "commodity" && activeMeta && <CommodityView instrument={active} meta={activeMeta} />}

      {view === "epc" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <ExportButton />
          <BomExposure />
          <AlertsPanel onAlertsLoaded={(all) => setTriggeredAlerts(all.filter((a) => a.triggered))} />
        </div>
      )}

      <footer className="faint" style={{ marginTop: 40, borderTop: "1px solid var(--border)", paddingTop: 12 }}>
        All prices are delayed/periodic and carry their own source + "as of" timestamp — never treated as live execution quotes.
        The "Expected price" panel is a rules-based technical/factor view, not a forecast or investment advice.
      </footer>
    </div>
  );
}
