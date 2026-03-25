"""
FastAPI application for Aspect-Based Sentiment Analysis (ABSA)
Integrates with Google Maps API to fetch business reviews
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uvicorn
import logging
import os
from dotenv import load_dotenv
import googlemaps
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from analyzer import (
    analyze_review_for_aspects,
    analyze_multiple_reviews,
    download_nltk_data,
    set_aspect_keywords_for_category,
    get_available_categories
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
    """Request model for market intelligence / web scraping"""
    business_name: str = Field(..., description="Name of your business")
    location: Optional[str] = Field("Mumbai", description="Location to filter news (default: Mumbai)")
    include_competitors: Optional[bool] = Field(False, description="Also scrape competitor mentions")
    competitor_names: Optional[List[str]] = Field(None, description="List of competitor names to track")


class ForecastRequest(BaseModel):
    """Request model for star rating forecast"""
    business_name: str = Field(..., description="Name of the business")
    city: str = Field(..., description="City name (e.g., 'Mumbai', 'San Francisco')")
    category: str = Field(..., description="Business category (e.g., 'Vegan Street Food', 'Restaurant')")
    current_rating: float = Field(..., ge=1.0, le=5.0, description="Current average rating (1.0-5.0)")
    sentiment_score: float = Field(..., ge=0.0, le=1.0, description="Sentiment score from ABSA (0.0-1.0)")
    months_ahead: Optional[int] = Field(6, ge=1, le=12, description="Number of months to forecast (default: 6)")


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
            "/analyze/competitors": "POST - Find and analyze top 4 competitors in your area",
            "/market-intelligence": "POST - Scrape Google News for business mentions and media tracking",
            "/market-intelligence/{business_name}": "GET - Retrieve stored market intelligence data",
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
            "Market Intelligence - Google News Scraping",
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
    import nltk
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

# LLM Insights endpoint - Analyze business and generate strategic insights
@app.post("/analyze/business/insights")
async def analyze_business_with_insights(
    request: BusinessRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Fetch reviews from Google Maps, perform ABSA, and generate strategic insights using Gemini LLM
    
    This endpoint combines:
    1. Google Maps review fetching
    2. Review ingestion into ChromaDB (for RAG)
    3. Aspect-based sentiment analysis
    4. LLM-powered (RAG) strategic recommendations
    5. Database storage of all results
    
    Args:
        request: BusinessRequest containing business name, category, and location
        db: Database session (injected)
        
    Returns:
        Dictionary with ABSA results and strategic insights
    """
    start_time = datetime.now()
    
    if not gmaps:
        raise HTTPException(
            status_code=503,
            detail="Google Maps API is not configured. Please set GOOGLE_MAPS_API_KEY in .env file"
        )
    
    try:
        # Set aspect keywords based on business category
        set_aspect_keywords_for_category(request.category)
        
        # First, get the ABSA analysis (reuse existing logic)
        # Construct search query
        query = f"{request.business_name}"
        if request.category:
            query += f" {request.category}"
        query += f" {request.location}"
        
        logger.info(f"Searching for business: {query}")
        
        # Search for the business
        places_result = gmaps.places(query=query)
        
        if not places_result.get('results'):
            raise HTTPException(
                status_code=404,
                detail=f"No business found matching: {query}"
            )
        
        # Get the first (most relevant) result
        place = places_result['results'][0]
        place_id = place['place_id']
        place_name = place['name']
        place_address = place.get('formatted_address', 'N/A')
        
        logger.info(f"Found business: {place_name} (ID: {place_id})")
        
        # Get detailed place information including reviews
        place_details = gmaps.place(place_id=place_id, fields=['name', 'rating', 'user_ratings_total', 'reviews'])
        
        if 'result' not in place_details:
            raise HTTPException(
                status_code=404,
                detail="Unable to fetch business details"
            )
        
        result = place_details['result']
        reviews_data = result.get('reviews', [])
        
        if not reviews_data:
            return {
                "status": "success",
                "business_info": {
                    "name": place_name,
                    "address": place_address,
                    "rating": result.get('rating', 'N/A'),
                    "total_ratings": result.get('user_ratings_total', 0)
                },
                "message": "No reviews found for this business",
                "analysis": {},
                "insights": None
            }
        
        logger.info(f"Found {len(reviews_data)} reviews for {place_name}")
        
        # Extract review texts
        review_texts = [review['text'] for review in reviews_data if review.get('text')]
        
        if not review_texts:
            return {
                "status": "success",
                "business_info": {
                    "name": place_name,
                    "address": place_address,
                    "rating": result.get('rating', 'N/A'),
                    "total_ratings": result.get('user_ratings_total', 0)
                },
                "message": "No review texts available for analysis",
                "analysis": {},
                "insights": None
            }
        
        # ### --- NEW RAG STEP: INGEST REVIEWS --- ###
        # Ingest (embed and store) these reviews into ChromaDB
        # This function is fast and uses 'upsert' to avoid duplicates.
        logger.info(f"Ingesting/updating {len(review_texts)} reviews for {place_name} in vector store...")
        ingest_reviews_to_chroma(
            business_name=place_name,
            review_texts=review_texts
        )
        # ### --- END OF NEW STEP --- ###
        
        # Analyze all reviews
        logger.info(f"Analyzing {len(review_texts)} reviews...")
        analysis_results = analyze_multiple_reviews(review_texts)
        
        # Prepare business info
        business_info = {
            "name": place_name,
            "address": place_address,
            "rating": result.get('rating', 'N/A'),
            "total_ratings": result.get('user_ratings_total', 0),
            "reviews_analyzed": len(review_texts)
        }
        
        # ### --- MODIFIED INSIGHTS CALL --- ###
        # Generate strategic insights using Gemini LLM (now with RAG)
        logger.info(f"Generating strategic insights using Gemini LLM with RAG...")
        
        # We no longer pass 'raw_reviews'. The function will
        # automatically retrieve the best context from ChromaDB.
        insights = generate_business_insights(
            business_name=place_name,
            business_info=business_info,
            absa_results=analysis_results
        )
        # ### --- END OF MODIFIED CALL --- ###
        
        # ### --- DATABASE STORAGE --- ###
        logger.info("Storing results in database...")
        try:
            # 1. Create or get business record
            business_db = crud.get_or_create_business(
                db=db,
                place_id=place_id,
                name=place_name,
                category=request.category,
                address=place_address,
                location=request.location,
                latitude=place.get('geometry', {}).get('location', {}).get('lat'),
                longitude=place.get('geometry', {}).get('location', {}).get('lng'),
                rating=result.get('rating'),
                total_reviews=result.get('user_ratings_total', 0)
            )
            
            # 2. Store all reviews
            review_db_ids = []
            for review_data in reviews_data:
                if review_data.get('text'):
                    review_db = crud.create_review(
                        db=db,
                        business_id=business_db.id,
                        review_text=review_data['text'],
                        author_name=review_data.get('author_name'),
                        rating=review_data.get('rating'),
                        review_date=datetime.fromtimestamp(review_data.get('time', 0)) if review_data.get('time') else None,
                        source="google_maps"
                    )
                    review_db_ids.append(review_db.id)
            
            # 3. Store ABSA analysis results
            analysis_db = crud.create_analysis(
                db=db,
                business_id=business_db.id,
                analysis_type="absa_with_insights",
                total_reviews_analyzed=len(review_texts),
                aspect_results=analysis_results,
                overall_sentiment=analysis_results.get('overall_sentiment', {}).get('sentiment', 'neutral'),
                average_rating=result.get('rating')
            )
            
            # 4. Store review sentiments (aspect-level)
            for aspect, data in analysis_results.get('aspect_analysis', {}).items():
                sentiment_counts = data.get('sentiment_distribution', {})
                # Store dominant sentiment for this aspect
                dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else 'neutral'
                confidence = sentiment_counts.get(dominant_sentiment, 0) / sum(sentiment_counts.values()) if sum(sentiment_counts.values()) > 0 else 0
                
                # Create a sentiment record for each review that mentioned this aspect
                for review_id in review_db_ids[:len(data.get('mentions', []))]:  # Match reviews to mentions
                    crud.create_review_sentiment(
                        db=db,
                        review_id=review_id,
                        aspect=aspect,
                        sentiment=dominant_sentiment,
                        confidence_score=confidence,
                        sentence=None  # Could be extracted if needed
                    )
            
            # 5. Store LLM insights
            insights_db = crud.create_insight_report(
                db=db,
                business_id=business_db.id,
                executive_summary=insights.get('executive_summary'),
                marketing_recommendations=insights.get('marketing_recommendations', []),
                pr_recommendations=insights.get('pr_recommendations', []),
                operational_improvements=insights.get('operational_improvements', []),
                competitive_positioning=insights.get('competitive_positioning', []),
                priority_actions=insights.get('priority_actions', []),
                rag_enabled=True,
                reviews_retrieved=len(review_texts),
                full_insights_text=str(insights)
            )
            
            # 6. Log the analysis in history
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            crud.log_analysis(
                db=db,
                business_name=place_name,
                category=request.category,
                location=request.location,
                endpoint="/analyze/business/insights",
                status="success",
                execution_time_ms=execution_time
            )
            
            logger.info(f"✅ Results stored in database (Business ID: {business_db.id})")
            
        except Exception as db_error:
            logger.error(f"Database storage error (non-fatal): {db_error}")
            # Don't fail the request if DB storage fails
        # ### --- END DATABASE STORAGE --- ###
        
        return {
            "status": "success",
            "business_info": business_info,
            "analysis": analysis_results,
            "strategic_insights": insights,
            "quick_summary": generate_quick_summary(analysis_results)
        }
        
    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API error: {e}")
        # Log failed analysis
        try:
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            crud.log_analysis(
                db=db,
                business_name=request.business_name,
                category=request.category,
                location=request.location,
                endpoint="/analyze/business/insights",
                status="failed",
                error_message=f"Google Maps API error: {str(e)}",
                execution_time_ms=execution_time
            )
        except:
            pass
        raise HTTPException(status_code=502, detail=f"Google Maps API error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing business with insights: {e}")
        # Log failed analysis
        try:
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            crud.log_analysis(
                db=db,
                business_name=request.business_name,
                category=request.category,
                location=request.location,
                endpoint="/analyze/business/insights",
                status="failed",
                error_message=str(e),
                execution_time_ms=execution_time
            )
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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


# Competitor Analysis endpoint - Optimized with Database
@app.post("/analyze/competitors")
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Fetch and analyze top 4 competitors using stored business data
    
    This optimized endpoint:
    1. Retrieves main business data from DATABASE (no redundant API call)
    2. Searches for competitors nearby using Google Maps
    3. Stores competitor data in PostgreSQL
    4. Returns comprehensive competitive analysis
    
    Args:
        request: CompetitorAnalysisRequest with business name, category, and location
        db: Database session (injected)
        
    Returns:
        Dictionary with competitor comparison data stored in DB
    """
    start_time = datetime.now()
    
    if not gmaps:
        raise HTTPException(
            status_code=503,
            detail="Google Maps API is not configured. Please set GOOGLE_MAPS_API_KEY in .env file"
        )
    
    try:
        # Step 1: Get main business from DATABASE (optimized - no API call)
        logger.info(f"Retrieving main business from database: {request.business_name}")
        
        # Try to find business in database first
        main_business_db = crud.get_business_by_name(db, request.business_name, request.location)
        
        if not main_business_db:
            # If not in database, we need to fetch it once from Google Maps
            logger.info(f"Business not in database, fetching from Google Maps: {request.business_name}")
            main_query = f"{request.business_name}"
            if request.category:
                main_query += f" {request.category}"
            main_query += f" {request.location}"
            
            main_business_result = gmaps.places(query=main_query)
            
            if not main_business_result.get('results'):
                raise HTTPException(
                    status_code=404,
                    detail=f"Could not find your business: {request.business_name}"
                )
            
            # Get main business details
            main_business = main_business_result['results'][0]
            place_id = main_business['place_id']
            place_name = main_business['name']
            place_address = main_business.get('formatted_address', 'N/A')
            main_business_location = main_business.get('geometry', {}).get('location', {})
            
            # Get detailed info
            main_details = gmaps.place(
                place_id=place_id, 
                fields=['name', 'rating', 'user_ratings_total', 'formatted_address', 'place_id']
            )
            
            # Store in database for future use
            main_business_db = crud.get_or_create_business(
                db=db,
                place_id=place_id,
                name=place_name,
                category=request.category,
                address=place_address,
                location=request.location,
                latitude=main_business_location.get('lat'),
                longitude=main_business_location.get('lng'),
                rating=main_details['result'].get('rating'),
                total_reviews=main_details['result'].get('user_ratings_total', 0)
            )
            
            logger.info(f"✅ Main business stored in database (ID: {main_business_db.id})")
        
        # Prepare main business info from database
        main_info = {
            "name": main_business_db.name,
            "place_id": main_business_db.place_id,
            "rating": float(main_business_db.rating) if main_business_db.rating else 0,
            "total_reviews": main_business_db.total_reviews or 0,
            "address": main_business_db.address
        }
        
        logger.info(f"Main business loaded: {main_info['name']} (Rating: {main_info['rating']}, Reviews: {main_info['total_reviews']})")
        
        # Step 2: Search for competitors nearby (only competitor query, not main business)
        if not main_business_db.latitude or not main_business_db.longitude:
            raise HTTPException(
                status_code=500,
                detail="Business location coordinates not available in database"
            )
        
        lat = main_business_db.latitude
        lng = main_business_db.longitude
        
        logger.info(f"Searching for competitors near ({lat}, {lng}) within {request.radius}m")
        
        # Use nearby search to find similar businesses
        competitors_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=request.radius,
            type=request.category.lower() if request.category else None,
            keyword=request.category if request.category else None
        )
        
        if not competitors_result.get('results'):
            return {
                "status": "success",
                "main_business": main_info,
                "competitors": [],
                "message": "No competitors found in the specified area",
                "total_competitors_found": 0
            }
        
        # Step 3: Filter, rank, and STORE competitors
        competitors = []
        
        for place in competitors_result['results']:
            # Skip if it's the main business
            if place['place_id'] == main_business_db.place_id:
                logger.info(f"Skipping main business: {place['name']}")
                continue
            
            # Skip if no rating (likely closed or not enough data)
            if 'rating' not in place:
                continue
            
            competitor_location = place.get('geometry', {}).get('location', {})
            
            # Store competitor in database
            competitor_db = crud.get_or_create_business(
                db=db,
                place_id=place['place_id'],
                name=place.get('name', 'Unknown'),
                category=request.category,
                address=place.get('vicinity', 'N/A'),
                location=request.location,
                latitude=competitor_location.get('lat'),
                longitude=competitor_location.get('lng'),
                rating=place.get('rating'),
                total_reviews=place.get('user_ratings_total', 0)
            )
            
            competitor_data = {
                "name": competitor_db.name,
                "place_id": competitor_db.place_id,
                "rating": float(competitor_db.rating) if competitor_db.rating else 0,
                "total_reviews": competitor_db.total_reviews or 0,
                "address": competitor_db.address,
                "is_open": place.get('opening_hours', {}).get('open_now', None),
                "db_id": competitor_db.id
            }
            
            competitors.append(competitor_data)
        
        # Step 4: Sort by rating (primary) and review count (secondary)
        competitors_sorted = sorted(
            competitors,
            key=lambda x: (x['rating'], x['total_reviews']),
            reverse=True
        )
        
        # Step 5: Get top 4 competitors
        top_4_competitors = competitors_sorted[:4]
        
        logger.info(f"Found {len(competitors)} competitors, proceeding with ABSA for top 4 and storing results")

        # Helper to compute 1-5 aspect scores from sentiment breakdown
        def compute_aspect_scores(aspect_results: Dict[str, Any]) -> Dict[str, float]:
            scores: Dict[str, float] = {}
            for aspect, a in aspect_results.items():
                try:
                    pos = a.get('sentiment_breakdown', {}).get('Positive', 0)
                    neg = a.get('sentiment_breakdown', {}).get('Negative', 0)
                    neu = a.get('sentiment_breakdown', {}).get('Neutral', 0)
                    total = pos + neg + neu
                    if total == 0:
                        continue
                    # Weighted score: Positive=1, Neutral=0.5, Negative=0 -> scale to 1..5
                    frac = (pos + 0.5 * neu) / total
                    score_1_5 = round(1 + 4 * frac, 2)
                    scores[aspect] = score_1_5
                except Exception:
                    continue
            return scores

        # Step 6: Load ABSA for main business from DB (do NOT re-analyze)
        main_analysis = crud.get_latest_analysis(db, main_business_db.id, analysis_type="absa_with_insights") or \
                         crud.get_latest_analysis(db, main_business_db.id, analysis_type="absa")
        if not main_analysis or not main_analysis.aspect_results:
            raise HTTPException(
                status_code=404,
                detail="No stored ABSA found for the main business. Please run /analyze/business/insights first."
            )

        main_aspect_scores = compute_aspect_scores(main_analysis.aspect_results)

        # Step 7: For each competitor, fetch reviews -> run ABSA -> store -> compute aspect scores
        stored_competitors = []
        competitor_aspect_scores: Dict[str, Dict[str, float]] = {}
        your_rating = main_info['rating']
        your_reviews = main_info['total_reviews']
        
        for rank, competitor in enumerate(top_4_competitors, start=1):
            # Store competitor meta row in competitor_analyses table
            try:
                competitor_analysis_db = crud.create_competitor_analysis(
                    db=db,
                    main_business_id=main_business_db.id,
                    competitor_place_id=competitor['place_id'],
                    competitor_name=competitor['name'],
                    competitor_rating=competitor['rating'],
                    competitor_reviews=competitor['total_reviews'],
                    competitor_address=competitor['address'],
                    rank=rank,
                    rating_difference=round(your_rating - competitor['rating'], 2),
                    review_difference=your_reviews - competitor['total_reviews'],
                    search_radius=request.radius,
                    search_category=request.category
                )
                stored_competitors.append(competitor_analysis_db.id)
            except Exception as e:
                logger.warning(f"Failed to store competitor row (meta): {e}")

            # Fetch competitor reviews
            comp_details = gmaps.place(
                place_id=competitor['place_id'],
                fields=['name', 'rating', 'user_ratings_total', 'reviews']
            )
            comp_reviews_data = comp_details.get('result', {}).get('reviews', []) if comp_details else []
            comp_texts = [r['text'] for r in comp_reviews_data if r.get('text')]
            
            if not comp_texts:
                logger.info(f"No review texts available for competitor: {competitor['name']}")
                competitor_aspect_scores[competitor['name']] = {}
                continue
            
            # Run ABSA for competitor
            comp_analysis_results = analyze_multiple_reviews(comp_texts)
            
            # Store competitor ABSA in analyses table
            try:
                crud.create_analysis(
                    db=db,
                    business_id=crud.get_or_create_business(
                        db=db,
                        place_id=competitor['place_id'],
                        name=competitor['name'],
                        category=request.category,
                        address=competitor['address'],
                        location=request.location,
                        latitude=None,
                        longitude=None,
                        rating=competitor['rating'],
                        total_reviews=competitor['total_reviews']
                    ).id,
                    analysis_type="absa_competitor",
                    total_reviews_analyzed=len(comp_texts),
                    aspect_results=comp_analysis_results,
                    overall_sentiment=None,
                    average_rating=competitor['rating']
                )
            except Exception as e:
                logger.warning(f"Failed to store competitor ABSA: {e}")

            # Compute 1-5 aspect scores for this competitor
            competitor_aspect_scores[competitor['name']] = compute_aspect_scores(comp_analysis_results)

        # Step 8: Aggregate competitor average per aspect
        # Consider aspects present in either main or any competitor
        all_aspects = set(main_aspect_scores.keys())
        for scores in competitor_aspect_scores.values():
            all_aspects.update(scores.keys())
        
        aspect_showdown = []
        for aspect in sorted(all_aspects):
            your_score = main_aspect_scores.get(aspect)
            # Average across competitors with that aspect
            vals = [scores.get(aspect) for scores in competitor_aspect_scores.values() if scores.get(aspect) is not None]
            comp_avg = round(sum(vals) / len(vals), 2) if vals else None
            # Only include if at least one side has a score
            if your_score is not None or comp_avg is not None:
                aspect_showdown.append({
                    "aspect": aspect,
                    "your_score": your_score,
                    "competitor_avg": comp_avg,
                    "scale": "1-5"
                })

        # Step 9: Calculate overall competitive metrics (ratings based)
        if top_4_competitors:
            avg_competitor_rating = sum(c['rating'] for c in top_4_competitors) / len(top_4_competitors)
            avg_competitor_reviews = sum(c['total_reviews'] for c in top_4_competitors) / len(top_4_competitors)
            rating_comparison = "above" if your_rating > avg_competitor_rating else "below" if your_rating < avg_competitor_rating else "equal to"
            review_comparison = "more" if your_reviews > avg_competitor_reviews else "fewer" if your_reviews < avg_competitor_reviews else "same as"
            competitive_analysis = {
                "average_competitor_rating": round(avg_competitor_rating, 2),
                "average_competitor_reviews": round(avg_competitor_reviews, 0),
                "your_rating_vs_average": rating_comparison,
                "your_reviews_vs_average": review_comparison,
                "rating_difference": round(your_rating - avg_competitor_rating, 2),
                "review_difference": your_reviews - avg_competitor_reviews,
                "market_position": "Leader" if your_rating > avg_competitor_rating else "Challenger" if your_rating >= avg_competitor_rating * 0.9 else "Follower"
            }
        else:
            competitive_analysis = None
        
        # Log execution
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        crud.log_analysis(
            db=db,
            business_name=request.business_name,
            category=request.category,
            location=request.location,
            endpoint="/analyze/competitors",
            status="success",
            execution_time_ms=execution_time
        )
        
        return {
            "status": "success",
            "main_business": main_info,
            "competitors": top_4_competitors,
            "total_competitors_found": len(competitors),
            "competitors_stored_in_db": len(stored_competitors),
            "competitive_analysis": competitive_analysis,
            "aspect_showdown": {
                "aspects": aspect_showdown,
                "methodology": "Scores per aspect computed from sentiment breakdown (Positive=1, Neutral=0.5, Negative=0) scaled to 1-5"
            },
            "competitor_aspect_scores": competitor_aspect_scores,
            "search_parameters": {
                "category": request.category,
                "location": request.location,
                "radius_meters": request.radius,
                "radius_miles": round(request.radius * 0.000621371, 2)
            },
            "data_source": "database_optimized",
            "execution_time_ms": execution_time
        }
        
    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API error: {e}")
        raise HTTPException(status_code=502, detail=f"Google Maps API error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Market Intelligence endpoint - Web Scraping
@app.post("/market-intelligence")
async def get_market_intelligence(
    request: MarketIntelligenceRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Scrape Google News for business mentions and news articles
    
    This endpoint:
    1. Searches Google News for your business name
    2. Optionally searches for competitor mentions
    3. Stores all results in the database
    4. Returns aggregated news intelligence
    
    Use this for:
    - Media monitoring
    - Brand reputation tracking
    - Competitive intelligence
    - PR impact analysis
    
    Args:
        request: MarketIntelligenceRequest with business name and optional competitors
        db: Database session (injected)
        
    Returns:
        Dictionary with news articles and market insights
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting market intelligence scan for: {request.business_name}")
        
        # Prepare list of queries
        queries = [request.business_name]
        if request.include_competitors and request.competitor_names:
            queries.extend(request.competitor_names)
        
        # Scrape Google News for all queries
        all_results = {}
        total_articles = 0
        
        for query in queries:
            logger.info(f"Scraping news for: {query}")
            articles = scrape_google_news(
                query_term=query,
                location=request.location,
                max_results=10
            )
            
            all_results[query] = articles
            total_articles += len(articles)
            
            logger.info(f"Found {len(articles)} articles for {query}")
        
        # Store results in database
        stored_count = 0
        
        for query, articles in all_results.items():
            # Get or create business record (or use a generic placeholder)
            # For competitor tracking, we might not have Google Maps data
            business = crud.get_business_by_place_id(db, f"news_only_{query.lower().replace(' ', '_')}")
            
            if not business:
                # Create a placeholder business record for news tracking
                business = crud.create_business(
                    db=db,
                    place_id=f"news_only_{query.lower().replace(' ', '_')}",
                    name=query,
                    category="news_tracking",
                    location=request.location
                )
            
            # Store each article
            for article in articles:
                try:
                    crud.create_web_scraping_result(
                        db=db,
                        business_id=business.id,
                        query_term=query,
                        headline=article['headline'],
                        link=article['link'],
                        source_name=article['source_name']
                    )
                    stored_count += 1
                except Exception as e:
                    logger.warning(f"Error storing article: {e}")
                    continue
        
        # Generate summary insights
        main_business_articles = all_results.get(request.business_name, [])
        
        # Count articles by source
        source_distribution = {}
        for articles in all_results.values():
            for article in articles:
                source = article['source_name']
                source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Log in history
        crud.log_analysis(
            db=db,
            business_name=request.business_name,
            category="news_tracking",
            location=request.location,
            endpoint="/market-intelligence",
            status="success",
            execution_time_ms=execution_time
        )
        
        logger.info(f"✅ Market intelligence scan complete: {total_articles} articles found, {stored_count} stored")
        
        return {
            "status": "success",
            "business_name": request.business_name,
            "location": request.location,
            "total_articles_found": total_articles,
            "articles_stored_in_db": stored_count,
            "queries_searched": queries,
            "results": {
                query: {
                    "article_count": len(articles),
                    "articles": articles
                }
                for query, articles in all_results.items()
            },
            "insights": {
                "main_business_mentions": len(main_business_articles),
                "competitor_mentions": total_articles - len(main_business_articles) if request.include_competitors else 0,
                "top_sources": dict(sorted(source_distribution.items(), key=lambda x: x[1], reverse=True)[:5]),
                "media_visibility": "High" if len(main_business_articles) >= 5 else "Medium" if len(main_business_articles) >= 2 else "Low"
            },
            "execution_time_ms": execution_time,
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in market intelligence scan: {e}")
        
        # Log failed attempt
        try:
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            crud.log_analysis(
                db=db,
                business_name=request.business_name,
                category="news_tracking",
                location=request.location or "Unknown",
                endpoint="/market-intelligence",
                status="failed",
                error_message=str(e),
                execution_time_ms=execution_time
            )
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Get stored market intelligence
@app.get("/market-intelligence/{business_name}")
async def get_stored_market_intelligence(
    business_name: str,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve stored market intelligence for a business
    
    Args:
        business_name: Name of the business
        limit: Maximum number of articles to return
        db: Database session (injected)
        
    Returns:
        Stored news articles and mentions
    """
    try:
        # Get scraping results by query term
        results = crud.get_scraping_results_by_query(db, business_name, limit=limit)
        
        if not results:
            return {
                "status": "success",
                "business_name": business_name,
                "total_articles": 0,
                "articles": [],
                "message": "No market intelligence data found. Run POST /market-intelligence first."
            }
        
        # Group by source
        by_source = {}
        for result in results:
            source = result.source_name or "Unknown"
            if source not in by_source:
                by_source[source] = []
            by_source[source].append({
                "headline": result.headline,
                "link": result.link,
                "scraped_at": result.scraped_at.isoformat() if result.scraped_at else None
            })
        
        return {
            "status": "success",
            "business_name": business_name,
            "total_articles": len(results),
            "articles": [
                {
                    "id": result.id,
                    "headline": result.headline,
                    "link": result.link,
                    "source_name": result.source_name,
                    "scraped_at": result.scraped_at.isoformat() if result.scraped_at else None
                }
                for result in results
            ],
            "by_source": by_source,
            "most_recent": results[0].scraped_at.isoformat() if results else None
        }
        
    except Exception as e:
        logger.error(f"Error retrieving market intelligence: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Star Rating Forecast endpoint
@app.post("/forecast")
async def get_rating_forecast(request: ForecastRequest) -> Dict[str, Any]:
    """
    Generate star rating forecast using XGBoost model
    
    This endpoint:
    1. Takes business info (city, category, rating, sentiment)
    2. Uses trained XGBoost model to predict future ratings
    3. Returns monthly forecast data for visualization
    
    Args:
        request: ForecastRequest with business details and sentiment
        
    Returns:
        Dictionary with forecast data and summary statistics
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating forecast for {request.business_name} in {request.city}")
        
        # Generate forecast using XGBoost model
        predictions = generate_rating_forecast(
            city=request.city,
            category=request.category,
            current_rating=request.current_rating,
            sentiment_score=request.sentiment_score,
            months_ahead=request.months_ahead
        )
        
        # Get summary statistics
        summary = get_forecast_summary(predictions)
        
        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"✅ Forecast generated: {summary['trend']} trend, {summary['rating_change']:+.2f} change")
        
        return {
            "status": "success",
            "business_name": request.business_name,
            "city": request.city,
            "category": request.category,
            "forecast_data": predictions,
            "summary": summary,
            "model": "XGBoost",
            "input_parameters": {
                "current_rating": request.current_rating,
                "sentiment_score": request.sentiment_score,
                "months_ahead": request.months_ahead
            },
            "execution_time_ms": execution_time,
            "generated_at": datetime.now().isoformat()
        }
        
    except FileNotFoundError:
        logger.error("Model file not found")
        raise HTTPException(
            status_code=503,
            detail="Forecasting model not found. Please ensure star_forecasting_model.pkl exists in models/ directory"
        )
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )