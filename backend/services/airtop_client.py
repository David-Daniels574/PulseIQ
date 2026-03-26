"""
AirTop agent result client.

Fetches invocation result payload and normalizes reviews into a common schema:
{
  "text": str,
  "author_name": Optional[str],
  "rating": Optional[float],
  "source": "airtop",
  "source_url": Optional[str],
}
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


def fetch_airtop_invocation_result(
    *,
    api_key: str,
    agent_id: str,
    invocation_id: str,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """Fetch raw AirTop invocation result JSON."""
    url = (
        f"https://api.airtop.ai/api/hooks/agents/{agent_id}/"
        f"invocations/{invocation_id}/result"
    )
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=timeout_seconds,
    )
    resp.raise_for_status()
    return resp.json()


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _extract_reviews_from_any(obj: Any) -> List[Dict[str, Any]]:
    """
    Best-effort recursive extractor for review-like records.
    Handles varying agent payload shapes.
    """
    out: List[Dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
            return

        if not isinstance(node, dict):
            return

        text = (
            node.get("text")
            or node.get("review_text")
            or node.get("content")
            or node.get("comment")
            or node.get("body")
        )

        if isinstance(text, str) and text.strip():
            raw_source = (
                node.get("source")
                or node.get("platform")
                or node.get("site")
                or node.get("origin")
            )
            out.append(
                {
                    "text": text.strip(),
                    "author_name": (
                        node.get("author_name")
                        or node.get("author")
                        or node.get("user")
                        or node.get("username")
                    ),
                    "rating": _to_float(node.get("rating") or node.get("stars") or node.get("score")),
                    "source": "airtop",
                    "source_name": (str(raw_source).strip() if raw_source else "AirTop"),
                    "source_url": node.get("link") or node.get("url") or node.get("source_url"),
                }
            )

        for v in node.values():
            walk(v)

    walk(obj)
    return out


def normalize_airtop_reviews(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalize and deduplicate review records from an AirTop result payload."""
    raw = _extract_reviews_from_any(payload)

    seen = set()
    deduped: List[Dict[str, Any]] = []
    for r in raw:
        key = r.get("text", "")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    logger.info("AirTop normalization complete: %d reviews", len(deduped))
    return deduped
