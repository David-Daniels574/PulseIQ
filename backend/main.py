"""
FastAPI application for Aspect-Based Sentiment Analysis (ABSA)
Integrates with Google Maps API to fetch business reviews
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uvicorn
import logging
import math
from services.twitter_scraper import get_restaurant_reviews
import os
from dotenv import load_dotenv
import googlemaps
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import nltk

import logging
logging.basicConfig(level=logging.INFO)
from collections import Counter
from datetime import timedelta
 
# New service imports
from services.confidence_engine import (
    compute_all_aspect_confidence,
    compute_sentiment_variance,
    cluster_complaints,
)
from services.framework_llm import generate_all_frameworks
from services.agentic_swot import generate_agentic_swot


from analyzer import (
    analyze_review_for_aspects,
    analyze_multiple_reviews,
    download_nltk_data,
    set_aspect_keywords_for_category
)

from llm_insights import (
    generate_business_insights,
    generate_quick_summary,
    ingest_reviews_to_chroma,
    generate_review_response_template
)

from database import get_db, init_db
import crud

# Import scraper service
from services.scraper import scrape_google_news, scrape_multiple_queries

# Import forecasting service
from models.forecasting import generate_rating_forecast, get_forecast_summary
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Aspect-Based Sentiment Analysis API",
    description="Analyze business reviews using ABSA with Google Maps integration",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Current frontend port
        "http://localhost:3000",  # Common React port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if GOOGLE_MAPS_API_KEY:
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    logger.info("Google Maps API client initialized")
else:
    gmaps = None
    logger.warning("Google Maps API key not found. Business search will be disabled.")


# Pydantic models
class ReviewRequest(BaseModel):
    """Request model for direct review analysis"""
    text: str = Field(..., description="Review text to analyze")


class BusinessRequest(BaseModel):
    """Request model for business review analysis via Google Maps"""
    business_name: str = Field(..., description="Name of the business")
    category: Optional[str] = Field(None, description="Category of the business (e.g., restaurant, hotel)")
    location: str = Field(..., description="Location (city, state, or full address)")


class InsightsRequest(BaseModel):
    """Request model for generating LLM insights from ABSA results"""
    business_name: str = Field(..., description="Name of the business")
    business_info: Dict[str, Any] = Field(..., description="Business information")
    absa_results: Dict[str, Any] = Field(..., description="ABSA analysis results")
    raw_reviews: Optional[list] = Field(None, description="Optional raw review texts")


class ResponseTemplateRequest(BaseModel):
    """Request model for generating review response templates"""
    aspect: str = Field(..., description="Aspect (Food, Service, Ambiance, Price)")
    sentiment: str = Field(..., description="Sentiment (Positive, Negative, Neutral)")
    business_name: str = Field(..., description="Name of the business")


class CompetitorAnalysisRequest(BaseModel):
    """Request model for competitor analysis"""
    business_name: str = Field(..., description="Name of your business")
    category: str = Field(..., description="Business category (e.g., restaurant, hotel, gym)")
    location: str = Field(..., description="Location (city, state, or full address)")
    radius: Optional[int] = Field(5000, description="Search radius in meters (default: 5000m = ~3 miles)")


class MarketIntelligenceRequest(BaseModel):
    """Request for the Market Intelligence page (forecast + news)"""
    business_name: str     = Field(..., description="Name of the restaurant")
    city: str              = Field(..., description="City e.g. 'Mumbai'")
    category: Optional[str] = Field("Restaurant", description="Business category for ML forecast")
    current_rating: float  = Field(..., ge=1.0, le=5.0, description="Current average rating")
    sentiment_score: Optional[float] = Field(None, ge=0.0, le=1.0,
        description="Sentiment score 0-1. If omitted, derived from stored ABSA results.")
    months_ahead: Optional[int] = Field(6, ge=1, le=12, description="Months to forecast (default 6)")
    location: Optional[str]     = Field(None, description="Location string for news search (defaults to city)")

class ForecastRequest(BaseModel):
    """Request model for star rating forecast"""
    business_name: str = Field(..., description="Name of the business")
    city: str = Field(..., description="City name (e.g., 'Mumbai', 'San Francisco')")
    category: str = Field(..., description="Business category (e.g., 'Vegan Street Food', 'Restaurant')")
    current_rating: float = Field(..., ge=1.0, le=5.0, description="Current average rating (1.0-5.0)")
    sentiment_score: float = Field(..., ge=0.0, le=1.0, description="Sentiment score from ABSA (0.0-1.0)")
    months_ahead: Optional[int] = Field(6, ge=1, le=12, description="Number of months to forecast (default: 6)")
    
class OverviewRequest(BaseModel):
    """Request for the Overview dashboard page"""
    business_name: str = Field(..., description="Name of the restaurant")
    area: str          = Field(..., description="Area/neighbourhood e.g. 'Colaba'")
    city: str          = Field(..., description="City e.g. 'Mumbai'")
    twitter_query: Optional[str] = Field(None, description="Optional specific query for Twitter. Defaults to business name.")
    months_back: Optional[int] = Field(6, ge=1, le=24, description="How many months of data to include (default 6)")


class SWOTFrameworkRequest(BaseModel):
    """Request for dedicated SWOT framework generation"""
    business_name: str = Field(..., description="Name of the restaurant")
    area: str = Field(..., description="Area/neighbourhood e.g. 'Colaba'")
    city: str = Field(..., description="City e.g. 'Mumbai'")
    twitter_query: Optional[str] = Field(None, description="Optional specific query for Twitter. Defaults to business name + city.")
    months_back: Optional[int] = Field(6, ge=1, le=24, description="How many months of data to include (default 6)")
 
class CompetitorRequest(BaseModel):
    """Request for the Competitor Analysis page"""
    business_name: str = Field(..., description="Name of your restaurant")
    area: str          = Field(..., description="Area/neighbourhood e.g. 'Colaba'")
    city: str          = Field(..., description="City e.g. 'Mumbai'")
    category: Optional[str] = Field("restaurant", description="Business category (default: restaurant)")
    radius: Optional[int]   = Field(3000, description="Search radius in metres (default 3000)")
 
class BusinessResponse(BaseModel):
    id: int
    place_id: str
    name: str
    category: Optional[str]
    address: Optional[str]
    location: Optional[str]
    area: Optional[str]            # V2 Field
    rating: Optional[float]
    total_reviews: Optional[int]
    
    model_config = ConfigDict(from_attributes=True) # orm_mode=True if using Pydantic v1

class AggregatedABSAResponse(BaseModel):
    aspect: str
    overall_sentiment: Optional[str]
    confidence_score: Optional[float]
    source_breakdown: Optional[Dict[str, Any]]
    conflict_flag: bool
    conflict_detail: Optional[str]

    model_config = ConfigDict(from_attributes=True)
    
class FrameworkReportResponse(BaseModel):
    framework: str
    result_json: Dict[str, Any]
    sources_used: Optional[List[str]]
    avg_confidence: Optional[float]

    model_config = ConfigDict(from_attributes=True)


class FrameworkCitationResponse(BaseModel):
    framework: str
    quadrant: str
    point_id: str
    point_label: str
    confidence_pct: Optional[float]
    suggestion: Optional[str]
    derived_insight: Optional[str]
    source_type: str
    source_strength: Optional[str]
    source_quote: str
    source_reference: Optional[str]
    source_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)
 

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize required resources on startup"""
    logger.info("Starting up the application...")
    
    # Initialize NLTK data
    download_nltk_data()
    
    # Initialize database
    try:
        logger.info("Initializing database connection...")
        init_db()
        logger.info("✅ Database connection initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization warning: {e}")
        logger.warning("Application will continue, but database features may not work")
    
    logger.info("Application startup complete!")


# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to the Aspect-Based Sentiment Analysis API with LLM Insights & Market Intelligence",
        "version": "3.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze a single review text",
            "/analyze/business": "POST - Fetch and analyze business reviews from Google Maps",
            "/analyze/business/insights": "POST - Fetch reviews, analyze, AND generate strategic insights (STORED IN DB)",
            "/analyze/frameworks/swot": "POST - Generate SWOT framework with source citations",
            "/analyze/competitors": "POST - Find and analyze top 4 competitors in your area",
            "/market-intelligence": "POST - Star-rating forecast + industry trend and market news",
            "/insights/generate": "POST - Generate insights from existing ABSA results",
            "/insights/response-template": "POST - Generate review response templates",
            "/history": "GET - View analysis history",
            "/businesses": "GET - List all analyzed businesses",
            "/business/{place_id}/reports": "GET - Get all reports for a specific business",
            "/categories": "GET - List all supported business categories",
            "/docs": "GET - Interactive API documentation"
        },
        "features": [
            "Aspect-Based Sentiment Analysis for 8+ business categories",
            "Multi-Category Support (Restaurant, Hotel, Gym, Salon, etc.)",
            "Google Maps Reviews Integration",
            "Competitor Analysis & Benchmarking",
            "Market Intelligence - Industry Trends & News",
            "Media Monitoring & Brand Tracking",
            "AI-Powered Strategic Recommendations using Gemini",
            "RAG-Enhanced Context-Aware Insights",
            "PostgreSQL Database Storage",
            "Analysis History Tracking",
            "Marketing & PR Action Plans",
            "Operational Improvement Suggestions"
        ]
    }

# Debug endpoint to test NLTK
@app.get("/debug/nltk")
async def debug_nltk():
    """Test NLTK tokenization"""
    
    test_text = "The coffee was great. The staff were friendly."
    try:
        sentences = nltk.sent_tokenize(test_text)
        return {
            "status": "success",
            "test_text": test_text,
            "sentences": sentences,
            "sentence_count": len(sentences)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Debug endpoint to test web scraper
@app.get("/debug/scraper")
async def debug_scraper(query: str = "Starbucks Mumbai"):
    """Test web scraper functionality"""
    try:
        logger.info(f"Testing scraper with query: {query}")
        
        # Split query into business name and location
        parts = query.rsplit(' ', 1)
        if len(parts) == 2:
            business_name, location = parts
        else:
            business_name = query
            location = "Mumbai"
        
        articles = scrape_google_news(
            query_term=business_name,
            location=location,
            max_results=5
        )
        
        return {
            "status": "success",
            "query": query,
            "business_name": business_name,
            "location": location,
            "articles_found": len(articles),
            "articles": articles
        }
    except Exception as e:
        logger.error(f"Scraper test error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

@app.post("/analyze/business/insights")
async def analyze_business_overview(
    request: OverviewRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Overview page - aggregates Google Maps + Twitter data,
    runs ABSA on all sources, computes confidence scores, and returns
    everything needed for the Overview dashboard.
    """
    start_time = datetime.now()
    logger.info(f"STARTING INSIGHTS PIPELINE FOR: {request.business_name}")

    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")

    try:
        # Step 1: Resolve place via Google Maps
        query = f"{request.business_name} {request.area} {request.city}"
        places_result = gmaps.places(query=query)
        if not places_result.get("results"):
            raise HTTPException(status_code=404, detail=f"No business found: {query}")

        place = places_result["results"][0]
        place_id = place["place_id"]
        place_name = place["name"]
        place_addr = place.get("formatted_address", "")

        details = gmaps.place(
            place_id=place_id,
            fields=["name", "rating", "user_ratings_total", "reviews"],
        )
        result_data = details["result"]
        gmap_reviews = result_data.get("reviews", [])
        gmap_rating = result_data.get("rating", 0)
        gmap_total = result_data.get("user_ratings_total", 0)
        logger.info("Step 1 complete (Google Maps API)")

        # Step 2: DB upsert for business
        business_db = crud.get_or_create_business(
            db=db,
            place_id=place_id,
            name=place_name,
            category="restaurant",
            address=place_addr,
            location=request.city,
            latitude=place.get("geometry", {}).get("location", {}).get("lat"),
            longitude=place.get("geometry", {}).get("location", {}).get("lng"),
            rating=gmap_rating,
            total_reviews=gmap_total,
        )
        logger.info("Step 2 complete (DB upsert business)")

        # Step 3: ABSA setup
        set_aspect_keywords_for_category("restaurant")

        # Step 4: Google Maps ABSA + store reviews
        gmap_texts = [r["text"] for r in gmap_reviews if r.get("text")]
        gmap_absa = analyze_multiple_reviews(gmap_texts) if gmap_texts else {}

        for r in gmap_reviews:
            if r.get("text"):
                crud.create_review(
                    db=db,
                    business_id=business_db.id,
                    review_text=r["text"],
                    author_name=r.get("author_name"),
                    rating=r.get("rating"),
                    review_date=(datetime.fromtimestamp(r["time"]) if r.get("time") else None),
                    source="google_maps",
                )
        logger.info("Step 4 complete (Google Maps ABSA + store reviews)")

        # Step 5: Twitter fetch + ABSA + store reviews
        twitter_query = request.twitter_query or f"{request.business_name} {request.city}"
        try:
            twitter_reviews = get_restaurant_reviews(twitter_query) or []
        except Exception as twitter_err:
            logger.warning(f"Twitter scraper failed: {twitter_err}")
            twitter_reviews = []

        twitter_texts = [t.get("text", "").strip() for t in twitter_reviews if t.get("text")]
        twitter_absa = analyze_multiple_reviews(twitter_texts) if twitter_texts else {}

        for t in twitter_reviews:
            text = t.get("text")
            if text:
                crud.create_review(
                    db=db,
                    business_id=business_db.id,
                    review_text=text,
                    author_name="twitter_user",
                    rating=None,
                    review_date=None,
                    source="twitter",
                )
        logger.info("Step 5 complete (Twitter ABSA + store reviews)")

        # Step 6: Build combined ABSA over all review text sources
        all_review_texts = gmap_texts + twitter_texts
        combined_absa = analyze_multiple_reviews(all_review_texts) if all_review_texts else {}

        # Step 7: Confidence engine
        aggregated = compute_all_aspect_confidence(
            gmap_absa=gmap_absa,
            twitter_absa=twitter_absa,
            months_back=request.months_back,
        )
        variances = compute_sentiment_variance(aggregated)

        negative_sentences = []
        for src_name, src_absa in [("google_maps", gmap_absa), ("twitter", twitter_absa)]:
            for aspect, data in src_absa.items():
                if isinstance(data, dict):
                    for detail in data.get("details", []):
                        if detail.get("sentiment") == "Negative":
                            negative_sentences.append(
                                {
                                    "sentence": detail.get("sentence", ""),
                                    "aspect": aspect,
                                    "source": src_name,
                                    "confidence": detail.get("score", 0.0),
                                }
                            )
        mece_clusters = cluster_complaints(negative_sentences)
        logger.info("Step 7 complete (confidence + MECE clustering)")

        # Step 8: Store aggregated ABSA
        analysis_db = crud.create_analysis(
            db=db,
            business_id=business_db.id,
            analysis_type="absa_full",
            total_reviews_analyzed=len(all_review_texts),
            aspect_results={
                "combined": combined_absa,
                "google_maps": gmap_absa,
                "twitter": twitter_absa,
            },
            months_back=request.months_back,
            sources_used={
                "google_maps": len(gmap_texts),
                "twitter": len(twitter_texts),
            },
        )
        crud.save_aggregated_absa(
            db=db,
            business_id=business_db.id,
            analysis_id=analysis_db.id,
            aspect_confidence_list=aggregated,
            mece_clusters=mece_clusters,
            sentiment_variances=variances,
        )
        logger.info("Step 8 complete (store aggregated ABSA results)")

        # Step 9: Build response payload
        all_sentiments = [a["overall_sentiment"] for a in aggregated]
        sentiment_counts = Counter(all_sentiments)
        total_aspects = len(all_sentiments) or 1
        sentiment_breakdown = {
            "positive": round(sentiment_counts.get("Positive", 0) / total_aspects * 100, 1),
            "neutral": round(sentiment_counts.get("Neutral", 0) / total_aspects * 100, 1),
            "negative": round(sentiment_counts.get("Negative", 0) / total_aspects * 100, 1),
        }

        overall_confidence = round(
            sum(a["confidence_score"] for a in aggregated) / (len(aggregated) or 1), 1
        )

        ratings = [r for r in [gmap_rating] if r]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else gmap_rating

        source_breakdown = {
            "google_maps": {
                "review_count": len(gmap_texts),
                "avg_rating": gmap_rating,
                "total_on_platform": gmap_total,
            },
            "twitter": {
                "review_count": len(twitter_texts),
                "query_used": twitter_query,
            },
        }

        month_buckets: Dict[str, int] = {}
        for r in gmap_reviews:
            if r.get("time"):
                dt = datetime.fromtimestamp(r["time"])
                key = dt.strftime("%Y-%m")
                month_buckets[key] = month_buckets.get(key, 0) + 1

        sorted_months = sorted(month_buckets.keys())
        review_volume_trend = [{"month": m, "count": month_buckets[m]} for m in sorted_months]

        aspect_mention_counts: Dict[str, int] = {}
        for src_absa in [gmap_absa, twitter_absa]:
            for aspect, data in src_absa.items():
                if isinstance(data, dict):
                    aspect_mention_counts[aspect] = (
                        aspect_mention_counts.get(aspect, 0) + data.get("total_mentions", 0)
                    )

        top_keywords = sorted(
            [{"keyword": k, "count": v} for k, v in aspect_mention_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        aspect_sentiment = [
            {
                "aspect": a["aspect"],
                "overall_sentiment": a["overall_sentiment"],
                "confidence_score": a["confidence_score"],
                "conflict": a["conflict_flag"],
                "conflict_detail": a.get("conflict_detail"),
                "source_breakdown": a.get("source_breakdown", {}),
                "mention_count": aspect_mention_counts.get(a["aspect"], 0),
            }
            for a in aggregated
        ]

        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        crud.log_analysis(
            db=db,
            business_name=place_name,
            category="restaurant",
            location=request.city,
            endpoint="/analyze/business/insights",
            status="success",
            execution_time_ms=execution_time,
        )

        return {
            "status": "success",
            "business_info": {
                "name": place_name,
                "area": request.area,
                "city": request.city,
                "address": place_addr,
                "place_id": place_id,
                "twitter_query_used": twitter_query,
                "months_back": request.months_back,
            },
            "summary_stats": {
                "total_reviews": len(all_review_texts),
                "avg_rating": avg_rating,
                "overall_confidence": overall_confidence,
            },
            "sentiment_breakdown": sentiment_breakdown,
            "source_breakdown": source_breakdown,
            "review_volume_trend": review_volume_trend,
            "top_keywords": top_keywords,
            "aspect_sentiment": aspect_sentiment,
            "execution_time_ms": execution_time,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Overview endpoint error: {e}")
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        try:
            crud.log_analysis(
                db=db,
                business_name=request.business_name,
                category="restaurant",
                location=request.city,
                endpoint="/analyze/business/insights",
                status="failed",
                error_message=str(e),
                execution_time_ms=execution_time,
            )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/frameworks/swot")
async def analyze_swot_framework(
    request: SWOTFrameworkRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Dedicated SWOT API.
    Reuses existing DB data prepared by /analyze/business/insights
    to generate source-cited SWOT quickly (no re-scraping).
    """
    start_time = datetime.now()

    try:
        business_db = crud.get_business_by_name(db, request.business_name, request.city)
        if not business_db:
            raise HTTPException(
                status_code=404,
                detail="Business not found in DB. Run /analyze/business/insights first.",
            )

        analysis_db = (
            crud.get_latest_analysis(db, business_db.id, "absa_full")
            or crud.get_latest_analysis(db, business_db.id, "absa_with_insights")
            or crud.get_latest_analysis(db, business_db.id, "absa")
        )
        if not analysis_db:
            raise HTTPException(
                status_code=400,
                detail="No ABSA analysis found. Run /analyze/business/insights first.",
            )

        aggregated_rows = crud.get_aggregated_absa(db, business_db.id)
        if not aggregated_rows:
            raise HTTPException(
                status_code=400,
                detail="No aggregated ABSA found. Run /analyze/business/insights first.",
            )

        aggregated = [
            {
                "aspect": row.aspect,
                "overall_sentiment": row.overall_sentiment,
                "confidence_score": row.confidence_score,
                "source_breakdown": row.source_breakdown,
                "conflict_flag": row.conflict_flag,
                "conflict_detail": row.conflict_detail,
            }
            for row in aggregated_rows
        ]

        reviews = crud.get_reviews_by_business(db, business_db.id)
        gmap_texts = [r.review_text for r in reviews if (r.source or "") == "google_maps" and r.review_text]
        twitter_texts = [r.review_text for r in reviews if (r.source or "") == "twitter" and r.review_text]
        all_review_texts = gmap_texts + twitter_texts

        latest_competitors = crud.get_latest_competitors(db, business_db.id)
        competitor_summaries = [
            {
                "name": c.competitor_name,
                "rating": c.competitor_rating,
                "reviews": c.competitor_reviews,
                "rating_difference": c.rating_difference,
                "aspect_scores": c.competitor_aspect_scores or {},
            }
            for c in latest_competitors
        ]
        latest_news_rows = crud.get_scraping_results_by_business(db, business_db.id, limit=20)
        news_mentions = [
            {
                "headline": n.headline,
                "source_name": n.source_name,
                "link": n.link,
            }
            for n in latest_news_rows
        ]
        # Keep payload format unchanged while improving source attribution per citation.
        review_evidence = []
        for r in reviews[:60]:
            if not r.review_text:
                continue
            src = r.source or "google_maps"
            reference = f"{src}_review_id:{r.id}"
            if r.author_name:
                reference = f"{src}_author:{r.author_name}|review_id:{r.id}"
            review_evidence.append(
                {
                    "source": src,
                    "text": r.review_text,
                    "source_reference": reference,
                    "author": r.author_name,
                }
            )

        swot_payload = generate_agentic_swot(
            business_name=business_db.name,
            city=request.city,
            aggregated_absa=aggregated,
            competitor_summaries=competitor_summaries,
            news_mentions=news_mentions,
            review_evidence=review_evidence,
        )

        swot_reports = crud.save_framework_reports(
            db=db,
            business_id=business_db.id,
            analysis_id=analysis_db.id,
            frameworks={"swot": swot_payload["result_json"]},
            avg_confidence_per_framework={"swot": float(swot_payload["confidence_pct"])},
            sources_used=["google_maps", "twitter"] + (["news"] if news_mentions else []),
        )
        if swot_reports:
            crud.save_framework_citations(
                db=db,
                business_id=business_db.id,
                framework_report_id=swot_reports[0].id,
                citations=swot_payload.get("citations", []),
            )

        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        crud.log_analysis(
            db=db,
            business_name=business_db.name,
            category="restaurant",
            location=request.city,
            endpoint="/analyze/frameworks/swot",
            status="success",
            execution_time_ms=execution_time,
        )

        return {
            "status": "success",
            "business_info": {
                "name": business_db.name,
                "area": request.area,
                "city": request.city,
                "address": business_db.address,
                "place_id": business_db.place_id,
                "twitter_query_used": request.twitter_query or f"{request.business_name} {request.city}",
                "months_back": request.months_back,
            },
            "summary_stats": {
                "total_reviews": len(all_review_texts),
                "avg_rating": business_db.rating,
            },
            "framework": {
                "type": "swot",
                "confidence_pct": swot_payload.get("confidence_pct", 0),
                "result_json": swot_payload.get("result_json", {}),
            },
            "execution_time_ms": execution_time,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SWOT framework endpoint error: {e}")
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        try:
            crud.log_analysis(
                db=db,
                business_name=request.business_name,
                category="restaurant",
                location=request.city,
                endpoint="/analyze/frameworks/swot",
                status="failed",
                error_message=str(e),
                execution_time_ms=execution_time,
            )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/business/{place_id}/reports")
async def get_business_reports(place_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Return saved framework reports for a business.
    Includes point-level citations for SWOT.
    """
    business = crud.get_business_by_place_id(db, place_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    reports = crud.get_all_framework_reports(db, business.id)
    out: List[Dict[str, Any]] = []

    for report in reports:
        item = {
            "framework": str(report.framework),
            "result_json": report.result_json,
            "sources_used": report.sources_used,
            "avg_confidence": report.avg_confidence,
            "generated_at": report.generated_at,
        }
        framework_name = report.framework.value if hasattr(report.framework, "value") else str(report.framework)
        if framework_name == "swot":
            citations = crud.get_framework_citations(db, report.id)
            item["citations"] = [
                {
                    "framework": c.framework,
                    "quadrant": c.quadrant,
                    "point_id": c.point_id,
                    "point_label": c.point_label,
                    "confidence_pct": c.confidence_pct,
                    "suggestion": c.suggestion,
                    "derived_insight": c.derived_insight,
                    "source_type": c.source_type,
                    "source_strength": c.source_strength,
                    "source_quote": c.source_quote,
                    "source_reference": c.source_reference,
                    "source_url": c.source_url,
                }
                for c in citations
            ]
        out.append(item)

    return {
        "status": "success",
        "business": {
            "place_id": business.place_id,
            "name": business.name,
            "city": business.location,
        },
        "reports": out,
    }

# Generate review response template
@app.post("/insights/response-template")
async def create_response_template(request: ResponseTemplateRequest) -> Dict[str, Any]:
    """
    Generate a professional review response template using Gemini LLM
    
    Args:
        request: ResponseTemplateRequest with aspect, sentiment, and business name
        
    Returns:
        Review response template
    """
    try:
        logger.info(f"Generating response template for {request.aspect} - {request.sentiment}")
        
        template = generate_review_response_template(
            aspect=request.aspect,
            sentiment=request.sentiment,
            business_name=request.business_name
        )
        
        return {
            "status": "success",
            "aspect": request.aspect,
            "sentiment": request.sentiment,
            "business_name": request.business_name,
            "response_template": template
        }
        
    except Exception as e:
        logger.error(f"Error generating response template: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ───────────────────────────────────────────────────────────────────
# 4.  REPLACE  /analyze/competitors  (Competitor Analysis page)
# ───────────────────────────────────────────────────────────────────
 
@app.post("/analyze/competitors")
async def analyze_competitors(
    request: CompetitorRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Competitor Analysis page.
 
    Returns:
    - main_business: name, rating, total_reviews
    - market_position: Leader / Challenger / Follower
    - avg_competitor_rating, avg_competitor_reviews, rating_vs_avg
    - competitors: list of top-5 with name/rating/reviews/status/category/position
    - rating_vs_reviews_chart: [{name, rating, reviews}] for scatter graph
    - aspect_showdown: your scores vs competitor avg for Food/Service/Ambiance/Price/Location
    """
    start_time = datetime.now()
 
    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
 
    try:
        # ── Resolve main business ──────────────────────────────────
        main_db = crud.get_business_by_name(db, request.business_name, request.city)
        main_price_level = None
 
        if not main_db:
            query = f"{request.business_name} {request.area} {request.city}"
            places = gmaps.places(query=query)
            if not places.get("results"):
                raise HTTPException(status_code=404, detail=f"Business not found: {query}")
            place = places["results"][0]
            det   = gmaps.place(
                place_id=place["place_id"],
                fields=["name", "rating", "user_ratings_total", "formatted_address", "price_level"],
            )["result"]
            main_price_level = det.get("price_level")
            main_db = crud.get_or_create_business(
                db=db,
                place_id=place["place_id"],
                name=place["name"],
                category=request.category,
                address=det.get("formatted_address", ""),
                location=request.city,
                latitude=place.get("geometry", {}).get("location", {}).get("lat"),
                longitude=place.get("geometry", {}).get("location", {}).get("lng"),
                rating=det.get("rating"),
                total_reviews=det.get("user_ratings_total", 0),
            )
        else:
            try:
                main_details = gmaps.place(
                    place_id=main_db.place_id,
                    fields=["price_level"],
                ).get("result", {})
                main_price_level = main_details.get("price_level")
            except Exception:
                main_price_level = None
 
        if not main_db.latitude or not main_db.longitude:
            raise HTTPException(status_code=400, detail="Main business has no coordinates. Run /analyze/business/insights first.")
 
        your_rating  = float(main_db.rating or 0)
        your_reviews = int(main_db.total_reviews or 0)
 
        # ── Find nearby competitors ────────────────────────────────
        nearby = gmaps.places_nearby(
            location=(main_db.latitude, main_db.longitude),
            radius=request.radius,
            keyword=request.category,
        )
        nearby_candidates = [
            p for p in nearby.get("results", [])
            if p["place_id"] != main_db.place_id and p.get("rating")
        ]

        # Prefer competitors in a comparable price band (if available from Google)
        price_matched = []
        price_unmatched = []
        for p in nearby_candidates:
            p_level = p.get("price_level")
            if main_price_level is None or p_level is None:
                price_matched.append(p)
            elif abs(int(p_level) - int(main_price_level)) <= 1:
                price_matched.append(p)
            else:
                price_unmatched.append(p)

        raw_competitors = price_matched if len(price_matched) >= 3 else (price_matched + price_unmatched)
        raw_competitors.sort(
            key=lambda p: (p.get("rating", 0), p.get("user_ratings_total", 0)),
            reverse=True,
        )
        top5 = raw_competitors[:5]
 
        # ── Fetch/store competitor details + ABSA ─────────────────
        set_aspect_keywords_for_category(request.category)
 
        target_aspects = ["Food", "Service", "Ambiance", "Price", "Location"]
        # "Location" is inferred from rating since Google Maps reviews often mention it
 
        def compute_aspect_scores_1_5(absa: Dict[str, Any]) -> Dict[str, float]:
            scores: Dict[str, float] = {}
            for asp, data in absa.items():
                if not isinstance(data, dict):
                    continue
                bd = data.get("sentiment_breakdown", {})
                pos, neg, neu = bd.get("Positive", 0), bd.get("Negative", 0), bd.get("Neutral", 0)
                total = pos + neg + neu
                if total == 0:
                    continue
                scores[asp] = round(1 + 4 * (pos + 0.5 * neu) / total, 2)
            return scores
 
        competitors_out = []
        competitor_aspect_scores: Dict[str, Dict[str, float]] = {}

        def _composite_market_score(rating: float, reviews: int, max_log_reviews: float) -> float:
            # Score in [0, 1]: rating quality dominates, review volume adds trust signal.
            rating_norm = max(0.0, min(1.0, rating / 5.0))
            volume_norm = 0.0 if max_log_reviews <= 0 else min(1.0, math.log1p(max(0, reviews)) / max_log_reviews)
            return 0.7 * rating_norm + 0.3 * volume_norm
 
        for rank, place in enumerate(top5, start=1):
            comp_db = crud.get_or_create_business(
                db=db,
                place_id=place["place_id"],
                name=place.get("name", ""),
                category=request.category,
                address=place.get("vicinity", ""),
                location=request.city,
                latitude=place.get("geometry", {}).get("location", {}).get("lat"),
                longitude=place.get("geometry", {}).get("location", {}).get("lng"),
                rating=place.get("rating"),
                total_reviews=place.get("user_ratings_total", 0),
            )
 
            # Open/closed status
            is_open = place.get("opening_hours", {}).get("open_now", None)
            if is_open is True:
                status = "Open"
            elif is_open is False:
                status = "Closed"
            else:
                status = "Unknown"
 
            comp_rating  = float(comp_db.rating or 0)
            comp_reviews = int(comp_db.total_reviews or 0)
 
            # Light ABSA on competitor reviews
            try:
                comp_details  = gmaps.place(
                    place_id=place["place_id"],
                    fields=["reviews"],
                )
                comp_reviews_data = comp_details.get("result", {}).get("reviews", [])
                comp_texts = [r["text"] for r in comp_reviews_data if r.get("text")]
                comp_absa  = analyze_multiple_reviews(comp_texts) if comp_texts else {}
            except Exception:
                comp_absa = {}
 
            comp_scores = compute_aspect_scores_1_5(comp_absa)
            competitor_aspect_scores[place.get("name", f"competitor_{rank}")] = comp_scores
 
            # Store competitor record
            comp_record = crud.create_competitor_analysis(
                db=db,
                main_business_id=main_db.id,
                competitor_place_id=place["place_id"],
                competitor_name=comp_db.name,
                competitor_rating=comp_rating,
                competitor_reviews=comp_reviews,
                competitor_address=comp_db.address or "",
                rank=rank,
                rating_difference=round(your_rating - comp_rating, 2),
                review_difference=your_reviews - comp_reviews,
                search_radius=request.radius,
                search_category=request.category,
            )
            crud.update_competitor_insights(
                db=db,
                competitor_id=comp_record.id,
                aspect_scores=comp_scores,
                absa_summary=comp_absa,
            )
 
            competitors_out.append({
                "name":         comp_db.name,
                "rating":       comp_rating,
                "reviews":      comp_reviews,
                "price_level":  place.get("price_level"),
                "price_match":  (
                    True if main_price_level is None or place.get("price_level") is None
                    else abs(int(place.get("price_level")) - int(main_price_level)) <= 1
                ),
                "status":       status,
                "category":     request.category,
                "position":     "Unknown",
                "address":      comp_db.address,
                "aspect_scores": comp_scores,
            })
 
        # ── Your ABSA scores ───────────────────────────────────────
        main_analysis = (
            crud.get_latest_analysis(db, main_db.id, "absa_full") or
            crud.get_latest_analysis(db, main_db.id, "absa_with_insights") or
            crud.get_latest_analysis(db, main_db.id, "absa")
        )
        if main_analysis and main_analysis.aspect_results:
            # aspect_results may be nested by source, e.g. {google_maps: {...}, twitter: {...}}
            ar = main_analysis.aspect_results
            if "combined" in ar and isinstance(ar["combined"], dict):
                your_scores = compute_aspect_scores_1_5(ar["combined"])
            elif "google_maps" in ar:
                combined_absa: Dict[str, Any] = {}
                for src_data in ar.values():
                    if isinstance(src_data, dict):
                        for asp, data in src_data.items():
                            if asp not in combined_absa:
                                combined_absa[asp] = data
                your_scores = compute_aspect_scores_1_5(combined_absa)
            else:
                your_scores = compute_aspect_scores_1_5(ar)
        else:
            your_scores = {}
 
        # ── Aspect showdown ────────────────────────────────────────
        all_aspects = set(target_aspects)
        all_aspects.update(your_scores.keys())
        for scores in competitor_aspect_scores.values():
            all_aspects.update(scores.keys())
 
        aspect_showdown = []
        for asp in sorted(all_aspects):
            comp_vals = [
                s[asp] for s in competitor_aspect_scores.values() if asp in s
            ]
            aspect_showdown.append({
                "aspect":           asp,
                "your_score":       your_scores.get(asp),
                "competitor_avg":   round(sum(comp_vals) / len(comp_vals), 2) if comp_vals else None,
                "scale":            "1-5",
            })
 
        # ── Market position metrics ────────────────────────────────
        if competitors_out:
            avg_comp_rating  = round(
                sum(c["rating"] for c in competitors_out) / len(competitors_out), 2
            )
            avg_comp_reviews = round(
                sum(c["reviews"] for c in competitors_out) / len(competitors_out)
            )
        else:
            avg_comp_rating  = 0.0
            avg_comp_reviews = 0

        # Composite market position: quality (rating) + scale (review count)
        all_review_counts = [your_reviews] + [int(c["reviews"]) for c in competitors_out]
        max_log_reviews = max([math.log1p(max(0, r)) for r in all_review_counts], default=1.0)

        your_market_score = _composite_market_score(your_rating, your_reviews, max_log_reviews)
        comp_scores = [
            _composite_market_score(float(c["rating"]), int(c["reviews"]), max_log_reviews)
            for c in competitors_out
        ]
        avg_comp_market_score = round(sum(comp_scores) / len(comp_scores), 4) if comp_scores else 0.0
        best_comp_market_score = max(comp_scores) if comp_scores else 0.0

        if your_market_score >= (best_comp_market_score - 0.02):
            market_position = "Leader"
        elif your_market_score >= (avg_comp_market_score - 0.01):
            market_position = "Challenger"
        else:
            market_position = "Follower"

        # Assign per-competitor relative position consistently using the same scoring model
        for c in competitors_out:
            c_score = _composite_market_score(float(c["rating"]), int(c["reviews"]), max_log_reviews)
            if c_score >= (your_market_score + 0.02):
                c["position"] = "Leader"
            elif c_score >= (your_market_score - 0.01):
                c["position"] = "Challenger"
            else:
                c["position"] = "Follower"
 
        # rating_vs_reviews_chart — scatter data
        rating_vs_reviews_chart = [
            {"name": main_db.name + " (You)", "rating": your_rating, "reviews": your_reviews}
        ] + [
            {"name": c["name"], "rating": c["rating"], "reviews": c["reviews"]}
            for c in competitors_out
        ]
 
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        crud.log_analysis(
            db=db, business_name=request.business_name,
            category=request.category, location=request.city,
            endpoint="/analyze/competitors", status="success",
            execution_time_ms=execution_time,
        )
 
        return {
            "status": "success",
            "main_business": {
                "name":          main_db.name,
                "rating":        your_rating,
                "total_reviews": your_reviews,
                "address":       main_db.address,
            },
            "market_position": {
                "position":             market_position,
                "your_rating":          your_rating,
                "avg_competitor_rating": avg_comp_rating,
                "avg_competitor_reviews": avg_comp_reviews,
                "rating_vs_avg":        round(your_rating - avg_comp_rating, 2),
                "your_market_score":    round(your_market_score, 4),
                "avg_competitor_market_score": round(avg_comp_market_score, 4),
                "main_price_level":     main_price_level,
            },
            "competitors":              competitors_out,
            "rating_vs_reviews_chart":  rating_vs_reviews_chart,
            "aspect_showdown":          aspect_showdown,
            "total_competitors_found":  len(raw_competitors),
            "execution_time_ms":        execution_time,
        }
 
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Competitors endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ───────────────────────────────────────────────────────────────────
# 5.  ENDPOINT  /market-intelligence  (POST — Market Intelligence page)
#     Single endpoint for forecast + industry trend/news intelligence.
# ───────────────────────────────────────────────────────────────────
 
@app.post("/market-intelligence")
async def get_market_intelligence(
    request: MarketIntelligenceRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Market Intelligence page — XGBoost rating forecast + industry trend/news.
 
    Returns:
    - forecast: current_rating, predicted_rating, expected_change, trend, confidence
    - forecast_data: monthly [{month, forecast, actual}]
    - market_intelligence_news: industry-level trends, top sources, articles (with links)
    """
    start_time = datetime.now()

    biz = crud.get_business_by_name(db, request.business_name, request.city)
    effective_category = (request.category or (biz.category if biz else None) or "restaurant").strip()
 
    # ── Derive sentiment_score from stored ABSA if not provided ───
    sentiment_score = request.sentiment_score
    if sentiment_score is None:
        try:
            if biz:
                analysis = (
                    crud.get_latest_analysis(db, biz.id, "absa_full") or
                    crud.get_latest_analysis(db, biz.id, "absa_with_insights") or
                    crud.get_latest_analysis(db, biz.id, "absa")
                )
                if analysis and analysis.aspect_results:
                    ar = analysis.aspect_results
                    # Flatten nested or flat structure
                    flat: Dict[str, Any] = {}
                    for v in ar.values():
                        if isinstance(v, dict):
                            for asp, data in v.items():
                                if isinstance(data, dict) and "average_confidence" in data:
                                    flat[asp] = data
                                elif isinstance(data, dict) and "overall_sentiment" in data:
                                    flat[asp] = data
                    if flat:
                        pos_count = sum(
                            1 for d in flat.values()
                            if isinstance(d, dict) and d.get("overall_sentiment") == "Positive"
                        )
                        sentiment_score = round(pos_count / len(flat), 3)
        except Exception as e:
            logger.warning(f"Could not derive sentiment score: {e}")
 
        if sentiment_score is None:
            sentiment_score = 0.6   # neutral fallback
 
    # ── XGBoost Forecast ──────────────────────────────────────────
    try:
        predictions = generate_rating_forecast(
            city=request.city,
            category=request.category,
            current_rating=request.current_rating,
            sentiment_score=sentiment_score,
            months_ahead=request.months_ahead,
        )
        forecast_summary = get_forecast_summary(predictions)
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        predictions      = []
        forecast_summary = {}
 
    # ── Industry News / Trend signals ─────────────────────────────
    news_location = request.location or "India"
    category_lc = effective_category.lower()
    category_news_term = f"{effective_category} news"
    category_trend_term = f"{effective_category} food trends"
    if "bar" in category_lc:
        category_trend_term = f"{effective_category} beverage trends"
    elif "cafe" in category_lc or "coffee" in category_lc:
        category_trend_term = f"{effective_category} coffee trends"

    industry_queries = [
        category_news_term,
        category_trend_term,
        f"{effective_category} consumer trends India",
        f"{effective_category} market outlook India",
        "restaurant industry news India",
        "commercial LPG price hike restaurants India",
        "LPG crisis restaurant industry India",
        "food inflation restaurant industry India",
        "food service supply chain disruption India",
    ]

    query_results: Dict[str, List[Dict[str, Any]]] = {}
    try:
        query_results = scrape_multiple_queries(
            query_terms=industry_queries,
            location=news_location,
            max_results_per_query=8,
            exact_match=False,
            include_location=False,
        )
    except Exception as e:
        logger.error(f"Industry news scrape error: {e}")
        query_results = {}

    # Flatten and de-duplicate by link
    seen_links = set()
    articles: List[Dict[str, Any]] = []
    for query_term, query_articles in query_results.items():
        for a in query_articles:
            link = a.get("link")
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            articles.append({
                "headline": a.get("headline", ""),
                "link": link,
                "source_name": a.get("source_name", "Unknown"),
                "query": query_term,
            })

    # Keep response size manageable while preserving source diversity
    articles = articles[:40]

    # Top sources (by frequency)
    source_counts: Dict[str, int] = {}
    for a in articles:
        src = a.get("source_name") or "Unknown"
        source_counts[src] = source_counts.get(src, 0) + 1
    top_sources = [
        {"source": k, "count": v}
        for k, v in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
 
    media_visibility = (
        "High" if len(articles) >= 10
        else "Medium" if len(articles) >= 4
        else "Low"
    )

    # Simple keyword trend extraction from headlines
    stop_words = {
        "the", "and", "for", "with", "from", "this", "that", "into", "over", "after",
        "will", "are", "has", "have", "its", "their", "about", "your", "new", "latest",
        "restaurant", "industry", "market", "trends",
    }
    keyword_counts: Dict[str, int] = {}
    for a in articles:
        for token in (a.get("headline", "").lower().replace("-", " ").split()):
            token = "".join(ch for ch in token if ch.isalnum())
            if len(token) < 4 or token in stop_words:
                continue
            keyword_counts[token] = keyword_counts.get(token, 0) + 1

    trend_topics = [
        {"topic": k, "count": v}
        for k, v in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    ]
 
    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
 
    return {
        "status": "success",
        "forecast": {
            "current_rating":   request.current_rating,
            "predicted_rating": forecast_summary.get("predicted_rating"),
            "expected_change":  forecast_summary.get("rating_change"),
            "expected_change_pct": forecast_summary.get("percentage_change"),
            "trend":            forecast_summary.get("trend"),
            "confidence":       forecast_summary.get("confidence"),
            "sentiment_score_used": sentiment_score,
        },
        "forecast_data":    predictions,
        "market_intelligence_news": {
            "scope": "industry",
            "location": news_location,
            "queries_used": industry_queries,
            "total_articles":    len(articles),
            "media_visibility":  media_visibility,
            "top_sources":       top_sources,
            "trend_topics":      trend_topics,
            "articles": [
                {
                    "headline":    a["headline"],
                    "link":        a["link"],
                    "source_name": a.get("source_name", "Unknown"),
                    "query":       a.get("query"),
                }
                for a in articles
            ],
        },
        "execution_time_ms": execution_time,
    }


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )