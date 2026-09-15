import { api } from "../api";

export default function ExportButton() {
  return (
    <div style={{ display: "flex", gap: 8 }}>
      <a href={api.exportSnapshotUrl("csv")} className="panel" style={{ padding: "8px 14px", textDecoration: "none", color: "var(--text)", fontSize: 13, fontWeight: 600 }}>
        ⬇ Export bid snapshot (CSV)
      </a>
      <a href={api.exportSnapshotUrl("json")} target="_blank" rel="noreferrer" className="panel" style={{ padding: "8px 14px", textDecoration: "none", color: "var(--text)", fontSize: 13, fontWeight: 600 }}>
        ⬇ Export bid snapshot (JSON)
      </a>
    </div>
  );
}
