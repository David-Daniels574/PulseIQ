"""
Fast PESTEL inference with balanced factor output.

This module returns PESTEL-only output with structured factors:
- title
- sentiment
- severity
- summary
- implication
- source metadata
"""

from __future__ import annotations

from typing import Any, Dict, List


PESTEL_KEYWORDS: Dict[str, List[str]] = {
    "political": ["policy", "government", "tax", "subsidy", "regulation", "election", "municipal"],
    "economic": ["inflation", "price", "lpg", "cost", "recession", "growth", "demand", "wage"],
    "social": ["trend", "lifestyle", "consumer", "viral", "influencer", "community", "gen z"],
    "technological": ["delivery", "platform", "app", "ai", "automation", "online", "digital", "payment"],
    "environmental": ["sustainability", "carbon", "waste", "green", "plastic", "recycle", "climate"],
    "legal": ["compliance", "law", "license", "legal", "penalty", "guideline", "fssai"],
}

CATEGORY_TARGETS: Dict[str, int] = {
    "political": 2,
    "economic": 3,
    "social": 2,
    "technological": 2,
    "environmental": 2,
    "legal": 3,
}

POSITIVE_WORDS = {
    "extend", "growth", "boost", "support", "approval", "improve", "increase", "recovery", "ease",
}
NEGATIVE_WORDS = {
    "hike", "crisis", "penalty", "ban", "drop", "decline", "shortage", "slowdown", "cut", "inflation",
}
HIGH_SEVERITY_WORDS = {
    "ban", "penalty", "crisis", "shortage", "compliance", "law", "inflation", "tax",
}


def _tokenize(text: str) -> List[str]:
    return [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in (text or "")).split() if t]


def _detect_sentiment(text: str) -> str:
    tokens = set(_tokenize(text))
    if tokens & NEGATIVE_WORDS:
        return "Negative"
    if tokens & POSITIVE_WORDS:
        return "Positive"
    return "Neutral"


def _detect_severity(text: str, category: str) -> str:
    tokens = set(_tokenize(text))
    if tokens & HIGH_SEVERITY_WORDS:
        return "High"
    if category in {"environmental", "social"}:
        return "Low"
    return "Medium"


def _category_implication(category: str, sentiment: str, headline: str) -> str:
    if category == "political":
        return "Track policy updates and align operating SOPs to avoid disruptions."
    if category == "economic":
        return "Revisit menu engineering and vendor contracts to protect margins."
    if category == "social":
        return "Align campaign themes with current customer preferences and review tone."
    if category == "technological":
        return "Improve delivery platform performance and digital ordering experience."
    if category == "environmental":
        return "Adopt visible sustainability actions to strengthen brand trust."
    if category == "legal":
        return "Prioritize compliance readiness to reduce penalty risk."
    return f"Monitor this development: {headline[:90]}"


def _signal_confidence(sentiment: str, severity: str, category: str) -> int:
    base = 58
    if sentiment != "Neutral":
        base += 8
    if severity == "High":
        base += 8
    elif severity == "Low":
        base -= 4
    if category == "environmental":
        base -= 6
    return max(45, min(base, 82))


def _categorize_news(news_mentions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    categorized: Dict[str, List[Dict[str, Any]]] = {
        "political": [],
        "economic": [],
        "social": [],
        "technological": [],
        "environmental": [],
        "legal": [],
    }

    for article in news_mentions:
        headline = (article.get("headline") or "").strip()
        tokens = set(_tokenize(headline))
        if not tokens:
            continue

        matched_any = False
        for cat, keys in PESTEL_KEYWORDS.items():
            overlap = len(tokens & set(keys))
            if overlap <= 0:
                continue
            matched_any = True
            sentiment = _detect_sentiment(headline)
            severity = _detect_severity(headline, cat)
            categorized[cat].append(
                {
                    "title": headline,
                    "sentiment": sentiment,
                    "severity": severity,
                    "summary": headline,
                    "implication": _category_implication(cat, sentiment, headline),
                    "source": article.get("source_name") or "Unknown",
                    "source_url": article.get("link"),
                    "confidence_pct": _signal_confidence(sentiment, severity, cat),
                    "overlap": overlap,
                }
            )

        if not matched_any:
            sentiment = _detect_sentiment(headline)
            categorized["social"].append(
                {
                    "title": headline,
                    "sentiment": sentiment,
                    "severity": "Low",
                    "summary": headline,
                    "implication": _category_implication("social", sentiment, headline),
                    "source": article.get("source_name") or "Unknown",
                    "source_url": article.get("link"),
                    "confidence_pct": 50,
                    "overlap": 0,
                }
            )

    return categorized


def _build_review_driven_factors(
    aggregated_absa: List[Dict[str, Any]],
    review_texts: List[str],
    virality_score: int,
) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {
        "social": [],
        "technological": [],
    }

    pos = sum(1 for r in aggregated_absa if r.get("overall_sentiment") == "Positive")
    neg = sum(1 for r in aggregated_absa if r.get("overall_sentiment") == "Negative")
    tone = "Positive" if pos >= neg else "Negative"
    out["social"].append(
        {
            "title": "Customer review tone trend",
            "sentiment": tone,
            "severity": "Medium",
            "summary": f"Review tone indicates {tone.lower()} momentum across key aspects.",
            "implication": "Adjust service and campaign messaging to reflect prevailing customer mood.",
            "source": "Google Maps + Twitter Reviews",
            "source_url": None,
            "confidence_pct": 68,
            "overlap": 1,
        }
    )
    out["social"].append(
        {
            "title": "Social virality signal",
            "sentiment": "Positive" if virality_score >= 50 else "Neutral",
            "severity": "Low" if virality_score >= 50 else "Medium",
            "summary": f"Virality score estimated at {virality_score}% from review source mix.",
            "implication": "Strengthen local creator partnerships if virality remains moderate.",
            "source": "Social/Review Mix",
            "source_url": None,
            "confidence_pct": 62,
            "overlap": 1,
        }
    )

    all_text = " ".join(t.lower() for t in review_texts)
    if "zomato" in all_text or "swiggy" in all_text:
        out["technological"].append(
            {
                "title": "Delivery platform dependency signal",
                "sentiment": "Neutral",
                "severity": "Medium",
                "summary": "Reviews mention delivery platforms (Zomato/Swiggy).",
                "implication": "Improve listing quality, delivery SLAs, and platform conversion funnels.",
                "source": "Google Maps + Twitter Reviews",
                "source_url": None,
                "confidence_pct": 66,
                "overlap": 1,
            }
        )

    return out


def _pick_balanced_factors(
    categorized_news: Dict[str, List[Dict[str, Any]]],
    review_factors: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, List[Dict[str, Any]]]:
    result: Dict[str, List[Dict[str, Any]]] = {}

    for cat, target in CATEGORY_TARGETS.items():
        items = list(categorized_news.get(cat, []))
        if review_factors.get(cat):
            items.extend(review_factors[cat])

        items = sorted(items, key=lambda x: (x.get("overlap", 0), x.get("confidence_pct", 0)), reverse=True)

        selected = items[:target]
        if not selected:
            selected = [
                {
                    "title": f"No strong {cat} signal available",
                    "sentiment": "Neutral",
                    "severity": "Low",
                    "summary": "Limited recent evidence in current data window.",
                    "implication": "Continue monitoring this dimension weekly.",
                    "source": "System",
                    "source_url": None,
                    "confidence_pct": 45,
                }
            ]
        result[cat] = selected

    return result


def generate_pestel_framework(
    aggregated_absa: List[Dict[str, Any]],
    news_mentions: List[Dict[str, Any]],
    review_texts: List[str],
    google_review_count: int,
    twitter_review_count: int,
) -> Dict[str, Any]:
    """
    Generate PESTEL-only output with balanced factors.
    """
    total_reviews = max(1, google_review_count + twitter_review_count)
    virality_score = int(round((twitter_review_count / total_reviews) * 100))

    categorized_news = _categorize_news(news_mentions)
    review_factors = _build_review_driven_factors(aggregated_absa, review_texts, virality_score)
    balanced_factors = _pick_balanced_factors(categorized_news, review_factors)

    category_scores: Dict[str, int] = {}
    for cat, items in balanced_factors.items():
        vals = [int(i.get("confidence_pct", 50)) for i in items]
        score = int(round(sum(vals) / len(vals))) if vals else 50
        if cat == "environmental":
            score = max(45, min(score, 68))
        category_scores[cat] = score

    avg_pestel_score = int(round(sum(category_scores.values()) / len(category_scores))) if category_scores else 55
    total_factors = sum(len(v) for v in balanced_factors.values())

    return {
        "avg_score_pct": avg_pestel_score,
        "factors_count": total_factors,
        "virality_score_pct": virality_score,
        "categories": {
            "political": {
                "score_pct": category_scores.get("political", 55),
                "factor_count": len(balanced_factors.get("political", [])),
                "factors": balanced_factors.get("political", []),
            },
            "economic": {
                "score_pct": category_scores.get("economic", 55),
                "factor_count": len(balanced_factors.get("economic", [])),
                "factors": balanced_factors.get("economic", []),
            },
            "social": {
                "score_pct": category_scores.get("social", 55),
                "factor_count": len(balanced_factors.get("social", [])),
                "factors": balanced_factors.get("social", []),
            },
            "technological": {
                "score_pct": category_scores.get("technological", 55),
                "factor_count": len(balanced_factors.get("technological", [])),
                "factors": balanced_factors.get("technological", []),
            },
            "environmental": {
                "score_pct": category_scores.get("environmental", 48),
                "factor_count": len(balanced_factors.get("environmental", [])),
                "factors": balanced_factors.get("environmental", []),
            },
            "legal": {
                "score_pct": category_scores.get("legal", 55),
                "factor_count": len(balanced_factors.get("legal", [])),
                "factors": balanced_factors.get("legal", []),
            },
        },
    }
