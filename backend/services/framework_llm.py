"""
8-Framework Strategic Analysis via Gemini LLM
Single API call → strict JSON → split into 8 FrameworkReport rows.

Frameworks: SWOT, PESTEL, 4 P's, BCG Matrix, VRIO, Ansoff, MECE, Six Sigma
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# EXPECTED OUTPUT KEYS
# ─────────────────────────────────────────────────────────────────────

EXPECTED_KEYS = {
    "swot", "pestel", "four_ps", "bcg", "vrio", "ansoff", "mece", "six_sigma"
}


# ─────────────────────────────────────────────────────────────────────
# BUILD THE MEGA PROMPT
# Uses str.format() style avoided — built with concatenation so that
# the JSON schema examples (which contain {curly braces}) don't
# conflict with Python f-string interpolation.
# ─────────────────────────────────────────────────────────────────────

def build_frameworks_prompt(
    restaurant_name: str,
    area: str,
    city: str,
    aggregated_absa: List[Dict[str, Any]],
    competitor_summaries: List[Dict[str, Any]],
    menu_items: List[Dict[str, Any]],
    virality_index: Dict[str, Any],
    news_mentions: List[Dict[str, Any]],
    mece_clusters: List[Dict[str, Any]],
    sentiment_variances: Dict[str, float],
    date_range_label: str,
) -> str:
    # ── Serialise all data sections first (no braces risk in these) ──
    absa_json        = json.dumps(aggregated_absa,      indent=2, default=str)
    comp_json        = json.dumps(competitor_summaries, indent=2, default=str)
    menu_json        = json.dumps(menu_items,           indent=2, default=str)
    virality_json    = json.dumps(virality_index,       indent=2, default=str)
    news_json        = json.dumps(
        [{"headline": n.get("headline"), "source": n.get("source_name")}
         for n in news_mentions[:20]],
        indent=2,
    )
    mece_json        = json.dumps(mece_clusters,        indent=2, default=str)
    variance_json    = json.dumps(sentiment_variances,  indent=2, default=str)
    news_count       = str(len(news_mentions))

    # ── Static schema strings (literal braces, NOT interpolated) ────
    # Written as plain strings then joined — zero risk of f-string collision.
    point_schema = (
        '{\n'
        '  "label":       "<short title>",\n'
        '  "description": "<2-3 sentence explanation citing data>",\n'
        '  "confidence":  <0-100 integer based on source confidence scores>,\n'
        '  "sources":     ["google_maps", "twitter", "news"],\n'
        '  "conflict":    <true if sources disagree on this point>\n'
        '}'
    )

    bcg_item_schema = (
        '{"item": "<menu item name>", "reason": "<str>", "confidence": <int>}'
    )

    vrio_schema = (
        '{\n'
        '  "resource":   "<what the restaurant has>",\n'
        '  "valuable":   true/false,\n'
        '  "rare":       true/false,\n'
        '  "inimitable": true/false,\n'
        '  "organised":  true/false,\n'
        '  "advantage":  "Sustained"|"Temporary"|"Competitive Parity"|"Unused",\n'
        '  "description": "<explanation>",\n'
        '  "confidence": <int>,\n'
        '  "sources":    [...]\n'
        '}'
    )

    mece_category_schema = (
        '{\n'
        '  "category":    "<bucket name>",\n'
        '  "description": "<what complaints fall here>",\n'
        '  "count":       <int>,\n'
        '  "examples":    ["<sentence>", ...],\n'
        '  "confidence":  <int>,\n'
        '  "sources":     [...]\n'
        '}'
    )

    six_sigma_defect_schema = (
        '{\n'
        '  "aspect":         "<aspect name>",\n'
        '  "variance":       <float>,\n'
        '  "severity":       "Critical"|"Major"|"Minor",\n'
        '  "description":    "<what inconsistency looks like>",\n'
        '  "root_cause":     "<possible cause>",\n'
        '  "recommendation": "<corrective action>",\n'
        '  "confidence":     <int>,\n'
        '  "sources":        [...]\n'
        '}'
    )

    # ── Assemble the prompt as a plain string ─────────────────────
    prompt = (
        "You are a senior restaurant strategy consultant. Your task is to generate a\n"
        "structured strategic intelligence report for **" + restaurant_name + "** (" + area + ", " + city + ")\n"
        "covering the analysis period: **" + date_range_label + "**.\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AGGREGATED ASPECT SENTIMENT (cross-source, with confidence scores)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + absa_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "COMPETITOR INTELLIGENCE (lighter analysis)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + comp_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "MENU ITEMS (for BCG Matrix)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + menu_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "SOCIAL SIGNAL INDEX\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + virality_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "NEWS MENTIONS (count: " + news_count + ")\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + news_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "PRE-CLUSTERED COMPLAINTS (for MECE)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + mece_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "SENTIMENT VARIANCE PER ASPECT (for Six Sigma)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + variance_json + "\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "INSTRUCTIONS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Generate ALL 8 frameworks. Use ONLY the data provided above.\n"
        "Each \"confidence\" value must reflect the confidence scores in\n"
        "the aggregated ABSA section — do NOT invent confidence numbers.\n"
        "When sources conflict (conflict_flag: true in ABSA), set \"conflict\": true\n"
        "on the relevant framework point.\n\n"

        "For BCG Matrix, classify EVERY menu item. Use mention_count and\n"
        "positive/negative_mentions to decide category:\n"
        "  Star          = high mentions + positive sentiment\n"
        "  Cash Cow      = high mentions + neutral/mixed\n"
        "  Question Mark = low mentions + positive potential\n"
        "  Dog           = low mentions + negative sentiment\n\n"

        "For VRIO, infer Rarity and Imitability from competitor aspect scores —\n"
        "if competitors score lower on an aspect, the restaurant has an advantage.\n\n"

        "For MECE, use the pre-clustered complaints above. Ensure the final\n"
        "complaint categories are Mutually Exclusive (no overlap) and\n"
        "Collectively Exhaustive (cover all complaint themes).\n\n"

        "For Six Sigma, flag aspects with variance > 0.05 as \"Defects\"\n"
        "(inconsistent experience). Higher variance = more critical defect.\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "REQUIRED OUTPUT FORMAT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Respond with ONLY valid JSON. No markdown. No explanation. No preamble.\n"
        "The JSON must exactly follow this structure:\n\n"
        "{\n"
        "  \"swot\": {\n"
        "    \"strengths\":     [ " + point_schema + " ],\n"
        "    \"weaknesses\":    [ " + point_schema + " ],\n"
        "    \"opportunities\": [ " + point_schema + " ],\n"
        "    \"threats\":       [ " + point_schema + " ]\n"
        "  },\n"
        "  \"pestel\": {\n"
        "    \"political\":     [ " + point_schema + " ],\n"
        "    \"economic\":      [ " + point_schema + " ],\n"
        "    \"social\":        [ " + point_schema + " ],\n"
        "    \"technological\": [ " + point_schema + " ],\n"
        "    \"environmental\": [ " + point_schema + " ],\n"
        "    \"legal\":         [ " + point_schema + " ]\n"
        "  },\n"
        "  \"four_ps\": {\n"
        "    \"product\":   [ " + point_schema + " ],\n"
        "    \"price\":     [ " + point_schema + " ],\n"
        "    \"place\":     [ " + point_schema + " ],\n"
        "    \"promotion\": [ " + point_schema + " ]\n"
        "  },\n"
        "  \"bcg\": {\n"
        "    \"stars\":          [ " + bcg_item_schema + " ],\n"
        "    \"cash_cows\":      [ " + bcg_item_schema + " ],\n"
        "    \"question_marks\": [ " + bcg_item_schema + " ],\n"
        "    \"dogs\":           [ " + bcg_item_schema + " ]\n"
        "  },\n"
        "  \"vrio\": {\n"
        "    \"resources\": [ " + vrio_schema + " ]\n"
        "  },\n"
        "  \"ansoff\": {\n"
        "    \"market_penetration\":  [ " + point_schema + " ],\n"
        "    \"product_development\": [ " + point_schema + " ],\n"
        "    \"market_development\":  [ " + point_schema + " ],\n"
        "    \"diversification\":     [ " + point_schema + " ]\n"
        "  },\n"
        "  \"mece\": {\n"
        "    \"complaint_categories\": [ " + mece_category_schema + " ],\n"
        "    \"is_exhaustive_note\": \"<brief note on coverage>\"\n"
        "  },\n"
        "  \"six_sigma\": {\n"
        "    \"defects\": [ " + six_sigma_defect_schema + " ],\n"
        "    \"dpmo_estimate\": <int>,\n"
        "    \"sigma_level\":   \"<e.g. 3.2sigma>\"\n"
        "  }\n"
        "}\n"
    )

    return prompt


# ─────────────────────────────────────────────────────────────────────
# PARSE AND VALIDATE GEMINI OUTPUT
# ─────────────────────────────────────────────────────────────────────

def _clean_json_response(text: str) -> str:
    """Strip markdown fences and leading/trailing whitespace."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        text  = "\n".join(lines)
    return text.strip()


def _compute_avg_confidence(framework_data: Any) -> float:
    """Walk the framework dict/list and average all confidence fields."""
    scores: List[float] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "confidence" in obj:
                try:
                    scores.append(float(obj["confidence"]))
                except Exception:
                    pass
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(framework_data)
    return round(sum(scores) / len(scores), 1) if scores else 0.0


def parse_framework_response(raw_text: str) -> Dict[str, Any]:
    """
    Parse Gemini's JSON response and validate all 8 framework keys exist.
    Returns parsed dict or raises ValueError with details.
    """
    cleaned = _clean_json_response(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}\nRaw (first 500 chars):\n{cleaned[:500]}")
        raise ValueError(f"Gemini returned invalid JSON: {e}")

    missing = EXPECTED_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"Gemini response missing frameworks: {missing}")

    return data


# ─────────────────────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────────────

def generate_all_frameworks(
    restaurant_name: str,
    area: str,
    city: str,
    aggregated_absa: List[Dict[str, Any]],
    competitor_summaries: List[Dict[str, Any]],
    menu_items: List[Dict[str, Any]],
    virality_index: Dict[str, Any],
    news_mentions: List[Dict[str, Any]],
    mece_clusters: List[Dict[str, Any]],
    sentiment_variances: Dict[str, float],
    months_back: int = 6,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """
    Generate all 8 strategic frameworks in a single Gemini call.

    Returns:
        {
            "frameworks": { "swot": {...}, "pestel": {...}, ... },
            "avg_confidence_per_framework": { "swot": 74.2, ... },
            "sources_used": [...],
            "generated_at": "..."
        }
    """
    date_range_label = (
        f"last {months_back} month{'s' if months_back != 1 else ''}"
    )

    prompt = build_frameworks_prompt(
        restaurant_name=restaurant_name,
        area=area,
        city=city,
        aggregated_absa=aggregated_absa,
        competitor_summaries=competitor_summaries,
        menu_items=menu_items,
        virality_index=virality_index,
        news_mentions=news_mentions,
        mece_clusters=mece_clusters,
        sentiment_variances=sentiment_variances,
        date_range_label=date_range_label,
    )

    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        generation_config={
            "temperature":        0.3,
            "top_p":              0.8,
            "response_mime_type": "application/json",
        },
    )

    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Calling Gemini for 8 frameworks — attempt {attempt}/{max_retries}"
            )
            response = model.generate_content(prompt)
            raw_text = response.text

            frameworks = parse_framework_response(raw_text)

            avg_conf = {
                fw: _compute_avg_confidence(frameworks[fw])
                for fw in EXPECTED_KEYS
                if fw in frameworks
            }

            sources_used = ["google_maps", "twitter"]
            if news_mentions:
                sources_used.append("news")

            logger.info(f"Frameworks generated successfully on attempt {attempt}")
            return {
                "frameworks":                   frameworks,
                "avg_confidence_per_framework": avg_conf,
                "sources_used":                 sources_used,
                "generated_at":                 datetime.utcnow().isoformat(),
            }

        except ValueError as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                logger.info("Retrying with a stricter prompt note...")
                prompt += (
                    "\n\nCRITICAL: Your previous response was not valid JSON. "
                    "Output ONLY the raw JSON object. "
                    "Do NOT include any text, explanation, or markdown fences."
                )
        except Exception as e:
            last_error = e
            logger.error(f"Gemini API error on attempt {attempt}: {e}")

    logger.error(
        f"All {max_retries} Gemini attempts failed. Last error: {last_error}"
    )
    raise RuntimeError(
        f"Failed to generate frameworks after {max_retries} attempts: {last_error}"
    )