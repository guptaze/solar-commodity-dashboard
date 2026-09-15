"""Static reference config: instrument metadata, curated macro factors, and EPC defaults.

None of this changes often enough to warrant a DB table (unlike BOM weights / landed-cost
inputs / alert thresholds, which are user-editable and live in the DB) except where noted.
"""

# Every tradable instrument the dashboard tracks. "metal" groups LME/MCX/NALCO variants of
# the same underlying commodity so they can share a factors panel.
INSTRUMENTS = {
    "LME_ALUMINIUM": {"name": "LME Aluminium (3M)", "market": "LME", "metal": "aluminium", "unit": "USD/tonne", "currency": "USD"},
    "LME_COPPER": {"name": "LME Copper (3M)", "market": "LME", "metal": "copper", "unit": "USD/tonne", "currency": "USD"},
    "LME_ZINC": {"name": "LME Zinc (3M)", "market": "LME", "metal": "zinc", "unit": "USD/tonne", "currency": "USD"},
    "LME_LEAD": {"name": "LME Lead (3M)", "market": "LME", "metal": "lead", "unit": "USD/tonne", "currency": "USD"},
    "LME_NICKEL": {"name": "LME Nickel (3M)", "market": "LME", "metal": "nickel", "unit": "USD/tonne", "currency": "USD"},
    "LME_TIN": {"name": "LME Tin (3M)", "market": "LME", "metal": "tin", "unit": "USD/tonne", "currency": "USD"},
    "MCX_COPPER": {"name": "MCX Copper (near-month)", "market": "MCX", "metal": "copper", "unit": "INR/kg", "currency": "INR"},
    "MCX_ALUMINIUM": {"name": "MCX Aluminium (near-month)", "market": "MCX", "metal": "aluminium", "unit": "INR/kg", "currency": "INR"},
    "NALCO_ALUMINIUM": {"name": "NALCO Domestic Aluminium", "market": "NALCO", "metal": "aluminium", "unit": "INR/kg", "currency": "INR"},
}

# instruments quoted in USD/tonne that need the forex + /1000 conversion to show INR/kg alongside
LME_INSTRUMENTS = [k for k, v in INSTRUMENTS.items() if v["market"] == "LME"]

FACTORS = {
    "aluminium": [
        {"name": "China PMI / demand", "direction": "neutral", "mechanism": "China consumes ~55% of global aluminium; PMI above 50 signals expanding industrial demand pulling on smelter output.", "evidence": "China Caixin manufacturing PMI dipped below 50 in Aug 2023, coinciding with a 6% aluminium price pullback over the following month."},
        {"name": "USD Index (DXY)", "direction": "bearish", "mechanism": "Aluminium is dollar-priced; a stronger dollar makes it costlier for non-USD buyers, dampening demand and pressuring price.", "evidence": "DXY rally from 90 to 114 in 2022 tracked with LME aluminium falling from ~$3,300 to ~$2,300/tonne."},
        {"name": "LME warehouse inventories", "direction": "bearish", "mechanism": "Rising exchange-registered stocks signal oversupply relative to draw-down demand, capping price.", "evidence": "LME aluminium stocks more than doubled through H1 2023, coinciding with prices staying range-bound near multi-year lows."},
        {"name": "Power / energy cost", "direction": "bullish", "mechanism": "Smelting is highly power-intensive (~14-15 MWh/tonne); energy price spikes squeeze smelter margins and force curtailments, tightening supply.", "evidence": "European gas/power crisis in 2022 forced smelters (Alcoa, Trimet) to curtail >1M tonnes of capacity, supporting prices even as demand softened."},
        {"name": "Chinese smelter supply discipline", "direction": "bullish", "mechanism": "China's 45M-tonne capacity cap and periodic power-curb enforcement in Yunnan/Sichuan constrain output growth structurally.", "evidence": "2021 Yunnan power curbs cut regional smelter output ~10%; LME aluminium rose ~35% over the following 6 months."},
        {"name": "Trade tariffs / import duty", "direction": "bullish", "mechanism": "Section 232-style tariffs and Indian BCD changes raise landed cost for importers, supporting domestic (NALCO) premiums over LME.", "evidence": "US Section 232 25% aluminium tariff (2018, raised further in 2025) widened Midwest premium sharply versus LME cash."},
        {"name": "EV / renewables demand pull", "direction": "bullish", "mechanism": "Lightweighting in EVs and solar mounting structures adds structural demand growth beyond traditional construction/transport.", "evidence": "IEA estimates solar + EV aluminium demand roughly doubling by 2030 versus 2020 baseline."},
        {"name": "Fed rate decisions", "direction": "neutral", "mechanism": "Lower real rates reduce the opportunity cost of holding inventory and typically weaken the dollar, both price-supportive.", "evidence": "Aluminium rallied through 2020-21 as the Fed held rates near zero and expanded its balance sheet."},
    ],
    "copper": [
        {"name": "China PMI / demand", "direction": "bullish", "mechanism": "China accounts for ~half of refined copper demand via grid, construction and manufacturing; PMI expansion signals stronger offtake.", "evidence": "China's 2023 grid investment push (+5% YoY) helped copper hold above $8,000/tonne despite a soft property sector."},
        {"name": "USD Index (DXY)", "direction": "bearish", "mechanism": "Copper is dollar-priced; dollar strength raises effective cost for ex-US buyers and typically inverse-correlates with price.", "evidence": "Copper fell from ~$4.90/lb to ~$3.30/lb through 2022 as DXY rallied to two-decade highs."},
        {"name": "LME warehouse inventories", "direction": "bullish", "mechanism": "Copper stocks have stayed structurally low versus history, leaving the market vulnerable to squeezes on any demand upside surprise.", "evidence": "LME copper stocks fell to multi-decade lows in 2021, contributing to a brief supply squeeze and record prices above $10,700/tonne."},
        {"name": "Major mine/smelter disruptions", "direction": "bullish", "mechanism": "Copper supply is concentrated in a handful of large mines (Chile, Peru, Indonesia); strikes, ore-grade decline or closures tighten the concentrate market quickly.", "evidence": "Cobre Panama mine closure (Nov 2023, ~1.5% of global supply) drove a swift rally in treatment charges and supported prices into 2024."},
        {"name": "Energy/input costs", "direction": "neutral", "mechanism": "Copper smelting is less power-intensive than aluminium, so energy costs matter mainly through diesel/mining input costs at the mine level.", "evidence": "2022 diesel and explosives cost inflation raised all-in sustaining costs at major Chilean mines by ~10-15%."},
        {"name": "Trade tariffs / import duty", "direction": "bearish", "mechanism": "US Section 232 copper tariff proposals raise the risk of demand destruction/rerouting, adding volatility without a clear structural supply response.", "evidence": "2025 US Section 232 copper tariff announcement caused a sharp COMEX-LME arbitrage spike and short-term price dislocation."},
        {"name": "Fed rate decisions", "direction": "bullish", "mechanism": "Rate cuts weaken the dollar and lower financing costs for capital-intensive mine development and inventory holding, both price-supportive.", "evidence": "Copper rallied through late 2023 into 2024 as markets priced in an approaching Fed easing cycle."},
        {"name": "EV / renewables demand pull", "direction": "bullish", "mechanism": "EVs use ~2-3x the copper of ICE vehicles; solar and grid buildout add further structural demand (each MW of solar needs ~4-5 tonnes of copper).", "evidence": "S&P Global projects copper demand from EVs and renewables to double by 2035, a key driver of long-run bullish forecasts."},
    ],
    "zinc": [
        {"name": "China PMI / demand", "direction": "neutral", "mechanism": "Zinc demand is tied mainly to galvanised steel for construction; China PMI softness weighs directly on offtake.", "evidence": "Weak Chinese property construction through 2023-24 kept zinc price gains capped versus other base metals."},
        {"name": "USD Index (DXY)", "direction": "bearish", "mechanism": "Dollar-priced like other LME metals; a stronger dollar mechanically pressures zinc.", "evidence": "Zinc fell alongside the broader base metals complex during the 2022 DXY rally."},
        {"name": "LME warehouse inventories", "direction": "bullish", "mechanism": "Zinc stocks have fallen to multi-year lows amid smelter curtailments, tightening physical availability.", "evidence": "European zinc smelter curtailments in the 2022 energy crisis (Nyrstar, Glencore) removed ~500kt of capacity, supporting premiums."},
        {"name": "Energy/input costs", "direction": "bullish", "mechanism": "Zinc smelting is power-intensive; high electricity prices squeeze smelter margins and trigger curtailments similar to aluminium.", "evidence": "2022 European gas price spike forced ~50% of regional zinc smelting capacity offline at points."},
        {"name": "Major mine/smelter disruptions", "direction": "bullish", "mechanism": "A concentrated set of large mines (e.g., Red Dog, Antamina by-product) means single-asset outages move the concentrate market.", "evidence": "Mine supply disruptions in 2023 pushed treatment charges negative, signalling a tight concentrate market."},
        {"name": "Trade tariffs / import duty", "direction": "neutral", "mechanism": "Zinc sees fewer targeted tariff actions than aluminium/steel/copper, so policy risk is comparatively muted.", "evidence": "No major Section 232-style zinc-specific tariff action has moved global prices materially in recent cycles."},
        {"name": "Fed rate decisions", "direction": "neutral", "mechanism": "Like other base metals, easier policy is broadly supportive via dollar weakness and lower carry costs.", "evidence": "Zinc participated in the broad base-metals rally around the 2019 and 2024 Fed easing pivots."},
        {"name": "EV / renewables demand pull", "direction": "neutral", "mechanism": "Zinc's exposure to the energy transition is indirect (galvanised solar mounting structures), smaller than copper or aluminium's.", "evidence": "Solar galvanised structure demand is a modest, steady tailwind rather than a step-change driver for zinc."},
    ],
    "lead": [
        {"name": "China PMI / demand", "direction": "neutral", "mechanism": "Lead demand is dominated by lead-acid batteries (auto + backup power), only loosely tied to broad industrial PMI.", "evidence": "Lead prices have historically shown lower PMI correlation than copper or aluminium."},
        {"name": "USD Index (DXY)", "direction": "bearish", "mechanism": "Dollar-priced LME metal; inverse relationship with the dollar holds broadly.", "evidence": "Lead softened alongside the base metals complex during 2022's DXY strength."},
        {"name": "LME warehouse inventories", "direction": "neutral", "mechanism": "Lead's large secondary (recycled battery) supply base cushions the impact of exchange stock swings versus primary-supply metals.", "evidence": "Lead prices stayed comparatively range-bound through 2022-23 despite inventory volatility."},
        {"name": "Energy/input costs", "direction": "neutral", "mechanism": "Secondary lead smelting (recycling) is less power-intensive than primary aluminium/zinc smelting, muting energy-cost pass-through.", "evidence": "Lead showed a smaller price reaction to the 2022 European energy crisis than aluminium or zinc."},
        {"name": "Major mine/smelter disruptions", "direction": "neutral", "mechanism": "With ~50% of supply from recycling, single-mine disruptions matter less than for concentrate-dependent metals.", "evidence": "Primary mine strikes in 2023 had a muted, short-lived effect on lead versus copper's sharper reaction."},
        {"name": "Trade tariffs / import duty", "direction": "neutral", "mechanism": "Lead sees limited targeted tariff action; battery-related trade policy affects it indirectly at most.", "evidence": "No major lead-specific tariff shock has been a primary price driver in recent years."},
        {"name": "Fed rate decisions", "direction": "neutral", "mechanism": "Standard base-metal sensitivity to dollar and carry costs, but smaller in magnitude given the smaller, more balanced market.", "evidence": "Lead's beta to Fed policy shifts has historically been lower than copper's."},
        {"name": "EV / renewables demand pull", "direction": "bearish", "mechanism": "EV adoption displaces lead-acid starter batteries over time (lithium-ion dominates traction batteries), a long-run structural headwind.", "evidence": "Long-run demand forecasts show lead-acid SLI battery volumes plateauing as EV penetration rises."},
    ],
    "nickel": [
        {"name": "China PMI / demand", "direction": "neutral", "mechanism": "Nickel demand splits between stainless steel (China-heavy) and EV battery precursors, giving mixed PMI sensitivity.", "evidence": "Chinese stainless steel output growth partly offset weak property-linked demand through 2023."},
        {"name": "USD Index (DXY)", "direction": "bearish", "mechanism": "Dollar-priced LME metal; standard inverse dollar relationship.", "evidence": "Nickel corrected sharply in 2022-23 alongside dollar strength and a broader base-metals selloff."},
        {"name": "LME warehouse inventories", "direction": "bearish", "mechanism": "Indonesian NPI/matte supply growth has flooded the market, pushing LME-deliverable-equivalent supply higher and pressuring price.", "evidence": "Indonesian nickel output surged ~40% from 2021-2023, driving LME nickel down from >$100,000/tonne (Mar 2022 squeeze peak) to under $17,000 by 2024."},
        {"name": "Energy/input costs", "direction": "neutral", "mechanism": "Indonesian NPI production is coal-power intensive, so energy costs affect the marginal cost curve but supply growth has dominated the price story.", "evidence": "Despite rising input costs, oversupply kept nickel prices depressed through 2023-24."},
        {"name": "Major mine/smelter disruptions", "direction": "bullish", "mechanism": "High-cost Western producers (e.g., in Australia, New Caledonia) have curtailed operations as prices fell below cost, a slow-acting supply response.", "evidence": "BHP suspended its Nickel West operations in 2024 as prices fell below its production cost."},
        {"name": "Trade tariffs / import duty", "direction": "neutral", "mechanism": "Indonesia's ore export ban (not a tariff, but similar effect) reshaped trade flows toward domestic downstream processing rather than raw ore export.", "evidence": "Indonesia's 2020 nickel ore export ban shifted the entire supply chain and contributed to the 2022 price squeeze."},
        {"name": "Fed rate decisions", "direction": "neutral", "mechanism": "Standard dollar/carry-cost channel applies, though currently secondary to the supply-glut narrative.", "evidence": "Rate-driven dollar moves have had a smaller relative impact on nickel than the Indonesian supply story since 2022."},
        {"name": "EV / renewables demand pull", "direction": "bullish", "mechanism": "Nickel is a key input in NMC/NCA battery chemistries used in longer-range EVs and some grid storage.", "evidence": "Battery-grade nickel demand roughly tripled from 2018-2023 even as LFP gains share, per IEA battery metals data."},
    ],
    "tin": [
        {"name": "China PMI / demand", "direction": "bullish", "mechanism": "Tin's largest end-use is solder for electronics; Chinese/global electronics manufacturing PMI is a direct demand read.", "evidence": "2023-24 semiconductor/electronics upcycle coincided with tin price recovery off 2023 lows."},
        {"name": "USD Index (DXY)", "direction": "bearish", "mechanism": "Dollar-priced LME metal; standard inverse relationship.", "evidence": "Tin fell over 35% through 2022 alongside dollar strength and a post-COVID electronics demand cooldown."},
        {"name": "LME warehouse inventories", "direction": "bullish", "mechanism": "Tin has the smallest, thinnest LME market of the six base metals, so exchange stock levels move price disproportionately.", "evidence": "Low LME tin stocks in 2021-22 amplified price swings both up (2021 rally to record highs) and down (2022 selloff)."},
        {"name": "Major mine/smelter disruptions", "direction": "bullish", "mechanism": "Supply is concentrated in Indonesia, Myanmar (Wa State) and DRC; export bans or conflict-linked disruptions in any one materially tighten global supply.", "evidence": "Myanmar's Wa State mining suspension (Aug 2023) removed a significant share of global mine supply and supported 2024 prices."},
        {"name": "Energy/input costs", "direction": "neutral", "mechanism": "Tin smelting is less energy-intensive than aluminium/zinc, so power costs are a secondary driver versus ore availability.", "evidence": "Tin's 2022-23 price moves tracked ore supply news more closely than energy headlines."},
        {"name": "Trade tariffs / import duty", "direction": "neutral", "mechanism": "Indonesia's periodic export licensing delays function like informal export controls, occasionally disrupting shipments.", "evidence": "Indonesian export licensing delays in early 2024 caused a temporary shipment slowdown and price support."},
        {"name": "Fed rate decisions", "direction": "neutral", "mechanism": "Standard dollar/carry channel, secondary to supply-concentration risk for this smaller market.", "evidence": "Tin's dollar sensitivity is present but historically smaller in magnitude than copper's or aluminium's."},
        {"name": "EV / renewables demand pull", "direction": "bullish", "mechanism": "Solder demand grows with power electronics content in EVs, inverters and grid equipment, layered on top of core electronics demand.", "evidence": "Growing power-electronics content per EV and per solar inverter is cited by ITA (International Tin Association) as a structural demand driver."},
    ],
}

# Default BOM cost-stack weightings for solar EPC + BESS scope. Percentages are of total
# module/BOS cost, editable by the user via the API — these are starting-point estimates.
DEFAULT_BOM_WEIGHTS = [
    {"instrument": "LME_ALUMINIUM", "component": "Module frames & mounting structures (MMS)", "weight_pct_of_module_cost": 8.0, "notes": "Aluminium extrusion for frames + racking; largest single non-ferrous exposure in EPC BOM."},
    {"instrument": "LME_COPPER", "component": "DC/AC cabling, transformers & earthing", "weight_pct_of_module_cost": 4.5, "notes": "String cables, AC feeders, transformer windings, earthing conductors."},
    {"instrument": "LME_ZINC", "component": "Galvanised steel structures (MMS coating)", "weight_pct_of_module_cost": 1.5, "notes": "Hot-dip galvanising of steel MMS and structural steel, priced via zinc coating weight."},
]

DEFAULT_LANDED_COST = {
    "LME_ALUMINIUM": {"freight_insurance_pct": 2.0, "customs_duty_pct": 7.5, "gst_pct": 18.0, "trader_premium_inr_per_kg": 8.0},
    "LME_COPPER": {"freight_insurance_pct": 1.5, "customs_duty_pct": 5.0, "gst_pct": 18.0, "trader_premium_inr_per_kg": 6.0},
    "LME_ZINC": {"freight_insurance_pct": 2.0, "customs_duty_pct": 7.5, "gst_pct": 18.0, "trader_premium_inr_per_kg": 4.0},
    "LME_LEAD": {"freight_insurance_pct": 2.0, "customs_duty_pct": 7.5, "gst_pct": 18.0, "trader_premium_inr_per_kg": 3.0},
    "LME_NICKEL": {"freight_insurance_pct": 1.5, "customs_duty_pct": 5.0, "gst_pct": 18.0, "trader_premium_inr_per_kg": 15.0},
    "LME_TIN": {"freight_insurance_pct": 1.5, "customs_duty_pct": 5.0, "gst_pct": 18.0, "trader_premium_inr_per_kg": 25.0},
}

DEFAULT_ALERTS = {code: {"threshold_pct": 5.0, "window_days": 30} for code in INSTRUMENTS}
