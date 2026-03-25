"""
Instagram Scraper Service
Strategy:
  1. instagrapi (unofficial Instagram private API wrapper) — primary
  2. requests-html / BeautifulSoup on public hashtag pages — fallback

Searches by restaurant-specific hashtags only.
Scrapes: captions, like count, comment count, post date, post URL.
Post count across all searched hashtags → virality index.
"""

import time
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# HASHTAG GENERATION
# ─────────────────────────────────────────────────────────────────────

def generate_hashtags(restaurant_name: str, area: str, city: str) -> List[str]:
    """
    Generate restaurant-specific hashtag variants to search.
    Keeps them tight — no area-level noise tags.

    e.g. "Leopold Cafe", "Colaba", "Mumbai"
    →  ["leopoldcafe", "leopoldcafemumbai", "leopoldcafecolaba",
        "leopoldcafebar", "leopoldcafeandbar"]
    """
    # Normalise
    name_slug  = re.sub(r"[^a-z0-9]", "", restaurant_name.lower())
    area_slug  = re.sub(r"[^a-z0-9]", "", area.lower())
    city_slug  = re.sub(r"[^a-z0-9]", "", city.lower())

    # Remove common generic words that would explode the search
    stop_words = {"restaurant", "cafe", "bar", "grill", "kitchen",
                  "food", "house", "the", "and", "&"}

    name_words = [w for w in re.split(r"\s+", restaurant_name.lower())
                  if w not in stop_words and len(w) > 1]
    core_slug  = re.sub(r"[^a-z0-9]", "", "".join(name_words))

    tags = set()

    # Primary: full name
    tags.add(name_slug)
    tags.add(f"{name_slug}{city_slug}")
    tags.add(f"{name_slug}{area_slug}")

    # Core (without stop words)
    if core_slug and core_slug != name_slug:
        tags.add(core_slug)
        tags.add(f"{core_slug}{city_slug}")

    # Common suffix variants
    for suffix in ["bar", "cafe", "restaurant", "mumbai"]:
        if suffix not in name_slug:
            tags.add(f"{name_slug}{suffix}")

    # Remove empty / very short tags
    tags = {t for t in tags if len(t) >= 4}

    logger.info(f"Generated hashtags for '{restaurant_name}': {sorted(tags)}")
    return sorted(tags)


# ─────────────────────────────────────────────────────────────────────
# PRIMARY: instagrapi  (unofficial, no official API needed)
# ─────────────────────────────────────────────────────────────────────

def _scrape_with_instagrapi(
    hashtags: List[str],
    months_back: int,
    max_per_tag: int = 50
) -> List[Dict[str, Any]]:
    """
    Use instagrapi to scrape public hashtag posts.
    instagrapi works with anonymous/unauthenticated requests for
    hashtag searches in most cases.

    Returns list of post dicts.
    """
    try:
        from instagrapi import Client
    except ImportError:
        logger.warning("instagrapi not installed — skipping")
        return []

    posts: List[Dict[str, Any]] = []
    cutoff = datetime.utcnow() - timedelta(days=months_back * 30)
    seen_ids: set = set()

    try:
        cl = Client()
        # Anonymous session — no login needed for public hashtag reads
        # (rate-limited, but fine for hackathon / local use)
        cl.delay_range = [1, 3]

        for tag in hashtags:
            try:
                logger.info(f"Searching Instagram hashtag: #{tag}")
                medias = cl.hashtag_medias_recent_v1(tag, amount=max_per_tag)

                for media in medias:
                    media_id = str(media.pk)
                    if media_id in seen_ids:
                        continue
                    seen_ids.add(media_id)

                    # Date filter
                    post_dt = media.taken_at
                    if post_dt and hasattr(post_dt, "replace"):
                        post_dt = post_dt.replace(tzinfo=None)
                    date_available = post_dt is not None

                    # If we have a date and it's too old, skip
                    if date_available and post_dt < cutoff:
                        continue

                    caption = media.caption_text or ""
                    # Extract hashtags from caption
                    found_tags = re.findall(r"#(\w+)", caption)

                    posts.append({
                        "post_id":      media_id,
                        "caption":      caption,
                        "hashtags":     found_tags,
                        "post_url":     f"https://www.instagram.com/p/{media.code}/",
                        "image_url":    str(media.thumbnail_url or ""),
                        "like_count":   media.like_count or 0,
                        "comment_count": media.comment_count or 0,
                        "posted_at":    post_dt,
                        "date_available": date_available,
                        "source_tag":   tag,
                    })

                time.sleep(2)  # polite rate limiting between tags

            except Exception as e:
                logger.warning(f"instagrapi error for #{tag}: {e}")
                continue

    except Exception as e:
        logger.warning(f"instagrapi client init/session error: {e}")

    logger.info(f"instagrapi: collected {len(posts)} posts across {len(hashtags)} hashtags")
    return posts


# ─────────────────────────────────────────────────────────────────────
# FALLBACK: requests on public hashtag page
# Less reliable — Instagram heavily JS-renders, but sometimes
# the initial HTML contains embedded JSON (similar to Zomato's __NEXT_DATA__)
# ─────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _scrape_with_requests(
    hashtags: List[str],
    months_back: int
) -> List[Dict[str, Any]]:
    """
    Fallback: fetch public Instagram hashtag page and extract
    shared_data JSON embedded in the HTML.
    Only gives top ~12 posts per tag (no pagination possible without auth).
    """
    import requests as req
    import json

    posts: List[Dict[str, Any]] = []
    seen_ids: set = set()
    cutoff = datetime.utcnow() - timedelta(days=months_back * 30)

    for tag in hashtags:
        try:
            url = f"https://www.instagram.com/explore/tags/{tag}/"
            time.sleep(2)
            resp = req.get(url, headers=HEADERS, timeout=12)

            if resp.status_code != 200:
                logger.warning(f"Instagram HTML page {resp.status_code} for #{tag}")
                continue

            # Look for window._sharedData or __additionalDataLoaded
            patterns = [
                r'window\._sharedData\s*=\s*({.*?});</script>',
                r'window\.__additionalDataLoaded\(.*?,\s*({.*?})\);</script>',
            ]

            raw_json = None
            for pattern in patterns:
                m = re.search(pattern, resp.text, re.DOTALL)
                if m:
                    try:
                        raw_json = json.loads(m.group(1))
                        break
                    except Exception:
                        continue

            if not raw_json:
                logger.warning(f"No embedded JSON found for #{tag}")
                continue

            # Navigate to media nodes
            try:
                hashtag_data = (
                    raw_json.get("entry_data", {}).get("TagPage", [{}])[0]
                    .get("graphql", {}).get("hashtag", {})
                )
                edges = (
                    hashtag_data.get("edge_hashtag_to_media", {}).get("edges", []) or
                    hashtag_data.get("edge_hashtag_to_top_posts", {}).get("edges", [])
                )

                for edge in edges:
                    node = edge.get("node", {})
                    media_id = str(node.get("id", ""))
                    if media_id in seen_ids:
                        continue
                    seen_ids.add(media_id)

                    caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                    caption = caption_edges[0].get("node", {}).get("text", "") if caption_edges else ""

                    taken_at = node.get("taken_at_timestamp")
                    post_dt = datetime.utcfromtimestamp(taken_at) if taken_at else None
                    date_available = post_dt is not None

                    if date_available and post_dt < cutoff:
                        continue

                    shortcode = node.get("shortcode", "")
                    found_tags = re.findall(r"#(\w+)", caption)

                    posts.append({
                        "post_id":      media_id,
                        "caption":      caption,
                        "hashtags":     found_tags,
                        "post_url":     f"https://www.instagram.com/p/{shortcode}/",
                        "image_url":    node.get("display_url") or node.get("thumbnail_src") or "",
                        "like_count":   node.get("edge_liked_by", {}).get("count", 0),
                        "comment_count": node.get("edge_media_to_comment", {}).get("count", 0),
                        "posted_at":    post_dt,
                        "date_available": date_available,
                        "source_tag":   tag,
                    })

            except Exception as e:
                logger.warning(f"JSON traversal error for #{tag}: {e}")
                continue

        except Exception as e:
            logger.warning(f"requests fallback error for #{tag}: {e}")
            continue

    logger.info(f"requests fallback: collected {len(posts)} posts")
    return posts


# ─────────────────────────────────────────────────────────────────────
# VIRALITY INDEX
# ─────────────────────────────────────────────────────────────────────

def compute_virality_index(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute a simple virality/interest index from the scraped posts.
    Used as a signal in PESTEL (Social) and 4 P's (Promotion).

    Returns:
        {
            "total_posts":      int,
            "total_likes":      int,
            "total_comments":   int,
            "avg_engagement":   float,
            "virality_score":   float,   # 0-100 normalised
            "level":            str      # "High" | "Medium" | "Low"
        }
    """
    if not posts:
        return {
            "total_posts": 0, "total_likes": 0, "total_comments": 0,
            "avg_engagement": 0.0, "virality_score": 0.0, "level": "Low"
        }

    total_posts    = len(posts)
    total_likes    = sum(p.get("like_count", 0) for p in posts)
    total_comments = sum(p.get("comment_count", 0) for p in posts)
    avg_engagement = (total_likes + total_comments) / total_posts if total_posts else 0

    # Simple normalised score — tune thresholds as needed
    # >500 avg engagement = 100, linear below
    virality_score = min(100.0, (avg_engagement / 500) * 100)

    level = "High" if virality_score >= 60 else "Medium" if virality_score >= 25 else "Low"

    return {
        "total_posts":    total_posts,
        "total_likes":    total_likes,
        "total_comments": total_comments,
        "avg_engagement": round(avg_engagement, 1),
        "virality_score": round(virality_score, 1),
        "level":          level,
    }


# ─────────────────────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────────────

def scrape_instagram(
    restaurant_name: str,
    area: str,
    city: str,
    months_back: int = 6,
    max_per_tag: int = 50,
) -> Dict[str, Any]:
    """
    Scrape Instagram mentions for a restaurant using hashtag search.

    Args:
        restaurant_name: e.g. "Leopold Cafe"
        area:            e.g. "Colaba"
        city:            e.g. "Mumbai"
        months_back:     How many months of posts to include
        max_per_tag:     Max posts per hashtag (instagrapi)

    Returns:
        {
            "posts":           [...],
            "hashtags_searched": [...],
            "virality_index":  {...},
            "total_posts":     int,
            "scrape_method":   str
        }
    """
    hashtags = generate_hashtags(restaurant_name, area, city)

    # ── Primary: instagrapi ────────────────────────────────────────
    posts = _scrape_with_instagrapi(hashtags, months_back, max_per_tag)
    method = "instagrapi"

    # ── Fallback: requests ─────────────────────────────────────────
    if not posts:
        logger.info("instagrapi returned nothing — trying requests fallback")
        posts = _scrape_with_requests(hashtags, months_back)
        method = "requests_html"

    if not posts:
        logger.warning("All Instagram scrape methods returned 0 posts")
        method = "none"

    virality = compute_virality_index(posts)

    logger.info(
        f"Instagram scrape complete: {len(posts)} posts — method: {method}"
    )

    return {
        "posts":             posts,
        "hashtags_searched": hashtags,
        "virality_index":    virality,
        "total_posts":       len(posts),
        "scrape_method":     method,
    }