const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

async function put(path, data) {
  const res = await fetch(`${BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export const api = {
  listInstruments: () => get("/api/commodities"),
  getLatest: (instrument) => get(`/api/commodities/${instrument}/latest`),
  getHistory: (instrument, range) => get(`/api/commodities/${instrument}/history?range=${range}`),
  getExpectedPrice: (instrument) => get(`/api/commodities/${instrument}/expected-price`),
  getFactors: (instrument) => get(`/api/commodities/${instrument}/factors`),
  getBomWeights: () => get("/api/epc/bom-weights"),
  updateBomWeight: (payload) => put("/api/epc/bom-weights", payload),
  getLandedCost: (instrument) => get(`/api/epc/landed-cost/${instrument}`),
  updateLandedCost: (instrument, payload) => put(`/api/epc/landed-cost/${instrument}`, payload),
  getAlerts: () => get("/api/epc/alerts"),
  updateAlert: (instrument, payload) => put(`/api/epc/alerts/${instrument}`, payload),
  exportSnapshotUrl: (format) => `${BASE}/api/export/bid-snapshot?format=${format}`,
};

export { BASE as API_BASE };
