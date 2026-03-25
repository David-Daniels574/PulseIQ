"""
Zomato Scraper Service
Strategy:
  1. Try Zomato's internal search API (reverse-engineered, no auth needed for basic search)
  2. For the restaurant page: requests + BeautifulSoup on the user-provided URL
  3. If JS-rendered content is missing: Selenium headless fallback
  
Scrapes: reviews, rating, cuisine tags, price range, menu items, photo count
"""

import requests
import time
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser
from urllib.parse import quote_plus, urljoin

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.zomato.com/",
}

API_HEADERS = {
    **HEADERS,
    "Accept": "application/json, text/plain, */*",
    "x-zomato-csrft": "",          # Zomato expects this header; empty is often fine for reads
}

BASE_URL = "https://www.zomato.com"


# ─────────────────────────────────────────────────────────────────────
# 1. RESOLVE COMPETITOR ZOMATO URL
#    Given a competitor name + area (from Google Maps nearby),
#    find their Zomato URL via Zomato's search endpoint.
# ─────────────────────────────────────────────────────────────────────

def find_zomato_url(restaurant_name: str, area: str, city: str) -> Optional[str]:
    """
    Search Zomato for a restaurant and return its URL.
    Uses Zomato's internal search API first; falls back to HTML search page.

    Args:
        restaurant_name: e.g. "Leopold Cafe"
        area: e.g. "Colaba"
        city: e.g. "Mumbai"

    Returns:
        Full Zomato URL or None if not found
    """
    # ── Attempt 1: Zomato internal search API ──────────────────────
    try:
        query = f"{restaurant_name} {area}"
        search_url = (
            f"{BASE_URL}/webroutes/search/autoSuggest"
            f"?addressId=0&entityType=&isOrderLocation=0"
            f"&latitude=0&longitude=0&query={quote_plus(query)}"
        )
        resp = requests.get(search_url, headers=API_HEADERS, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            # Response structure: {"restaurants": [...], "pages": {"restaurant": [...]}}
            restaurants = (
                data.get("restaurants", []) or
                data.get("pages", {}).get("restaurant", [])
            )

            for item in restaurants:
                # Normalise across possible response shapes
                r = item.get("restaurant") or item
                r_name    = (r.get("name") or r.get("title") or "").lower()
                r_area    = (r.get("area") or r.get("subzone") or "").lower()
                r_url     = r.get("url") or r.get("restaurant_url") or ""

                name_match = restaurant_name.lower() in r_name or r_name in restaurant_name.lower()
                area_match = area.lower() in r_area or r_area in area.lower()

                if name_match and (area_match or not area):
                    full_url = r_url if r_url.startswith("http") else BASE_URL + r_url
                    logger.info(f"Zomato URL found via API: {full_url}")
                    return full_url

    except Exception as e:
        logger.warning(f"Zomato API search failed: {e}")

    # ── Attempt 2: HTML search page ───────────────────────────────
    try:
        time.sleep(1)
        query = f"{restaurant_name} {area} {city}"
        search_page = f"{BASE_URL}/search?q={quote_plus(query)}"
        resp = requests.get(search_page, headers=HEADERS, timeout=12)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Search result cards usually have an <a> with the restaurant path
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # Zomato restaurant URLs look like: /mumbai/restaurant-name-area
                city_slug = city.lower().replace(" ", "-")
                if f"/{city_slug}/" in href and href.count("/") >= 3:
                    # Basic name similarity check
                    slug = href.split("/")[2].replace("-", " ")
                    if any(word in slug for word in restaurant_name.lower().split()):
                        full_url = BASE_URL + href if href.startswith("/") else href
                        logger.info(f"Zomato URL found via HTML search: {full_url}")
                        return full_url

    except Exception as e:
        logger.warning(f"Zomato HTML search failed: {e}")

    logger.warning(f"Could not find Zomato URL for: {restaurant_name}, {area}")
    return None


# ─────────────────────────────────────────────────────────────────────
# 2. RESOLVE RELATIVE DATES
# ─────────────────────────────────────────────────────────────────────

def resolve_relative_date(raw: str, now: Optional[datetime] = None) -> tuple[Optional[datetime], bool]:
    """
    Convert Zomato's relative date strings to absolute datetimes.

    Returns:
        (datetime | None, is_estimated: bool)
        is_estimated=True means we guessed from a relative string.
    """
    if not raw:
        return None, False

    now = now or datetime.utcnow()
    raw_lower = raw.strip().lower()

    # ── Exact / near-exact formats ─────────────────────────────────
    try:
        dt = dateutil_parser.parse(raw, dayfirst=False)
        return dt, False
    except Exception:
        pass

    # ── Relative patterns ──────────────────────────────────────────
    patterns = [
        (r"(\d+)\s*day",   lambda n: now - timedelta(days=int(n))),
        (r"(\d+)\s*week",  lambda n: now - timedelta(weeks=int(n))),
        (r"(\d+)\s*month", lambda n: now - timedelta(days=int(n) * 30)),
        (r"(\d+)\s*year",  lambda n: now - timedelta(days=int(n) * 365)),
        (r"yesterday",     lambda _: now - timedelta(days=1)),
        (r"last week",     lambda _: now - timedelta(weeks=1)),
        (r"last month",    lambda _: now - timedelta(days=30)),
        (r"just now|today|recently", lambda _: now),
    ]

    for pattern, fn in patterns:
        m = re.search(pattern, raw_lower)
        if m:
            try:
                n = m.group(1) if m.lastindex else None
                return fn(n), True
            except Exception:
                pass

    # ── Fallback: assume 3 months ago (plausible/recent) ──────────
    logger.debug(f"Could not parse date '{raw}', assuming 3 months ago")
    return now - timedelta(days=90), True


# ─────────────────────────────────────────────────────────────────────
# 3. REQUESTS-BASED PAGE SCRAPER (primary)
# ─────────────────────────────────────────────────────────────────────

def _scrape_with_requests(zomato_url: str) -> Optional[BeautifulSoup]:
    """Fetch Zomato page HTML using requests. Returns soup or None."""
    try:
        resp = requests.get(zomato_url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
        logger.warning(f"Requests returned {resp.status_code} for {zomato_url}")
    except Exception as e:
        logger.warning(f"Requests fetch failed: {e}")
    return None


def _extract_next_data(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Zomato injects __NEXT_DATA__ JSON into the page.
    This is the richest source — parse it first.
    """
    tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if tag and tag.string:
        try:
            return json.loads(tag.string)
        except Exception as e:
            logger.warning(f"__NEXT_DATA__ parse failed: {e}")
    return None


# ─────────────────────────────────────────────────────────────────────
# 4. SELENIUM FALLBACK
# ─────────────────────────────────────────────────────────────────────

def _scrape_with_selenium(zomato_url: str) -> Optional[BeautifulSoup]:
    """
    Headless Selenium scraper — only used when requests returns
    incomplete/empty JS-rendered content.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-agent={HEADERS['User-Agent']}")

        driver = webdriver.Chrome(options=options)
        driver.get(zomato_url)

        # Wait until the restaurant name heading loads (signals JS is done)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except Exception:
            pass  # Continue anyway with whatever rendered

        # Extra wait for dynamic review content
        time.sleep(3)

        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, "html.parser")

    except Exception as e:
        logger.error(f"Selenium scrape failed: {e}")
        return None


def _get_soup(zomato_url: str) -> Optional[BeautifulSoup]:
    """Try requests first; fall back to Selenium."""
    soup = _scrape_with_requests(zomato_url)

    # Quality check: if __NEXT_DATA__ or meaningful content missing, use Selenium
    if soup:
        next_data = _extract_next_data(soup)
        has_reviews = soup.find_all(string=re.compile(r"rated", re.I))
        if next_data or has_reviews:
            return soup
        logger.info("requests soup looks empty/JS-only — switching to Selenium")

    return _scrape_with_selenium(zomato_url)


# ─────────────────────────────────────────────────────────────────────
# 5. EXTRACT RESTAURANT INFO
# ─────────────────────────────────────────────────────────────────────

def _extract_restaurant_info(soup: BeautifulSoup, next_data: Optional[Dict]) -> Dict[str, Any]:
    """
    Extract: name, rating, review count, cuisine tags, price range, photo count.
    Tries __NEXT_DATA__ JSON first (most reliable), then HTML fallback.
    """
    info: Dict[str, Any] = {
        "name": None,
        "rating": None,
        "review_count": 0,
        "cuisine_tags": [],
        "price_range": None,
        "photo_count": 0,
    }

    # ── From __NEXT_DATA__ ─────────────────────────────────────────
    if next_data:
        try:
            # Path varies; walk common locations
            props = next_data.get("props", {})
            page_props = props.get("pageProps", {})

            # Try common Zomato Next.js structures
            res_data = (
                page_props.get("res_id") or
                page_props.get("restaurant") or
                page_props.get("restData") or
                {}
            )

            # Sometimes nested under "sections"
            sections = page_props.get("sections", {})
            basic = sections.get("SECTION_BASIC_INFO", {})
            overview = sections.get("SECTION_RES_CONTACT", {})

            info["name"]        = basic.get("name") or res_data.get("name")
            info["rating"]      = float(basic.get("rating", {}).get("aggregate_rating") or
                                        res_data.get("user_rating", {}).get("aggregate_rating") or 0)
            info["review_count"] = int(basic.get("rating", {}).get("votes") or
                                       res_data.get("user_rating", {}).get("votes") or 0)
            info["photo_count"]  = int(sections.get("SECTION_IMAGES", {}).get("count") or
                                       page_props.get("photoCount") or 0)
            info["price_range"]  = (
                basic.get("cft", {}).get("text") or
                res_data.get("average_cost_for_two") or None
            )

            # Cuisine tags
            cuisines = basic.get("cuisine_string") or res_data.get("cuisines") or ""
            if isinstance(cuisines, str):
                info["cuisine_tags"] = [c.strip() for c in cuisines.split(",") if c.strip()]
            elif isinstance(cuisines, list):
                info["cuisine_tags"] = cuisines

        except Exception as e:
            logger.warning(f"__NEXT_DATA__ restaurant info extraction failed: {e}")

    # ── HTML fallback ──────────────────────────────────────────────
    if not info["name"] and soup:
        try:
            # 1. Name
            h1 = soup.find("h1")
            if h1:
                info["name"] = h1.get_text(strip=True)

            # 2. Rating — ignore numbers hidden in scripts/json
            rating_candidates = soup.find_all(string=re.compile(r"^[1-4]\.\d$"))
            for rc in rating_candidates:
                if rc.parent and rc.parent.name not in ["script", "style", "meta"]:
                    try:
                        info["rating"] = float(rc.strip())
                        break  # Found the first visible rating, stop looking
                    except ValueError:
                        continue

            # 3. Price range — strictly ignore JSON-LD and enforce 50-char limit
            price_tags = soup.find_all(string=re.compile(r"₹\d+"))
            for pt in price_tags:
                if pt.parent and pt.parent.name not in ["script", "style", "meta"]:
                    clean_price = str(pt).strip()
                    # Truncate to 50 chars max to prevent StringDataRightTruncation DB errors
                    info["price_range"] = clean_price[:50] 
                    break  # Found the first visible price, stop looking

            # 4. Cuisine tags from meta keywords
            meta_keywords = soup.find("meta", {"name": "keywords"})
            if meta_keywords:
                content = meta_keywords.get("content", "")
                info["cuisine_tags"] = [
                    k.strip() for k in content.split(",")
                    if k.strip() and "restaurant" not in k.lower()
                ][:8]

        except Exception as e:
            logger.warning(f"HTML restaurant info extraction failed: {e}")

    return info


# ─────────────────────────────────────────────────────────────────────
# 6. EXTRACT REVIEWS
# ─────────────────────────────────────────────────────────────────────

def _extract_reviews_from_next_data(next_data: Dict) -> List[Dict[str, Any]]:
    """Pull reviews from __NEXT_DATA__."""
    reviews = []
    try:
        sections = next_data.get("props", {}).get("pageProps", {}).get("sections", {})
        review_section = sections.get("SECTION_REVIEWS", {})
        review_list = review_section.get("reviewsList") or []

        for item in review_list:
            r = item.get("reviewData") or item
            raw_date = (
                r.get("reviewTimeStamp") or
                r.get("timestamp") or
                r.get("friendlyTime") or ""
            )
            dt, estimated = resolve_relative_date(str(raw_date))
            reviews.append({
                "review_text": r.get("reviewText") or r.get("body") or "",
                "author_name": r.get("reviewer", {}).get("name") or r.get("userName") or "Anonymous",
                "rating":      float(r.get("rating") or r.get("ratingV2") or 0),
                "raw_date":    str(raw_date),
                "review_date": dt,
                "date_is_estimated": estimated,
                "dining_type": "combined",
            })
    except Exception as e:
        logger.warning(f"__NEXT_DATA__ review extraction failed: {e}")
    return reviews


def _extract_reviews_html(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """HTML fallback review extraction."""
    reviews = []
    try:
        # Zomato review cards: look for blocks containing a rating number + review text
        # Structure changes often; we target common patterns
        review_blocks = (
            soup.find_all("div", {"class": re.compile(r"review", re.I)}) or
            soup.find_all("section", {"class": re.compile(r"review", re.I)})
        )

        for block in review_blocks:
            text_el = block.find(
                ["p", "div", "span"],
                {"class": re.compile(r"(reviewText|review-text|comment|desc)", re.I)}
            )
            if not text_el:
                text_el = block.find("p")
            if not text_el:
                continue

            review_text = text_el.get_text(separator=" ", strip=True)
            if len(review_text) < 10:
                continue

            # Rating
            rating_el = block.find(string=re.compile(r"^[1-5](\.\d)?$"))
            rating = float(rating_el) if rating_el else None

            # Date
            date_el = block.find(["time", "span"], {"class": re.compile(r"time|date", re.I)})
            raw_date = date_el.get_text(strip=True) if date_el else ""
            dt, estimated = resolve_relative_date(raw_date)

            # Author
            author_el = block.find(["a", "span"], {"class": re.compile(r"name|user|author", re.I)})
            author = author_el.get_text(strip=True) if author_el else "Anonymous"

            reviews.append({
                "review_text": review_text,
                "author_name": author,
                "rating":      rating,
                "raw_date":    raw_date,
                "review_date": dt,
                "date_is_estimated": estimated,
                "dining_type": "combined",
            })

    except Exception as e:
        logger.warning(f"HTML review extraction failed: {e}")

    return reviews


# ─────────────────────────────────────────────────────────────────────
# 7. EXTRACT MENU ITEMS
# ─────────────────────────────────────────────────────────────────────

def _extract_menu_items(soup: BeautifulSoup, next_data: Optional[Dict]) -> List[Dict[str, Any]]:
    """Extract menu items for BCG Matrix analysis."""
    items = []

    # ── From __NEXT_DATA__ ─────────────────────────────────────────
    if next_data:
        try:
            sections = next_data.get("props", {}).get("pageProps", {}).get("sections", {})
            menu_section = (
                sections.get("SECTION_MENU") or
                sections.get("SECTION_DELIVERY_MENU") or
                {}
            )
            menus = menu_section.get("menus") or []

            for menu in menus:
                for category in menu.get("menu", {}).get("categories") or []:
                    cat_name = category.get("category", {}).get("name", "")
                    for item_wrap in category.get("category", {}).get("items") or []:
                        item = item_wrap.get("item") or item_wrap
                        items.append({
                            "name":        item.get("name") or "",
                            "price":       float(item.get("price") or 0),
                            "category":    cat_name,
                            "description": item.get("desc") or "",
                            "is_veg":      item.get("is_veg") == "1",
                        })
        except Exception as e:
            logger.warning(f"__NEXT_DATA__ menu extraction failed: {e}")

    # ── HTML fallback ──────────────────────────────────────────────
    if not items and soup:
        try:
            item_els = soup.find_all(
                "div",
                {"class": re.compile(r"(menuItem|menu-item|sc-.*item)", re.I)}
            )
            for el in item_els:
                name_el  = el.find(["h4", "h3", "span", "p"],
                                   {"class": re.compile(r"name|title", re.I)})
                price_el = el.find(string=re.compile(r"₹\s*\d+"))
                if name_el:
                    price_str = price_el or "0"
                    price_num = float(re.sub(r"[^\d.]", "", str(price_str)) or 0)
                    items.append({
                        "name":        name_el.get_text(strip=True),
                        "price":       price_num,
                        "category":    "",
                        "description": "",
                        "is_veg":      None,
                    })
        except Exception as e:
            logger.warning(f"HTML menu extraction failed: {e}")

    logger.info(f"Extracted {len(items)} menu items")
    return items


# ─────────────────────────────────────────────────────────────────────
# 8. FETCH PAGINATED REVIEWS VIA ZOMATO API
#    Zomato has an internal reviews API used by their own frontend.
#    We use it to get more than the first page of reviews.
# ─────────────────────────────────────────────────────────────────────

def _fetch_reviews_via_api(res_id: str, months_back: int = 6) -> List[Dict[str, Any]]:
    """
    Try Zomato's internal reviews endpoint to get paginated reviews.
    
    Args:
        res_id: Zomato restaurant ID (extracted from URL or __NEXT_DATA__)
        months_back: How far back to collect reviews
    """
    reviews = []
    cutoff = datetime.utcnow() - timedelta(days=months_back * 30)
    page = 0
    max_pages = 20  # safety limit

    while page < max_pages:
        try:
            api_url = (
                f"{BASE_URL}/webroutes/reviews/loadMore"
                f"?res_id={res_id}&offset={page * 10}&filter_by_time=&sort_by=dd"
            )
            resp = requests.get(api_url, headers=API_HEADERS, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"Reviews API returned {resp.status_code} at page {page}")
                break

            data = resp.json()
            review_list = (
                data.get("entities", {}).get("REVIEWS", {}).values() or
                data.get("reviews") or
                []
            )
            review_list = list(review_list)

            if not review_list:
                break

            stop_pagination = False
            for r in review_list:
                raw_date = r.get("reviewTimeStamp") or r.get("timestamp") or ""
                dt, estimated = resolve_relative_date(str(raw_date))

                # Stop if we've gone beyond the requested time window
                if dt and not estimated and dt < cutoff:
                    stop_pagination = True
                    break

                reviews.append({
                    "review_text": r.get("reviewText") or r.get("body") or "",
                    "author_name": (r.get("reviewer") or {}).get("name") or "Anonymous",
                    "rating":      float(r.get("ratingV2") or r.get("rating") or 0),
                    "raw_date":    str(raw_date),
                    "review_date": dt,
                    "date_is_estimated": estimated,
                    "dining_type": "combined",
                })

            if stop_pagination:
                break

            page += 1
            time.sleep(0.5)  # be polite

        except Exception as e:
            logger.warning(f"Reviews API failed at page {page}: {e}")
            break

    logger.info(f"Fetched {len(reviews)} reviews via Zomato API (pages: {page})")
    return reviews


def _extract_res_id(next_data: Optional[Dict], zomato_url: str) -> Optional[str]:
    """Extract Zomato restaurant ID from __NEXT_DATA__ or URL."""
    if next_data:
        try:
            props = next_data.get("props", {}).get("pageProps", {})
            res_id = (
                props.get("res_id") or
                props.get("resId") or
                props.get("restaurant", {}).get("id")
            )
            if res_id:
                return str(res_id)
        except Exception:
            pass

    # Fallback: some Zomato URLs contain the ID as a number at the end
    # e.g. /mumbai/leopold-cafe-colaba/order -> won't have ID
    # But older format: /mumbai/leopold-cafe-18932 might
    m = re.search(r"-(\d{4,})", zomato_url)
    if m:
        return m.group(1)

    return None


# ─────────────────────────────────────────────────────────────────────
# 9. FILTER BY DATE RANGE
# ─────────────────────────────────────────────────────────────────────

def _filter_by_date(
    reviews: List[Dict[str, Any]],
    months_back: int
) -> List[Dict[str, Any]]:
    """
    Keep reviews within the last `months_back` months.
    Reviews with estimated/unknown dates are kept (treated as recent).
    """
    cutoff = datetime.utcnow() - timedelta(days=months_back * 30)
    filtered = []
    for r in reviews:
        if r.get("date_is_estimated") or r.get("review_date") is None:
            filtered.append(r)   # unknown date → include (plausible/recent)
        elif r["review_date"] >= cutoff:
            filtered.append(r)
    return filtered


# ─────────────────────────────────────────────────────────────────────
# 10. MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────────────

def scrape_zomato(
    zomato_url: str,
    months_back: int = 6
) -> Dict[str, Any]:
    """
    Full Zomato scrape for a restaurant.

    Args:
        zomato_url:  Direct Zomato URL (user-provided for their own restaurant,
                     or auto-resolved for competitors)
        months_back: How many months of reviews to include

    Returns:
        {
            "restaurant_info": {...},
            "reviews": [...],
            "menu_items": [...],
            "total_reviews_scraped": int,
            "scrape_method": "api|requests|selenium"
        }
    """
    logger.info(f"Starting Zomato scrape: {zomato_url}")

    # ── Step 1: Get the page ───────────────────────────────────────
    soup = _get_soup(zomato_url)
    if not soup:
        logger.error("Could not fetch Zomato page at all")
        return {"error": "Could not fetch Zomato page", "reviews": [], "menu_items": []}

    next_data = _extract_next_data(soup)
    scrape_method = "requests" if next_data else "selenium_or_html"

    # ── Step 2: Restaurant info ────────────────────────────────────
    restaurant_info = _extract_restaurant_info(soup, next_data)

    # ── Step 3: Reviews — try paginated API first ──────────────────
    reviews = []
    res_id = _extract_res_id(next_data, zomato_url)

    if res_id:
        logger.info(f"Found res_id={res_id}; using paginated API for reviews")
        reviews = _fetch_reviews_via_api(res_id, months_back=months_back)
        if reviews:
            scrape_method = "api"

    # ── Step 4: If API gave nothing, fall back to page scrape ──────
    if not reviews:
        if next_data:
            reviews = _extract_reviews_from_next_data(next_data)
        if not reviews:
            reviews = _extract_reviews_html(soup)

    # ── Step 5: Date filter ────────────────────────────────────────
    reviews = _filter_by_date(reviews, months_back)

    # ── Step 6: Menu items ─────────────────────────────────────────
    menu_items = _extract_menu_items(soup, next_data)

    logger.info(
        f"Zomato scrape complete: {len(reviews)} reviews, "
        f"{len(menu_items)} menu items — method: {scrape_method}"
    )

    return {
        "restaurant_info": restaurant_info,
        "reviews": reviews,
        "menu_items": menu_items,
        "total_reviews_scraped": len(reviews),
        "scrape_method": scrape_method,
    }