from app.static_data import FACTORS, INSTRUMENTS

DIRECTION_SCORE = {"bullish": 1, "bearish": -1, "neutral": 0}


def get_factors_for_instrument(instrument: str) -> list[dict]:
    metal = INSTRUMENTS[instrument]["metal"]
    return FACTORS.get(metal, [])


def factor_score(instrument: str) -> dict:
    factors = get_factors_for_instrument(instrument)
    if not factors:
        return {"score": 0, "lean": "neutral", "bullish_count": 0, "bearish_count": 0, "neutral_count": 0}
    total = sum(DIRECTION_SCORE[f["direction"]] for f in factors)
    bullish = sum(1 for f in factors if f["direction"] == "bullish")
    bearish = sum(1 for f in factors if f["direction"] == "bearish")
    neutral = sum(1 for f in factors if f["direction"] == "neutral")
    if total >= 2:
        lean = "bullish"
    elif total <= -2:
        lean = "bearish"
    else:
        lean = "neutral"
    return {"score": total, "lean": lean, "bullish_count": bullish, "bearish_count": bearish, "neutral_count": neutral}


def directional_lean(instrument: str, trend: str) -> dict:
    """Combines the rules-based factor score with the MA trend into one labeled, non-ML lean.
    Explicitly indicative - not a prediction - per the product requirement."""
    fscore = factor_score(instrument)
    trend_bias = {"uptrend": 1, "downtrend": -1, "sideways": 0}[trend]
    combined = fscore["score"] + trend_bias
    if combined >= 2:
        lean = "bullish"
    elif combined <= -2:
        lean = "bearish"
    else:
        lean = "neutral"
    return {
        "lean": lean,
        "factor_score": fscore["score"],
        "trend": trend,
        "bullish_factors": fscore["bullish_count"],
        "bearish_factors": fscore["bearish_count"],
        "neutral_factors": fscore["neutral_count"],
        "disclaimer": "Indicative, rules-based lean derived from moving-average trend and curated factor tags. Not a price prediction or investment advice.",
    }
