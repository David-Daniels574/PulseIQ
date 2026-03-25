"""
SWOT-first agentic pipeline using LangChain + Gemini.

This module turns ABSA/confidence signals into owner-facing SWOT points,
then attaches exactly one best citation per point from available evidence.
"""

from __future__ import annotations

import json
import logging
import os
from statistics import mean
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

from services.framework_llm import validate_swot_with_citations


def _tokenize(text: str) -> List[str]:
    return [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if len(t) >= 4]


def _source_strength(source_type: str) -> str:
    source_type = (source_type or "").lower()
    if source_type in {"google_maps", "news"}:
        return "High"
    if source_type == "twitter":
        return "Medium"
    return "Low"


def _point_confidence(base_conf: float, evidence_relevance: float, has_conflict: bool) -> int:
    penalty = 10.0 if has_conflict else 0.0
    score = (0.75 * base_conf) + (25.0 * evidence_relevance) - penalty
    score = max(0.0, min(100.0, score))
    return int(round(score))


def _candidate_from_aspect(aspect_row: Dict[str, Any]) -> Dict[str, Any]:
    aspect = aspect_row.get("aspect", "General")
    sentiment = str(aspect_row.get("overall_sentiment", "Neutral"))
    confidence = float(aspect_row.get("confidence_score") or 0.0)
    conflict_flag = bool(aspect_row.get("conflict_flag", False))

    reason = f"{aspect} sentiment is {sentiment.lower()} with confidence {confidence:.1f}%"
    return {
        "aspect": aspect,
        "sentiment": sentiment,
        "base_confidence": confidence,
        "conflict": conflict_flag,
        "reason": reason,
    }


def _build_swot_candidates(
    aggregated_absa: List[Dict[str, Any]],
    competitor_summaries: List[Dict[str, Any]],
    news_mentions: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    strengths: List[Dict[str, Any]] = []
    weaknesses: List[Dict[str, Any]] = []

    for row in aggregated_absa:
        c = _candidate_from_aspect(row)
        if c["sentiment"] == "Positive":
            strengths.append(c)
        elif c["sentiment"] == "Negative":
            weaknesses.append(c)

    strengths = sorted(strengths, key=lambda x: x["base_confidence"], reverse=True)[:3]
    weaknesses = sorted(weaknesses, key=lambda x: x["base_confidence"], reverse=True)[:3]

    opportunities: List[Dict[str, Any]] = []
    threats: List[Dict[str, Any]] = []

    for comp in competitor_summaries[:5]:
        comp_name = comp.get("name") or comp.get("competitor_name") or "Competitor"
        comp_rating = float(comp.get("rating") or comp.get("competitor_rating") or 0.0)
        rating_delta = float(comp.get("rating_difference") or 0.0)

        if rating_delta > 0:
            opportunities.append(
                {
                    "aspect": "Competitive Gap",
                    "sentiment": "Positive",
                    "base_confidence": min(95.0, 60.0 + abs(rating_delta) * 10.0),
                    "conflict": False,
                    "reason": f"{comp_name} trails by {rating_delta:.2f} rating points; room to capture share.",
                }
            )
        elif comp_rating > 0:
            threats.append(
                {
                    "aspect": "Competitive Pressure",
                    "sentiment": "Negative",
                    "base_confidence": min(95.0, 55.0 + comp_rating * 8.0),
                    "conflict": False,
                    "reason": f"{comp_name} shows strong customer pull; risk of customer leakage.",
                }
            )

    threat_keywords = {
        "inflation", "lpg", "crisis", "price", "hike", "disruption", "slowdown", "tax", "compliance", "shortage"
    }
    opportunity_keywords = {
        "growth", "demand", "trend", "festival", "recovery", "premium", "delivery", "digital", "expansion"
    }

    for article in news_mentions[:20]:
        headline = str(article.get("headline", ""))
        head_tokens = set(_tokenize(headline))
        if not head_tokens:
            continue

        if head_tokens & threat_keywords:
            threats.append(
                {
                    "aspect": "Industry Risk",
                    "sentiment": "Negative",
                    "base_confidence": 70.0,
                    "conflict": False,
                    "reason": f"Market signal from news: {headline}",
                }
            )
        elif head_tokens & opportunity_keywords:
            opportunities.append(
                {
                    "aspect": "Market Opportunity",
                    "sentiment": "Positive",
                    "base_confidence": 68.0,
                    "conflict": False,
                    "reason": f"Positive market signal in news: {headline}",
                }
            )

    opportunities = sorted(opportunities, key=lambda x: x["base_confidence"], reverse=True)[:3]
    threats = sorted(threats, key=lambda x: x["base_confidence"], reverse=True)[:3]

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
    }


def _pick_best_citation(point_text: str, evidence_items: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
    ptoks = set(_tokenize(point_text))
    best = None
    best_score = -1.0

    for item in evidence_items:
        quote = item.get("quote", "")
        etoks = set(_tokenize(quote))
        if not etoks:
            continue

        overlap = len(ptoks & etoks)
        union = max(1, len(ptoks | etoks))
        relevance = overlap / union

        src_boost = 0.05 if item.get("source_type") == "google_maps" else 0.0
        score = relevance + src_boost
        if score > best_score:
            best_score = score
            best = item

    if best is None and evidence_items:
        best = evidence_items[0]
        best_score = 0.1

    return best or {
        "source_type": "news",
        "quote": "Limited source evidence available for this point.",
        "source_reference": "system_fallback",
        "source_url": None,
    }, best_score


def _build_evidence_items(
    review_evidence: List[Dict[str, Any]],
    news_mentions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []

    for r in review_evidence:
        source_type = r.get("source", "google_maps")
        text = str(r.get("text") or "").strip()
        if not text:
            continue
        evidence.append(
            {
                "source_type": source_type,
                "quote": text,
                "source_reference": r.get("source_reference") or r.get("author") or source_type,
                "source_url": r.get("source_url"),
            }
        )

    for n in news_mentions:
        headline = str(n.get("headline") or "").strip()
        if not headline:
            continue
        evidence.append(
            {
                "source_type": "news",
                "quote": headline,
                "source_reference": n.get("source_name") or "news",
                "source_url": n.get("link"),
            }
        )

    return evidence


def _synthesize_with_langchain(
    business_name: str,
    city: str,
    candidates: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Use LangChain + Gemini to convert candidate facts into strategic phrasing."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not configured")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are a senior restaurant strategy consultant.
Turn SWOT candidate facts into concise owner-ready strategic suggestions.
Business: {business_name}
City: {city}

Candidate facts JSON:
{candidates_json}

Return ONLY valid JSON in this exact shape:
{{
  "strengths": [{{"label":"...","suggestion":"...","derived_insight":"..."}}],
  "weaknesses": [{{"label":"...","suggestion":"...","derived_insight":"..."}}],
  "opportunities": [{{"label":"...","suggestion":"...","derived_insight":"..."}}],
  "threats": [{{"label":"...","suggestion":"...","derived_insight":"..."}}]
}}

Rules:
- Use only candidate facts. Do not invent external data.
- Keep each suggestion practical and specific to operations/marketing.
- Keep each derived_insight to one sentence.
""".strip()
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "business_name": business_name,
            "city": city,
            "candidates_json": json.dumps(candidates, indent=2),
        }
    )

    raw = (response.content or "").strip()
    if raw.startswith("```"):
        parts = raw.split("\n")
        parts = parts[1:] if parts and parts[0].startswith("```") else parts
        parts = parts[:-1] if parts and parts[-1].strip() == "```" else parts
        raw = "\n".join(parts).strip()

    data = json.loads(raw)
    for k in ["strengths", "weaknesses", "opportunities", "threats"]:
        data.setdefault(k, [])
    return data


def generate_agentic_swot(
    business_name: str,
    city: str,
    aggregated_absa: List[Dict[str, Any]],
    competitor_summaries: List[Dict[str, Any]],
    news_mentions: List[Dict[str, Any]],
    review_evidence: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate SWOT with one best citation per point.

    Output includes:
    - framework-level confidence (example: 84)
    - SWOT JSON with source citation per point
    - flattened citation rows for DB persistence
    """
    candidates = _build_swot_candidates(aggregated_absa, competitor_summaries, news_mentions)
    evidence_items = _build_evidence_items(review_evidence, news_mentions)

    try:
        synthesized = _synthesize_with_langchain(business_name, city, candidates)
    except Exception as exc:
        logger.warning("LangChain SWOT synthesis failed, using deterministic fallback: %s", exc)
        synthesized = {
            quadrant: [
                {
                    "label": c.get("aspect", "General"),
                    "suggestion": c.get("reason", ""),
                    "derived_insight": c.get("reason", ""),
                }
                for c in rows
            ]
            for quadrant, rows in candidates.items()
        }

    result_swot: Dict[str, List[Dict[str, Any]]] = {
        "strengths": [],
        "weaknesses": [],
        "opportunities": [],
        "threats": [],
    }
    citations_for_db: List[Dict[str, Any]] = []
    confidence_values: List[int] = []

    for quadrant in ["strengths", "weaknesses", "opportunities", "threats"]:
        base_rows = candidates.get(quadrant, [])
        phrased_rows = synthesized.get(quadrant, []) if isinstance(synthesized, dict) else []

        for idx, base in enumerate(base_rows, start=1):
            phrased = phrased_rows[idx - 1] if idx - 1 < len(phrased_rows) else {}
            label = str(phrased.get("label") or base.get("aspect") or quadrant.title())
            suggestion = str(phrased.get("suggestion") or base.get("reason") or "")
            derived_insight = str(phrased.get("derived_insight") or base.get("reason") or "")

            best_citation, relevance = _pick_best_citation(
                point_text=f"{label} {suggestion} {derived_insight}",
                evidence_items=evidence_items,
            )
            confidence_pct = _point_confidence(
                base_conf=float(base.get("base_confidence") or 0.0),
                evidence_relevance=float(relevance),
                has_conflict=bool(base.get("conflict", False)),
            )
            confidence_values.append(confidence_pct)

            point_id = f"swot_{quadrant[:-1]}_{idx}"
            citation_payload = {
                "source_type": best_citation.get("source_type", "news"),
                "source_strength": _source_strength(best_citation.get("source_type", "")),
                "quote": best_citation.get("quote", ""),
                "source_reference": best_citation.get("source_reference"),
                "source_url": best_citation.get("source_url"),
                "insight_derived": derived_insight,
            }

            result_swot[quadrant].append(
                {
                    "point_id": point_id,
                    "label": label,
                    "suggestion": suggestion,
                    "confidence_pct": confidence_pct,
                    "derived_insight": derived_insight,
                    "source_citation": citation_payload,
                }
            )

            citations_for_db.append(
                {
                    "framework": "swot",
                    "quadrant": quadrant,
                    "point_id": point_id,
                    "point_label": label,
                    "confidence_pct": confidence_pct,
                    "suggestion": suggestion,
                    "derived_insight": derived_insight,
                    "source_type": citation_payload["source_type"],
                    "source_strength": citation_payload["source_strength"],
                    "source_quote": citation_payload["quote"],
                    "source_reference": citation_payload["source_reference"],
                    "source_url": citation_payload["source_url"],
                }
            )

    framework_confidence = int(round(mean(confidence_values))) if confidence_values else 0

    validate_swot_with_citations(result_swot)

    return {
        "framework": "swot",
        "confidence_pct": framework_confidence,
        "result_json": result_swot,
        "citations": citations_for_db,
    }
