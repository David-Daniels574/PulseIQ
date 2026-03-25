"""
Analyzer module for Aspect-Based Sentiment Analysis (ABSA)
Focused strictly on the Food & Beverage Industry (Restaurants, Cafes, Bars)
Uses Hugging Face's cardiffnlp/twitter-roberta-base-sentiment-latest model
"""

import nltk
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# F&B specific aspect keywords
CATEGORY_ASPECT_KEYWORDS = {
    "restaurant": {
        "Food": [
            "food", "meal", "dish", "dishes", "taste", "flavor", "flavour", "cuisine", "menu",
            "breakfast", "lunch", "dinner", "appetizer", "dessert", "entree", "main course",
            "pizza", "burger", "pasta", "salad", "steak", "chicken", "seafood", "sushi",
            "delicious", "tasty", "fresh", "quality", "portion", "serving",
            "yummy", "spicy", "bland", "cooked", "raw", "undercooked"
        ],
        "Service": [
            "service", "staff", "waiter", "waitress", "server", "servers",
            "manager", "employee", "host", "hostess", "friendly", "attentive", 
            "helpful", "rude", "slow", "fast", "quick", "professional", 
            "courteous", "polite", "wait", "waiting", "welcoming", "ignored"
        ],
        "Ambiance": [
            "ambiance", "ambience", "atmosphere", "environment", "decor",
            "interior", "seating", "music", "lighting", "vibe", "vibes", "mood",
            "cozy", "comfortable", "clean", "dirty", "spacious", "crowded", 
            "cramped", "noise", "noisy", "quiet", "romantic", "casual", "view"
        ],
        "Price": [
            "price", "prices", "pricing", "cost", "costs", "expensive", "pricey",
            "cheap", "affordable", "value", "worth", "money", "overpriced", 
            "reasonable", "deal", "bill", "check", "tip", "tax"
        ]
    },
    
    "cafe": {
        "Drinks & Coffee": [
            "coffee", "espresso", "latte", "cappuccino", "drink", "drinks", "beverage",
            "tea", "matcha", "smoothie", "brew", "iced", "hot", "milk", "syrup",
            "delicious", "tasty", "strong", "watered down", "bitter", "sweet"
        ],
        "Food & Pastries": [
            "pastry", "cake", "cookies", "muffin", "croissant", "sandwich", 
            "bagel", "toast", "breakfast", "snack", "food", "menu", "fresh"
        ],
        "Service": [
            "service", "staff", "barista", "baristas", "friendly", "attentive", 
            "helpful", "rude", "slow", "fast", "quick", "line", "wait", "welcoming"
        ],
        "Workspace & Ambiance": [
            "ambiance", "atmosphere", "vibe", "cozy", "comfortable", "clean", 
            "wifi", "internet", "workspace", "study", "laptop", "outlets", "plug",
            "noise", "quiet", "peaceful", "music", "seating", "table", "couch"
        ],
        "Price": [
            "price", "prices", "cost", "expensive", "pricey", "cheap", "affordable",
            "value", "worth", "money", "overpriced", "reasonable"
        ]
    },

    "bar": {
        "Drinks & Alcohol": [
            "drink", "drinks", "beer", "cocktail", "cocktails", "wine", "shot", 
            "shots", "liquor", "alcohol", "pour", "mixed", "menu", "draft", 
            "tap", "strong", "weak", "tasty"
        ],
        "Food & Snacks": [
            "food", "snack", "snacks", "fries", "wings", "nachos", "pizza", 
            "burger", "bar food", "menu", "taste", "portion"
        ],
        "Service": [
            "service", "bartender", "bartenders", "staff", "bouncer", "security",
            "server", "waitress", "friendly", "rude", "slow", "fast", "ignored", 
            "attentive", "cut off"
        ],
        "Vibe & Crowd": [
            "vibe", "vibes", "atmosphere", "music", "dj", "band", "live", "loud", 
            "noisy", "crowd", "crowded", "packed", "empty", "dance", "floor", 
            "lighting", "clean", "dirty", "restroom", "bathroom"
        ],
        "Price & Cover": [
            "price", "cost", "expensive", "cheap", "tab", "bill", "cover", 
            "cover charge", "entry", "happy hour", "deal", "overpriced"
        ]
    }
}

# Default F&B fallback if exact category isn't matched
DEFAULT_ASPECT_KEYWORDS = {
    "Food/Drinks": [
        "food", "drink", "meal", "menu", "taste", "delicious", "terrible", 
        "great", "poor", "amazing", "awful", "fresh", "stale", "quality"
    ],
    "Service": [
        "service", "staff", "employee", "waiter", "bartender", "manager",
        "friendly", "helpful", "rude", "professional", "attentive", "slow", "fast"
    ],
    "Ambiance": [
        "place", "atmosphere", "environment", "clean", "dirty", "vibe", "music",
        "comfortable", "noisy", "quiet", "crowded", "seating"
    ],
    "Price/Value": [
        "price", "cost", "expensive", "cheap", "affordable", "value", "worth",
        "money", "overpriced", "reasonable", "bill", "charge"
    ]
}

# Category aliases for flexible matching
CATEGORY_ALIASES = {
    "restaurant": ["restaurant", "diner", "eatery", "bistro", "grill", "steakhouse", "pizzeria"],
    "cafe": ["cafe", "coffee shop", "coffee", "coffeehouse", "tea house", "bakery"],
    "bar": ["bar", "pub", "club", "nightclub", "lounge", "brewery", "taproom", "dive bar"]
}

# Active aspect keywords
ASPECT_KEYWORDS = DEFAULT_ASPECT_KEYWORDS.copy()

# Load model and tokenizer
logger.info("Loading sentiment analysis model...")
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        top_k=None
    )
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise


def detect_business_category(category_input: str = None) -> str:
    if not category_input:
        return "default"
    
    category_lower = category_input.lower().strip()
    
    for main_category, aliases in CATEGORY_ALIASES.items():
        if any(alias in category_lower for alias in aliases):
            logger.info(f"Detected F&B category: {main_category}")
            return main_category
            
    logger.info(f"Unknown F&B category '{category_input}', using default F&B keywords")
    return "default"


def set_aspect_keywords_for_category(category: str = None):
    global ASPECT_KEYWORDS
    detected_category = detect_business_category(category)
    
    if detected_category == "default":
        ASPECT_KEYWORDS = DEFAULT_ASPECT_KEYWORDS.copy()
        logger.info("Using default F&B aspect keywords")
    else:
        ASPECT_KEYWORDS = CATEGORY_ASPECT_KEYWORDS.get(
            detected_category, 
            DEFAULT_ASPECT_KEYWORDS
        ).copy()
        logger.info(f"Loaded aspect keywords for category: {detected_category}")
    
    return ASPECT_KEYWORDS


def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)


def map_sentiment_label(label: str) -> str:
    label_mapping = {
        "positive": "Positive",
        "negative": "Negative",
        "neutral": "Neutral",
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }
    return label_mapping.get(label.lower(), label)


def analyze_review_for_aspects(review_text: str) -> Dict[str, List[Dict[str, Any]]]:
    if not review_text or not review_text.strip():
        return {}
    
    results = {aspect: [] for aspect in ASPECT_KEYWORDS.keys()}
    
    try:
        sentences = nltk.sent_tokenize(review_text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            for aspect, keywords in ASPECT_KEYWORDS.items():
                if any(keyword in sentence_lower for keyword in keywords):
                    try:
                        sentiment_results = sentiment_pipeline(sentence)[0]
                        top_sentiment = max(sentiment_results, key=lambda x: x['score'])
                        
                        results[aspect].append({
                            "sentiment": map_sentiment_label(top_sentiment['label']),
                            "score": round(top_sentiment['score'], 4),
                            "sentence": sentence.strip()
                        })
                    except Exception as e:
                        logger.error(f"Error analyzing sentence '{sentence}': {e}")
                        continue
                        
        # Remove empty aspects
        results = {k: v for k, v in results.items() if v}
        
    except Exception as e:
        logger.error(f"Error processing review: {e}")
        return {}
        
    return results


def analyze_multiple_reviews(reviews: List[str]) -> Dict[str, Any]:
    all_aspects = {aspect: [] for aspect in ASPECT_KEYWORDS.keys()}
    
    logger.info(f"Starting analysis of {len(reviews)} reviews")
    
    for idx, review in enumerate(reviews):
        review_results = analyze_review_for_aspects(review)
        for aspect, sentiments in review_results.items():
            all_aspects[aspect].extend(sentiments)
            
    aspect_summary = {}
    for aspect, sentiments in all_aspects.items():
        if sentiments:
            sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
            total_score = 0
            
            for item in sentiments:
                sentiment_counts[item["sentiment"]] += 1
                total_score += item["score"]
                
            total_mentions = len(sentiments)
            avg_score = total_score / total_mentions
            dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            
            aspect_summary[aspect] = {
                "total_mentions": total_mentions,
                "sentiment_breakdown": sentiment_counts,
                "average_confidence": round(avg_score, 4),
                "overall_sentiment": dominant_sentiment,
                "details": sentiments
            }
            
    return aspect_summary