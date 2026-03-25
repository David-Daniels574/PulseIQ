"""
AirTop client for fetching multi-source review data.

This module enforces strict JSON validation to reduce hallucinated content:
- Keeps only reviews that include non-empty review text and a valid http(s) link.
- Normalizes source labels so they can be persisted safely in the reviews table.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.airtop.ai/api/hooks/agents"


class AirtopError(Exception):
    """Raised when AirTop invocation fails or returns invalid payload."""


def _env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise AirtopError(f"Missing required env var: {name}")
    return value


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _coerce_output(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        txt = raw.strip()
        # Some agents wrap JSON in markdown fences. Strip them safely.
        if txt.startswith("```"):
            txt = re.sub(r"^```[a-zA-Z0-9_\-]*\s*", "", txt)
            txt = re.sub(r"\s*```$", "", txt)
        try:
            parsed = json.loads(txt)
            if isinstance(parsed, dict):
                return parsed
        except Exception as exc:
            raise AirtopError(f"AirTop output is not valid JSON: {exc}") from exc
    raise AirtopError("AirTop output must be a JSON object")


def _pick(d: Dict[str, Any], keys: List[str]) -> Any:
    for key in keys:
        if key in d and d[key] not in (None, ""):
            return d[key]
    return None


def _normalize_source(raw_source: Optional[str]) -> str:
    text = (raw_source or "airtop").strip().lower()
    text = re.sub(r"[^a-z0-9_\-]", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        text = "airtop"
    # Keep DB-safe source values within the reviews.source length budget.
    return text[:45]


def _parse_review_date(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value)
        except Exception:
            return None
    if isinstance(value, str):
        txt = value.strip()
        if not txt:
            return None
        for candidate in (txt, txt.replace("Z", "+00:00")):
            try:
                return datetime.fromisoformat(candidate)
            except Exception:
                pass
    return None


def _is_valid_url(value: Optional[str]) -> bool:
    if not value or not isinstance(value, str):
        return False
    v = value.strip().lower()
    return v.startswith("http://") or v.startswith("https://")


def trigger_agent(config_vars: Dict[str, Any], timeout_sec: int = 30) -> str:
    api_key = _env("AIRTOP_API_KEY")
    agent_id = _env("AGENT_ID")
    webhook_id = _env("WEBHOOK_ID")

    url = f"{BASE_URL}/{agent_id}/webhooks/{webhook_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    res = requests.post(url, headers=headers, json={"configVars": config_vars}, timeout=timeout_sec)
    if res.status_code >= 400:
        raise AirtopError(f"AirTop trigger failed: HTTP {res.status_code} - {res.text[:300]}")

    payload = res.json()
    invocation_id = payload.get("invocationId")
    if not invocation_id:
        raise AirtopError("AirTop trigger response missing invocationId")
    return invocation_id


def get_result(
    invocation_id: str,
    max_wait_seconds: int = 180,
    interval_sec: float = 2.0,
) -> Dict[str, Any]:
    api_key = _env("AIRTOP_API_KEY")
    agent_id = _env("AGENT_ID")

    url = f"{BASE_URL}/{agent_id}/invocations/{invocation_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    max_attempts = max(1, int(max_wait_seconds / max(interval_sec, 0.5)))
    logger.info(
        "AirTop polling started | invocation_id=%s | max_wait_seconds=%s | interval_sec=%.1f | max_attempts=%s",
        invocation_id,
        max_wait_seconds,
        interval_sec,
        max_attempts,
    )

    last_payload: Dict[str, Any] = {}
    started_at = time.time()
    for attempt in range(1, max_attempts + 1):
        res = requests.get(url, headers=headers, timeout=30)
        if res.status_code >= 400:
            raise AirtopError(f"AirTop result failed: HTTP {res.status_code} - {res.text[:300]}")

        payload = res.json()
        last_payload = payload if isinstance(payload, dict) else {}
        status = str(last_payload.get("status", "")).lower()
        elapsed = int(time.time() - started_at)
        logger.info(
            "AirTop poll | invocation_id=%s | attempt=%s/%s | elapsed_s=%s | status=%s",
            invocation_id,
            attempt,
            max_attempts,
            elapsed,
            last_payload.get("status"),
        )
        if status in {"completed", "succeeded", "success"}:
            output = last_payload.get("output", {})
            logger.info("AirTop completed | invocation_id=%s", invocation_id)
            return _coerce_output(output)
        if status in {"failed", "error", "cancelled"}:
            raise AirtopError(f"AirTop invocation failed with status: {last_payload.get('status')}")

        time.sleep(interval_sec)

    raise AirtopError(
        "AirTop invocation timed out. "
        f"invocation_id={invocation_id}, "
        f"last_status={last_payload.get('status')}, "
        f"max_wait_seconds={max_wait_seconds}."
    )


def normalize_reviews(raw_reviews: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw_reviews, list):
        return []

    normalized: List[Dict[str, Any]] = []
    seen_pairs = set()

    for item in raw_reviews:
        if not isinstance(item, dict):
            continue

        review_text = _pick(
            item,
            ["review_text", "reviewText", "text", "review", "content", "body", "comment"],
        )
        review_url = _pick(
            item,
            ["review_url", "reviewUrl", "url", "link", "source_url", "sourceUrl", "review_link", "permalink", "href"],
        )
        if not review_text or not isinstance(review_text, str):
            continue
        if not _is_valid_url(review_url):
            continue

        text = review_text.strip()
        url = str(review_url).strip()
        if len(text) < 5:
            continue

        fingerprint = (text[:180].lower(), url.lower())
        if fingerprint in seen_pairs:
            continue
        seen_pairs.add(fingerprint)

        source_raw = _pick(item, ["source", "platform", "source_name", "sourceName", "site"]) or "airtop"
        source = _normalize_source(str(source_raw))

        normalized.append(
            {
                "text": text,
                "link": url,
                "source": source,
                "source_raw": str(source_raw),
                "author_name": _pick(item, ["author", "author_name", "authorName", "user", "username", "user_name"]),
                "rating": _pick(item, ["rating", "stars", "score", "star_rating", "starRating"]),
                "review_date": _parse_review_date(
                    _pick(item, ["review_date", "reviewDate", "date", "created_at", "createdAt", "timestamp"])
                ),
            }
        )

    return normalized


def _extract_raw_reviews(output: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Accept common top-level and nested shapes from agent outputs.
    candidates = [
        output.get("reviews"),
        output.get("data", {}).get("reviews") if isinstance(output.get("data"), dict) else None,
        output.get("result", {}).get("reviews") if isinstance(output.get("result"), dict) else None,
        output.get("output", {}).get("reviews") if isinstance(output.get("output"), dict) else None,
    ]
    for value in candidates:
        if isinstance(value, list):
            return value
    return []


def fetch_airtop_reviews_for_business(
    business_name: str,
    review_source_url: str,
    city: str,
) -> Dict[str, Any]:
    """
    Trigger AirTop agent and return validated, normalized review data.

    Important: this webhook enforces a strict config schema and currently
    requires restaurant_name, zomato_url, and city.
    The URL value can point to any review/listing service.
    """
    if not (review_source_url or "").strip():
        raise AirtopError("Missing review_source_url for AirTop webhook invocation")
    if not _is_valid_url(review_source_url):
        raise AirtopError("review_source_url must be an absolute http(s) URL")

    config_vars = {
        "restaurant_name": business_name,
        # Webhook contract requires this key name.
        "zomato_url": review_source_url.strip(),
        "city": (city or "").strip(),
    }

    invocation_id = trigger_agent(config_vars)
    logger.info(
        "AirTop triggered | invocation_id=%s | restaurant_name=%s | city=%s",
        invocation_id,
        business_name,
        city,
    )

    max_wait_seconds = _env_int("AIRTOP_MAX_WAIT_SECONDS", 180)
    poll_interval_seconds = float(_env_int("AIRTOP_POLL_INTERVAL_SECONDS", 2))
    output = get_result(
        invocation_id,
        max_wait_seconds=max_wait_seconds,
        interval_sec=poll_interval_seconds,
    )

    raw_reviews = _extract_raw_reviews(output)
    normalized = normalize_reviews(raw_reviews)
    logger.info(
        "AirTop parsed output | invocation_id=%s | raw_review_count=%s | valid_review_count=%s",
        invocation_id,
        len(raw_reviews) if isinstance(raw_reviews, list) else 0,
        len(normalized),
    )

    return {
        "invocation_id": invocation_id,
        "business_name": (
            output.get("business_name")
            or (output.get("data", {}).get("business_name") if isinstance(output.get("data"), dict) else None)
            or business_name
        ),
        "reviews": normalized,
        "metadata": (
            output.get("metadata")
            if isinstance(output.get("metadata"), dict)
            else (output.get("data", {}).get("metadata") if isinstance(output.get("data"), dict) else {})
        ),
        "raw_review_count": len(raw_reviews) if isinstance(raw_reviews, list) else 0,
        "valid_review_count": len(normalized),
    }
