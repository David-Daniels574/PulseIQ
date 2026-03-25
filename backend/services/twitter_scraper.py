import requests
import json
import re
import numpy as np
from sentence_transformers import CrossEncoder
import os # <-- ADD THIS
from dotenv import load_dotenv # <-- ADD THIS

# Load environment variables right at the start
load_dotenv() # <-- ADD THIS

# ── NLI model — loaded ONCE at module startup ──────────────────────────────
print("Loading NLI classifier...")
# Fix 1: Corrected model name
_NLI = CrossEncoder("cross-encoder/nli-MiniLM2-L6-H768")
_HYPOTHESIS = "I am sharing my opinion about the food and my experience eating at this restaurant."
_EXCLUDE = re.compile(
    r'^RT\s|hiring|job\s+open|giveaway|contest|follow\s+(us|@)|opening\s+soon',
    re.I
)
print("Classifier ready.\n")


# ── Twitter fetch ──────────────────────────────────────────────────────────
def fetch_twitter_mentions(search_query: str) -> list[str]:
    print(f"Fetching tweets for: '{search_query}'...\n")
    rapidapi_key = os.getenv("RAPIDAPI_TWITTER_KEY")

    url = "https://twitter241.p.rapidapi.com/search-v2"
    querystring = {"type": "Top", "query": search_query, "count": "20"}
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "twitter241.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        if "result" not in data:
            print("API connected but returned an error:")
            print(json.dumps(data, indent=2))
            return []

        instructions = data.get("result", {}).get("timeline", {}).get("instructions", [])
        entries = []
        for inst in instructions:
            if inst.get("__typename") == "TimelineAddEntries" or "entries" in inst:
                entries = inst.get("entries", [])
                break

        extracted = []
        for entry in entries:
            try:
                item_content = entry.get("content", {}).get("itemContent", {})
                if item_content.get("__typename") != "TimelineTweet":
                    continue

                tweet_result = item_content.get("tweet_results", {}).get("result", {})
                text = tweet_result.get("legacy", {}).get("full_text")
                if not text:
                    text = (tweet_result
                            .get("note_tweet", {})
                            .get("note_tweet_results", {})
                            .get("result", {})
                            .get("text"))
                if text:
                    extracted.append(text.replace('\n', ' ').strip())
            except Exception:
                continue

        return extracted

    except Exception as e:
        print(f"Error connecting to API: {e}")
        return []


# ── NLI review filter ──────────────────────────────────────────────────────
def filter_reviews_nli(
    tweets: list[str],
    threshold: float = 0.55
) -> list[dict]:
    """
    Runs all tweets through the NLI model in a single batch call.
    Returns list of dicts with text + confidence score.
    """
    if not tweets:
        return []

    # Cheap pre-filter: drop obvious non-reviews before hitting the model
    candidates = [t for t in tweets if not _EXCLUDE.search(t) and len(t.split()) >= 5]

    if not candidates:
        return []

    # Single batched inference call
    pairs = [(tweet, _HYPOTHESIS) for tweet in candidates]
    
    # Fix 2: Handle the multi-class output of NLI models
    logits = _NLI.predict(pairs)
    
    # Calculate Softmax to turn raw logits into 0-1 probabilities 
    # (Subtracting max logits for numerical stability)
    exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
    
    # NLI output mapping is [contradiction, entailment, neutral]
    # We only care about the confidence of 'entailment' (index 1)
    entailment_scores = probs[:, 1]

    results = []
    for tweet, score in zip(candidates, entailment_scores):
        if score > threshold:
            results.append({
                "text": tweet,
                "confidence": round(float(score), 3)
            })

    # Sort highest confidence first
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results


# ── Main pipeline ──────────────────────────────────────────────────────────
def get_restaurant_reviews(search_query: str) -> list[dict]:
    """Fetch tweets and return only genuine reviews."""

    # Step 1: fetch
    raw_tweets = fetch_twitter_mentions(search_query)
    if not raw_tweets:
        print("No tweets fetched.")
        return []
    print(f"Fetched {len(raw_tweets)} tweets. Running NLI filter...\n")

    # Step 2: filter
    reviews = filter_reviews_nli(raw_tweets)
    return reviews


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    reviews = get_restaurant_reviews("Pizza By The Bay Mumbai")

    print(f"{'─' * 60}")
    print(f"  Found {len(reviews)} genuine reviews")
    print(f"{'─' * 60}\n")

    for i, review in enumerate(reviews, 1):
        print(f"{i}. [{review['confidence']:.0%}] {review['text']}\n")