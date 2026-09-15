import { useEffect, useState } from "react";
import { api } from "../api";
import PriceCard from "./PriceCard";
import PriceChart from "./PriceChart";
import ExpectedPricePanel from "./ExpectedPricePanel";
import FactorsPanel from "./FactorsPanel";
import LandedCostCalculator from "./LandedCostCalculator";

export default function CommodityView({ instrument, meta }) {
  const [latest, setLatest] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLatest(null);
    setError(null);
    setLoading(true);
    api
      .getLatest(instrument)
      .then(setLatest)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [instrument]);

  const isLme = meta.market === "LME";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <PriceCard meta={meta} latest={latest} loading={loading} error={error} />
      <PriceChart instrument={instrument} isLme={isLme} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }} className="two-col">
        <ExpectedPricePanel instrument={instrument} />
        {isLme ? <LandedCostCalculator instrument={instrument} /> : <div className="panel dim">Landed-cost calculator is configured for LME base metals (the import leg). MCX and NALCO prices are already domestic INR quotes.</div>}
      </div>
      <FactorsPanel instrument={instrument} />
    </div>
  );
}
