export default function AlertBanner({ triggered }) {
  if (!triggered || triggered.length === 0) return null;
  return (
    <div
      style={{
        background: "rgba(239,91,91,0.12)", border: "1px solid var(--bearish)", color: "var(--bearish)",
        borderRadius: 8, padding: "10px 14px", marginBottom: 16, fontSize: 13, fontWeight: 600,
      }}
    >
      ⚠ {triggered.length} threshold alert{triggered.length > 1 ? "s" : ""} triggered:{" "}
      {triggered.map((a) => `${a.instrument} ${a.change_pct > 0 ? "+" : ""}${a.change_pct}% over ${a.window_days}d`).join(" · ")}
    </div>
  );
}
