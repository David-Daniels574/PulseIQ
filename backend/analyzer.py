"""
Analyzer module for Aspect-Based Sentiment Analysis (ABSA)
Uses Hugging Face's cardiffnlp/twitter-roberta-base-sentiment-latest model
"""

import nltk
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Category-specific aspect keywords for different business types
CATEGORY_ASPECT_KEYWORDS = {
    # RESTAURANTS, CAFES, FOOD & BEVERAGE
    "restaurant": {
        "Food/Product": [
            "food", "meal", "dish", "dishes", "taste", "flavor", "flavour", "cuisine", "menu",
            "breakfast", "lunch", "dinner", "appetizer", "dessert", "entree", "main course",
            "pizza", "burger", "pasta", "salad", "steak", "chicken", "seafood", "sushi",
            "delicious", "tasty", "fresh", "quality", "portion", "portions", "serving",
            "yummy", "amazing", "great", "excellent", "terrible", "bad", "good",
            "hot", "cold", "warm", "sweet", "bitter", "sour", "spicy", "bland"
        ],
        "Service": [
            "service", "staff", "waiter", "waitress", "server", "servers",
            "manager", "employee", "employees", "bartender", "host", "hostess",
            "friendly", "attentive", "helpful", "rude", "slow", "fast", "quick",
            "professional", "courteous", "polite", "wait", "waiting", "customer service",
            "team", "crew", "worker", "workers", "nice", "kind", "welcoming", "responsive"
        ],
        "Ambiance": [
            "ambiance", "ambience", "atmosphere", "environment", "decor", "decoration",
            "interior", "seating", "music", "lighting", "vibe", "vibes", "mood",
            "cozy", "comfortable", "clean", "dirty", "spacious", "crowded", "cramped",
            "noise", "noisy", "quiet", "peaceful", "romantic", "casual", "elegant",
            "place", "spot", "location", "area", "room", "space", "beautiful", "ugly",
            "nice", "lovely", "pleasant", "unpleasant", "busy", "relaxing", "view"
        ],
        "Price": [
            "price", "prices", "pricing", "cost", "costs", "expensive", "pricey",
            "cheap", "affordable", "value", "worth", "money", "overpriced", "underpriced",
            "reasonable", "budget", "deal", "deals", "discount", "discounts",
            "$", "dollar", "dollars", "paid", "pay", "charged", "charge", "bill", "check"
        ]
    },
    
    "cafe": {
        "Food/Product": [
            "coffee", "espresso", "latte", "cappuccino", "drink", "drinks", "beverage",
            "sandwich", "pastry", "cake", "cookies", "muffin", "croissant", "tea", "smoothie",
            "breakfast", "lunch", "snack", "food", "menu", "quality", "fresh",
            "delicious", "tasty", "yummy", "good", "bad", "excellent", "terrible"
        ],
        "Service": [
            "service", "staff", "barista", "baristas", "employee", "employees",
            "friendly", "attentive", "helpful", "rude", "slow", "fast", "quick",
            "professional", "courteous", "polite", "wait", "waiting", "customer service",
            "team", "crew", "worker", "nice", "kind", "welcoming", "efficient"
        ],
        "Ambiance": [
            "ambiance", "atmosphere", "environment", "decor", "interior", "seating",
            "music", "lighting", "vibe", "cozy", "comfortable", "clean", "spacious",
            "wifi", "internet", "workspace", "study", "noise", "quiet", "peaceful",
            "place", "spot", "location", "beautiful", "nice", "pleasant", "relaxing"
        ],
        "Price": [
            "price", "prices", "cost", "expensive", "pricey", "cheap", "affordable",
            "value", "worth", "money", "overpriced", "reasonable", "budget", "deal"
        ]
    },
    
    # HOTELS & ACCOMMODATIONS
    "hotel": {
        "Rooms/Facilities": [
            "room", "rooms", "bed", "beds", "bathroom", "shower", "toilet", "amenities",
            "clean", "dirty", "comfortable", "spacious", "cramped", "size", "view",
            "ac", "air conditioning", "heating", "wifi", "internet", "tv", "television",
            "towel", "towels", "linen", "sheets", "pillow", "pillows", "mattress",
            "modern", "outdated", "renovated", "maintained", "condition"
        ],
        "Service": [
            "service", "staff", "receptionist", "concierge", "housekeeping", "employees",
            "front desk", "check-in", "checkout", "friendly", "helpful", "professional",
            "attentive", "responsive", "rude", "slow", "courteous", "welcoming"
        ],
        "Location": [
            "location", "area", "neighborhood", "transport", "transportation", "access",
            "convenient", "central", "downtown", "airport", "station", "parking",
            "nearby", "close", "far", "distance", "walk", "walking distance"
        ],
        "Price": [
            "price", "rate", "cost", "expensive", "cheap", "affordable", "value",
            "worth", "money", "overpriced", "reasonable", "deal", "booking"
        ]
    },
    
    # RETAIL & SHOPPING
    "store": {
        "Product/Inventory": [
            "product", "products", "item", "items", "quality", "selection", "variety",
            "stock", "inventory", "availability", "fresh", "new", "used", "condition",
            "brand", "brands", "choice", "options", "range", "merchandise"
        ],
        "Service": [
            "service", "staff", "employee", "employees", "cashier", "sales", "help",
            "friendly", "helpful", "knowledgeable", "rude", "attentive", "professional",
            "customer service", "assistance", "support", "responsive"
        ],
        "Store Experience": [
            "store", "shop", "clean", "organized", "messy", "layout", "display",
            "atmosphere", "environment", "music", "lighting", "spacious", "crowded",
            "parking", "access", "location", "convenient"
        ],
        "Price": [
            "price", "prices", "cost", "expensive", "cheap", "affordable", "value",
            "deal", "deals", "discount", "sale", "overpriced", "reasonable", "worth"
        ]
    },
    
    # HEALTHCARE & MEDICAL
    "clinic": {
        "Medical Care": [
            "doctor", "doctors", "physician", "nurse", "nurses", "treatment", "care",
            "diagnosis", "examination", "checkup", "consultation", "professional",
            "competent", "knowledgeable", "experienced", "thorough", "careful",
            "attention", "quality", "medical", "health", "healing"
        ],
        "Service": [
            "service", "staff", "receptionist", "appointment", "scheduling", "wait",
            "waiting", "time", "friendly", "helpful", "rude", "courteous", "polite",
            "efficient", "professional", "responsive", "caring", "compassionate"
        ],
        "Facilities": [
            "facility", "facilities", "clinic", "office", "clean", "cleanliness",
            "hygiene", "equipment", "modern", "outdated", "comfortable", "spacious",
            "parking", "location", "access", "accessibility"
        ],
        "Cost": [
            "price", "cost", "fee", "fees", "expensive", "affordable", "insurance",
            "billing", "charge", "charges", "reasonable", "overpriced", "value"
        ]
    },
    
    # BEAUTY & WELLNESS
    "salon": {
        "Service/Result": [
            "haircut", "hair", "cut", "color", "style", "styling", "treatment",
            "manicure", "pedicure", "nails", "massage", "facial", "result", "results",
            "quality", "skill", "skillful", "talented", "professional", "expert",
            "good", "bad", "excellent", "terrible", "perfect", "amazing", "awful"
        ],
        "Staff": [
            "stylist", "stylists", "staff", "barber", "hairdresser", "technician",
            "friendly", "helpful", "rude", "professional", "attentive", "listening",
            "consultation", "advice", "recommendation", "experience", "experienced"
        ],
        "Ambiance": [
            "salon", "shop", "clean", "cleanliness", "hygiene", "atmosphere",
            "comfortable", "relaxing", "peaceful", "music", "decor", "modern",
            "nice", "pleasant", "welcoming", "space"
        ],
        "Price": [
            "price", "cost", "expensive", "cheap", "affordable", "value", "worth",
            "overpriced", "reasonable", "deal", "charge", "fee"
        ]
    },
    
    # GYM & FITNESS
    "gym": {
        "Equipment/Facilities": [
            "equipment", "machines", "weights", "cardio", "treadmill", "facility",
            "facilities", "clean", "maintained", "modern", "outdated", "variety",
            "selection", "pool", "sauna", "shower", "locker", "lockers", "space"
        ],
        "Staff/Trainers": [
            "staff", "trainer", "trainers", "instructor", "instructors", "coach",
            "friendly", "helpful", "knowledgeable", "professional", "motivating",
            "attentive", "supportive", "guidance", "service"
        ],
        "Environment": [
            "gym", "atmosphere", "environment", "clean", "cleanliness", "spacious",
            "crowded", "busy", "quiet", "music", "air conditioning", "ventilation",
            "parking", "location", "access", "hours", "timing"
        ],
        "Price": [
            "membership", "price", "cost", "fee", "expensive", "affordable", "value",
            "deal", "worth", "reasonable", "overpriced", "contract"
        ]
    },
    
    # AUTOMOTIVE
    "car_service": {
        "Service Quality": [
            "service", "work", "repair", "repairs", "maintenance", "quality",
            "professional", "thorough", "careful", "done", "fixed", "problem",
            "issue", "mechanic", "mechanics", "technician", "expert", "skilled"
        ],
        "Staff": [
            "staff", "mechanic", "mechanics", "technician", "manager", "friendly",
            "helpful", "honest", "trustworthy", "knowledgeable", "professional",
            "communication", "explain", "explanation", "transparent"
        ],
        "Timeliness": [
            "time", "timing", "wait", "waiting", "fast", "slow", "quick", "prompt",
            "appointment", "schedule", "delay", "delayed", "on time", "punctual"
        ],
        "Price": [
            "price", "cost", "expensive", "reasonable", "fair", "cheap", "affordable",
            "overpriced", "quote", "estimate", "charge", "fee", "value", "worth"
        ]
    }
}

# Default fallback keywords for unknown categories
DEFAULT_ASPECT_KEYWORDS = {
    "Product/Service": [
        "product", "service", "quality", "item", "good", "bad", "excellent",
        "terrible", "great", "poor", "amazing", "awful", "best", "worst",
        "work", "working", "broken", "effective", "useless"
    ],
    "Customer Service": [
        "service", "staff", "employee", "employees", "manager", "team",
        "friendly", "helpful", "rude", "professional", "attentive", "responsive",
        "support", "customer service", "assistance", "help", "care"
    ],
    "Experience": [
        "experience", "place", "location", "atmosphere", "environment", "clean",
        "comfortable", "convenient", "easy", "difficult", "pleasant", "unpleasant",
        "nice", "good", "bad", "recommend", "return"
    ],
    "Price/Value": [
        "price", "cost", "expensive", "cheap", "affordable", "value", "worth",
        "money", "overpriced", "reasonable", "deal", "fee", "charge", "paid"
    ]
}

# Category aliases for flexible matching
CATEGORY_ALIASES = {
    "restaurant": ["restaurant", "diner", "eatery", "bistro", "grill"],
    "cafe": ["cafe", "coffee shop", "coffee", "coffeehouse", "tea house"],
    "hotel": ["hotel", "motel", "inn", "resort", "lodge", "accommodation"],
    "store": ["store", "shop", "retail", "boutique", "mart", "supermarket"],
    "clinic": ["clinic", "hospital", "medical", "doctor", "healthcare"],
    "salon": ["salon", "spa", "barber", "beauty", "hair salon"],
    "gym": ["gym", "fitness", "health club", "workout", "fitness center"],
    "car_service": ["car service", "auto repair", "mechanic", "garage", "car repair"]
}

# Active aspect keywords (will be set based on business category)
ASPECT_KEYWORDS = DEFAULT_ASPECT_KEYWORDS.copy()

# Load model and tokenizer at module level for performance
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
    """
    Detect the business category from input string
    
    Args:
        category_input: Category or business type string (e.g., "restaurant", "coffee shop")
        
    Returns:
        Normalized category key for CATEGORY_ASPECT_KEYWORDS
    """
    if not category_input:
        return "default"
    
    category_lower = category_input.lower().strip()
    
    # Check against category aliases
    for main_category, aliases in CATEGORY_ALIASES.items():
        if any(alias in category_lower for alias in aliases):
            logger.info(f"Detected business category: {main_category}")
            return main_category
    
    logger.info(f"Unknown category '{category_input}', using default keywords")
    return "default"


def set_aspect_keywords_for_category(category: str = None):
    """
    Set the global ASPECT_KEYWORDS based on business category
    
    Args:
        category: Business category string (e.g., "restaurant", "hotel", "cafe")
    """
    global ASPECT_KEYWORDS
    
    detected_category = detect_business_category(category)
    
    if detected_category == "default":
        ASPECT_KEYWORDS = DEFAULT_ASPECT_KEYWORDS.copy()
        logger.info("Using default aspect keywords")
    else:
        ASPECT_KEYWORDS = CATEGORY_ASPECT_KEYWORDS.get(
            detected_category, 
            DEFAULT_ASPECT_KEYWORDS
        ).copy()
        logger.info(f"Loaded aspect keywords for category: {detected_category}")
    
    return ASPECT_KEYWORDS


def get_available_categories() -> List[str]:
    """
    Get list of all available business categories
    
    Returns:
        List of category names
    """
    return list(CATEGORY_ASPECT_KEYWORDS.keys())


def download_nltk_data():
    """
    Download required NLTK data (punkt tokenizer)
    """
    try:
        nltk.data.find('tokenizers/punkt')
        logger.info("NLTK punkt tokenizer already downloaded")
    except LookupError:
        logger.info("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)
        logger.info("NLTK punkt tokenizer downloaded successfully")
    
    # Also download punkt_tab for newer NLTK versions
    try:
        nltk.data.find('tokenizers/punkt_tab')
        logger.info("NLTK punkt_tab tokenizer already downloaded")
    except LookupError:
        logger.info("Downloading NLTK punkt_tab tokenizer...")
        nltk.download('punkt_tab', quiet=True)
        logger.info("NLTK punkt_tab tokenizer downloaded successfully")


def map_sentiment_label(label: str) -> str:
    """
    Map model output labels to readable sentiment names
    """
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
    """
    Analyze a review text for aspects and their sentiments
    
    Args:
        review_text: The review text to analyze
        
    Returns:
        Dictionary with aspects as keys and list of sentiment results as values
        Example: {
            "Food": [
                {
                    "sentiment": "Positive",
                    "score": 0.98,
                    "sentence": "The food was absolutely delicious!"
                }
            ]
        }
    """
    if not review_text or not review_text.strip():
        return {}
    
    # Initialize results dictionary
    results = {aspect: [] for aspect in ASPECT_KEYWORDS.keys()}
    
    try:
        # Tokenize the review into sentences
        sentences = nltk.sent_tokenize(review_text)
        logger.info(f"Processing review with {len(sentences)} sentences")
        
        # Process each sentence
        for sentence in sentences:
            sentence_lower = sentence.lower()
            logger.debug(f"Analyzing sentence: {sentence}")
            
            # Check each aspect for keyword matches
            for aspect, keywords in ASPECT_KEYWORDS.items():
                # Check if any keyword is in the sentence
                if any(keyword in sentence_lower for keyword in keywords):
                    logger.info(f"Found {aspect} aspect in sentence: {sentence[:50]}...")
                    try:
                        # Run sentiment analysis on the sentence
                        sentiment_results = sentiment_pipeline(sentence)[0]
                        
                        # Get the top sentiment (highest score)
                        top_sentiment = max(sentiment_results, key=lambda x: x['score'])
                        
                        # Store the result
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
    """
    Analyze multiple reviews and aggregate the results
    
    Args:
        reviews: List of review texts
        
    Returns:
        Aggregated analysis results with aspect-wise sentiment breakdown
    """
    all_aspects = {aspect: [] for aspect in ASPECT_KEYWORDS.keys()}
    
    logger.info(f"Starting analysis of {len(reviews)} reviews")
    
    for idx, review in enumerate(reviews):
        logger.info(f"Analyzing review {idx + 1}/{len(reviews)}")
        review_results = analyze_review_for_aspects(review)
        logger.info(f"Review {idx + 1} found aspects: {list(review_results.keys())}")
        
        # Aggregate results
        for aspect, sentiments in review_results.items():
            all_aspects[aspect].extend(sentiments)
    
    # Calculate statistics for each aspect
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
            
            # Determine overall sentiment for this aspect
            dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            
            aspect_summary[aspect] = {
                "total_mentions": total_mentions,
                "sentiment_breakdown": sentiment_counts,
                "average_confidence": round(avg_score, 4),
                "overall_sentiment": dominant_sentiment,
                "details": sentiments
            }
    
    return aspect_summary
