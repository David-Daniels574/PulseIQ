"""
Confidence Scoring Engine
Computes a dynamic compound confidence score (0-100) per aspect
across all sources: Google Maps, Zomato, Instagram, News.

Factors:
  1. Source base weight
  2. Recency (newer = higher weight)
  3. Volume (more mentions = higher confidence)
  4. Cross-source agreement (compounding bonus)
  5. Cross-source conflict (penalty + flag)
  6. Individual model sentiment strength
"""

import math
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# SOURCE BASE WEIGHTS  (0-1)
# ─────────────────────────────────────────────────────────────────────

SOURCE_WEIGHTS = {
    "google_maps": 0.90,
    "zomato":      0.85,
    "instagram":   0.55,
    "news":        0.65,
}

# ─────────────────────────────────────────────────────────────────────
# RECENCY WEIGHT
# Reviews/posts from the last 30 days → 1.0
# Older → decays linearly toward 0.5 at 12 months
# ─────────────────────────────────────────────────────────────────────

def recency_weight(review_date: Optional[datetime], months_back: int = 6) -> float:
    if not review_date:
        return 0.75   # unknown date — use neutral weight
    now = datetime.utcnow()
    age_days = max(0, (now - review_date).days)
    max_days  = months_back * 30
    weight = 1.0 - 0.5 * (age_days / max_days) if max_days > 0 else 1.0
    return max(0.5, min(1.0, weight))


# ─────────────────────────────────────────────────────────────────────
# VOLUME WEIGHT
# 1 mention → 0.4, 5 → 0.65, 10 → 0.75, 30+ → ~1.0
# ─────────────────────────────────────────────────────────────────────

def volume_weight(mention_count: int) -> float:
    if mention_count <= 0:
        return 0.0
    return min(1.0, 0.4 + 0.3 * math.log(mention_count + 1, 10))


# ─────────────────────────────────────────────────────────────────────
# AGREEMENT / CONFLICT DETECTION
# ─────────────────────────────────────────────────────────────────────

def _dominant_sentiment(source_data: Dict[str, Any]) -> Optional[str]:
    return source_data.get("sentiment") or source_data.get("overall_sentiment")


def detect_conflict(
    source_sentiments: Dict[str, str]
) -> Tuple[bool, Optional[str]]:
    """
    Given {source_name: dominant_sentiment}, detect if sources conflict.

    Returns:
        (conflict: bool, detail: str | None)
    """
    if len(source_sentiments) < 2:
        return False, None

    sentiments = set(source_sentiments.values())
    strong = {s for s in sentiments if s in ("Positive", "Negative")}

    if "Positive" in strong and "Negative" in strong:
        parts = [f"{src}: {sent}" for src, sent in source_sentiments.items()]
        detail = " vs ".join(parts)
        return True, detail

    return False, None


# ─────────────────────────────────────────────────────────────────────
# COMPOUNDING BONUS
# ─────────────────────────────────────────────────────────────────────

def agreement_bonus(agreeing_sources: int) -> float:
    """
    agreeing_sources: number of sources with the SAME dominant sentiment
    1 → 0.0 bonus, 2 → 0.07, 3 → 0.12, 4 → 0.15
    """
    if agreeing_sources <= 1:
        return 0.0
    return min(0.15, 0.07 * (agreeing_sources - 1))


# ─────────────────────────────────────────────────────────────────────
# CONFLICT PENALTY
# ─────────────────────────────────────────────────────────────────────

CONFLICT_PENALTY = 0.15


# ─────────────────────────────────────────────────────────────────────
# COMPUTE COMPOUND SCORE FOR ONE ASPECT ACROSS ALL SOURCES
# ─────────────────────────────────────────────────────────────────────

def compute_aspect_confidence(
    aspect: str,
    source_data: Dict[str, Dict[str, Any]],
    months_back: int = 6,
) -> Dict[str, Any]:
    """
    Compute a compound confidence score for a single aspect.

    Args:
        aspect: e.g. "Food", "Service"
        source_data: {
            "google_maps": {
                "sentiment": "Positive",
                "avg_model_score": 0.88,
                "mention_count": 12,
                "avg_review_date": <datetime> | None
            },
            ...
        }
        months_back: for recency calculation

    Returns dict with confidence_score (0-100), overall_sentiment, breakdown, flags.
    """
    if not source_data:
        return {
            "aspect": aspect,
            "overall_sentiment": "Neutral",
            "confidence_score": 0.0,
            "source_breakdown": {},
            "conflict_flag": False,
            "conflict_detail": None,
            "agreeing_sources": 0,
        }

    # ── Step 1: Per-source weighted scores ────────────────────────
    per_source_scores: Dict[str, float] = {}
    source_sentiments: Dict[str, str]   = {}

    for source, data in source_data.items():
        base_w   = SOURCE_WEIGHTS.get(source, 0.6)
        model_s  = float(data.get("avg_model_score", 0.7))
        mentions = int(data.get("mention_count", 1))
        avg_date = data.get("avg_review_date")

        rec_w = recency_weight(avg_date, months_back)
        vol_w = volume_weight(mentions)

        raw = base_w * rec_w * vol_w * model_s
        per_source_scores[source] = raw

        sentiment = _dominant_sentiment(data) or "Neutral"
        source_sentiments[source] = sentiment

    # ── Step 2: Conflict detection ────────────────────────────────
    conflict, conflict_detail = detect_conflict(source_sentiments)

    # ── Step 3: Dominant sentiment (majority vote) ────────────────
    sentiment_votes: Dict[str, int] = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for sent in source_sentiments.values():
        sentiment_votes[sent] = sentiment_votes.get(sent, 0) + 1
    overall_sentiment = max(sentiment_votes, key=lambda k: sentiment_votes[k])

    # ── Step 4: Agreement bonus ───────────────────────────────────
    agreeing = sum(1 for s in source_sentiments.values() if s == overall_sentiment)
    bonus    = agreement_bonus(agreeing)

    # ── Step 5: Weighted average of per-source scores ─────────────
    total_weight = sum(SOURCE_WEIGHTS.get(src, 0.6) for src in source_data)
    if total_weight == 0:
        raw_avg = 0.0
    else:
        raw_avg = sum(
            per_source_scores[src] * SOURCE_WEIGHTS.get(src, 0.6)
            for src in source_data
        ) / total_weight

    # ── Step 6: Apply bonus and conflict penalty ──────────────────
    raw_avg += bonus
    if conflict:
        raw_avg -= CONFLICT_PENALTY

    # ── Step 7: Scale to 0-100 ────────────────────────────────────
    confidence_score = round(max(0.0, min(100.0, raw_avg * 100)), 1)

    return {
        "aspect":            aspect,
        "overall_sentiment": overall_sentiment,
        "confidence_score":  confidence_score,
        "source_breakdown":  {
            src: {
                "sentiment":     source_sentiments[src],
                "raw_score":     round(per_source_scores[src], 4),
                "mention_count": source_data[src].get("mention_count", 0),
            }
            for src in source_data
        },
        "conflict_flag":    conflict,
        "conflict_detail":  conflict_detail,
        "agreeing_sources": agreeing,
    }


# ─────────────────────────────────────────────────────────────────────
# AGGREGATE ACROSS ALL ASPECTS
# ─────────────────────────────────────────────────────────────────────

def compute_all_aspect_confidence(
    gmap_absa:   Dict[str, Any],
    zomato_absa: Dict[str, Any],
    insta_absa:  Dict[str, Any],
    months_back: int = 6,
) -> List[Dict[str, Any]]:
    """
    Given ABSA results from all three sources, compute compound
    confidence for every aspect that appears in at least one source.

    Args:
        gmap_absa:   output of analyze_multiple_reviews()  (Google Maps)
        zomato_absa: output of analyze_multiple_reviews()  (Zomato)
        insta_absa:  output of analyze_multiple_reviews()  (Instagram captions)
        months_back: for recency weighting

    Returns:
        List of per-aspect confidence dicts (sorted by confidence desc)
    """

    def extract_source_data(absa: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for aspect, data in absa.items():
            if not isinstance(data, dict):
                continue
            result[aspect] = {
                "sentiment":       data.get("overall_sentiment", "Neutral"),
                "avg_model_score": data.get("average_confidence", 0.7),
                "mention_count":   data.get("total_mentions", 0),
                "avg_review_date": None,   # per-source avg date not available here
            }
        return result

    gmap_by_aspect   = extract_source_data(gmap_absa)
    zomato_by_aspect = extract_source_data(zomato_absa)
    insta_by_aspect  = extract_source_data(insta_absa)

    all_aspects = (
        set(gmap_by_aspect.keys()) |
        set(zomato_by_aspect.keys()) |
        set(insta_by_aspect.keys())
    )

    results: List[Dict[str, Any]] = []
    for aspect in sorted(all_aspects):
        source_data: Dict[str, Dict[str, Any]] = {}
        if aspect in gmap_by_aspect:
            source_data["google_maps"] = gmap_by_aspect[aspect]
        if aspect in zomato_by_aspect:
            source_data["zomato"] = zomato_by_aspect[aspect]
        if aspect in insta_by_aspect:
            source_data["instagram"] = insta_by_aspect[aspect]

        conf = compute_aspect_confidence(aspect, source_data, months_back)
        results.append(conf)

    results.sort(key=lambda x: x["confidence_score"], reverse=True)
    return results


# ─────────────────────────────────────────────────────────────────────
# SENTIMENT VARIANCE (for Six Sigma)
# ─────────────────────────────────────────────────────────────────────

def compute_sentiment_variance(
    aggregated_aspects: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    For each aspect, compute variance in per-source raw_scores.
    High variance = inconsistency = Six Sigma defect signal.

    Returns:
        { "Food": 0.24, "Service": 0.08, ... }
    """
    variances: Dict[str, float] = {}

    for item in aggregated_aspects:
        aspect = item["aspect"]
        breakdown = item.get("source_breakdown", {})
        raw_scores = [v["raw_score"] for v in breakdown.values() if "raw_score" in v]

        if len(raw_scores) < 2:
            variances[aspect] = 0.0
        else:
            try:
                variances[aspect] = round(statistics.variance(raw_scores), 4)
            except Exception:
                variances[aspect] = 0.0

    return variances


# ─────────────────────────────────────────────────────────────────────
# MECE CLUSTERING
# Group similar complaint sentences into clusters before Gemini call
# ─────────────────────────────────────────────────────────────────────

def cluster_complaints(
    negative_sentences: List[Dict[str, Any]],
    similarity_threshold: float = 0.6,
) -> List[Dict[str, Any]]:
    """
    Cluster semantically similar negative sentences into MECE buckets.
    Uses TF-IDF cosine similarity (no GPU needed, fast).

    Args:
        negative_sentences: List of {sentence, aspect, source, confidence}
        similarity_threshold: cosine similarity above which sentences are grouped

    Returns:
        List of clusters: [{
            "cluster_label": str,
            "sentences": [...],
            "count": int,
            "aspects": [...],
            "sources": [...]
        }]
    """
    if not negative_sentences:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        texts = [s["sentence"] for s in negative_sentences]

        vectorizer   = TfidfVectorizer(stop_words="english", max_features=200)
        tfidf_matrix = vectorizer.fit_transform(texts)
        sim_matrix   = cosine_similarity(tfidf_matrix)

        visited  = [False] * len(texts)
        clusters: List[Dict[str, Any]] = []

        for i in range(len(texts)):
            if visited[i]:
                continue
            cluster_indices = [i]
            visited[i] = True
            for j in range(i + 1, len(texts)):
                if not visited[j] and sim_matrix[i][j] >= similarity_threshold:
                    cluster_indices.append(j)
                    visited[j] = True

            cluster_sentences = [negative_sentences[k] for k in cluster_indices]
            aspects = list({s.get("aspect", "General") for s in cluster_sentences})
            sources = list({s.get("source", "unknown") for s in cluster_sentences})

            label_sentence = max(
                cluster_sentences,
                key=lambda s: s.get("confidence", 0),
            )["sentence"]
            label = (label_sentence[:80] + "...") if len(label_sentence) > 80 else label_sentence

            clusters.append({
                "cluster_label": label,
                "sentences":     [s["sentence"] for s in cluster_sentences],
                "count":         len(cluster_sentences),
                "aspects":       aspects,
                "sources":       sources,
            })

        clusters.sort(key=lambda c: c["count"], reverse=True)
        logger.info(
            f"MECE clustering: {len(negative_sentences)} sentences → {len(clusters)} clusters"
        )
        return clusters

    except Exception as e:
        logger.warning(f"MECE clustering failed: {e} — returning ungrouped")
        return [
            {
                "cluster_label": s["sentence"][:80],
                "sentences":     [s["sentence"]],
                "count":         1,
                "aspects":       [s.get("aspect", "General")],
                "sources":       [s.get("source", "unknown")],
            }
            for s in negative_sentences
        ]