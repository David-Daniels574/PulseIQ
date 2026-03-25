"""
Agentic MECE framework generation.

Uses pre-clustered complaint buckets from confidence_engine output and asks Gemini
for a final Mutually Exclusive + Collectively Exhaustive categorization.
Falls back to deterministic formatting when Gemini is unavailable.
"""

import json
import logging
from typing import Any, Dict, List

import google.generativeai as genai

logger = logging.getLogger(__name__)


def _clean_json_response(text: str) -> str:
    txt = (text or "").strip()
    if txt.startswith("```"):
        lines = txt.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        txt = "\n".join(lines).strip()
    return txt


def _normalize_clusters(mece_clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []

    for c in mece_clusters or []:
        if not isinstance(c, dict):
            continue

        category = (
            c.get("cluster_label")
            or c.get("category")
            or c.get("cluster")
            or "General Complaints"
        )

        raw_examples = c.get("sentences") or c.get("examples") or []
        if not isinstance(raw_examples, list):
            raw_examples = []

        examples = [str(x).strip() for x in raw_examples if str(x).strip()][:6]

        raw_count = c.get("count")
        if isinstance(raw_count, int):
            count = raw_count
        else:
            count = len(examples)

        sources = c.get("sources") if isinstance(c.get("sources"), list) else []
        aspects = c.get("aspects") if isinstance(c.get("aspects"), list) else []

        normalized.append(
            {
                "category": str(category).strip(),
                "count": int(count),
                "examples": examples,
                "sources": [str(s) for s in sources if str(s).strip()],
                "aspects": [str(a) for a in aspects if str(a).strip()],
            }
        )

    return normalized


def _deterministic_mece(
    normalized_clusters: List[Dict[str, Any]],
    product_focus: str,
) -> Dict[str, Any]:
    categories: List[Dict[str, Any]] = []

    for c in normalized_clusters:
        count = int(c.get("count") or 0)
        confidence = max(45, min(92, 45 + count * 3))
        cat_name = c.get("category") or "General Complaints"

        categories.append(
            {
                "category": cat_name,
                "description": (
                    f"Customer complaints grouped under {cat_name} impacting {product_focus} "
                    "experience and repeat intent."
                ),
                "count": count,
                "examples": c.get("examples", [])[:4],
                "confidence": confidence,
                "sources": c.get("sources", ["google_maps", "twitter"]),
            }
        )

    avg = round(sum(x["confidence"] for x in categories) / len(categories), 1) if categories else 0.0
    return {
        "complaint_categories": categories,
        "is_exhaustive_note": (
            "Categories derived from all pre-clustered negative sentences; no uncovered complaint theme detected."
            if categories
            else "No complaint clusters found for the selected period."
        ),
        "product_focus": product_focus,
        "avg_score_pct": avg,
    }


def _validate_mece_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("MECE response is not an object")

    categories = data.get("complaint_categories", [])
    if not isinstance(categories, list):
        raise ValueError("MECE complaint_categories must be a list")

    out_categories: List[Dict[str, Any]] = []
    for item in categories:
        if not isinstance(item, dict):
            continue
        out_categories.append(
            {
                "category": str(item.get("category", "General Complaints")),
                "description": str(item.get("description", "")),
                "count": int(item.get("count", 0) or 0),
                "examples": [str(x) for x in (item.get("examples") or [])][:4],
                "confidence": max(0, min(100, int(item.get("confidence", 60) or 60))),
                "sources": [str(x) for x in (item.get("sources") or ["google_maps", "twitter"])],
            }
        )

    avg = round(sum(x["confidence"] for x in out_categories) / len(out_categories), 1) if out_categories else 0.0
    return {
        "complaint_categories": out_categories,
        "is_exhaustive_note": str(data.get("is_exhaustive_note", "")),
        "product_focus": str(data.get("product_focus", "pizzas")),
        "avg_score_pct": avg,
    }


def generate_mece_framework(
    business_name: str,
    city: str,
    mece_clusters: List[Dict[str, Any]],
    product_focus: str = "pizzas",
) -> Dict[str, Any]:
    normalized = _normalize_clusters(mece_clusters)
    if not normalized:
        return _deterministic_mece([], product_focus=product_focus)

    prompt = (
        "You are a strategy consultant.\n"
        "Refine the pre-clustered complaint buckets into a final MECE framework.\n"
        "MECE means: Mutually Exclusive (no overlap) and Collectively Exhaustive (all complaint themes covered).\n"
        f"Business: {business_name}, City: {city}, Product focus: {product_focus}.\n\n"
        "Input pre-clustered buckets (JSON):\n"
        f"{json.dumps(normalized, indent=2)}\n\n"
        "Return ONLY JSON in this exact shape:\n"
        "{\n"
        "  \"complaint_categories\": [\n"
        "    {\n"
        "      \"category\": \"...\",\n"
        "      \"description\": \"...\",\n"
        "      \"count\": 0,\n"
        "      \"examples\": [\"...\"],\n"
        "      \"confidence\": 0,\n"
        "      \"sources\": [\"google_maps\", \"twitter\"]\n"
        "    }\n"
        "  ],\n"
        "  \"is_exhaustive_note\": \"...\",\n"
        "  \"product_focus\": \""
        + product_focus
        + "\"\n"
        "}\n"
        "Rules:\n"
        "- Use only the given input clusters and examples.\n"
        "- You may merge/rename categories to improve MECE quality.\n"
        "- Do not invent unsupported complaint themes.\n"
    )

    try:
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "response_mime_type": "application/json",
            },
        )
        response = model.generate_content(prompt)
        parsed = json.loads(_clean_json_response(response.text))
        validated = _validate_mece_payload(parsed)
        validated["product_focus"] = product_focus
        return validated
    except Exception as e:
        logger.warning(f"MECE Gemini refinement failed, using deterministic fallback: {e}")
        return _deterministic_mece(normalized, product_focus=product_focus)
