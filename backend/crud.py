"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import db_models as models


# ============ BUSINESS CRUD ============

def create_business(
    db: Session,
    place_id: str,
    name: str,
    category: str = None,
    address: str = None,
    location: str = None,
    latitude: float = None,
    longitude: float = None,
    rating: float = None,
    total_reviews: int = 0
) -> models.Business:
    """Create a new business record"""
    business = models.Business(
        place_id=place_id,
        name=name,
        category=category,
        address=address,
        location=location,
        latitude=latitude,
        longitude=longitude,
        rating=rating,
        total_reviews=total_reviews
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def get_business_by_place_id(db: Session, place_id: str) -> Optional[models.Business]:
    """Get business by Google Maps place_id"""
    return db.query(models.Business).filter(models.Business.place_id == place_id).first()


def get_business_by_name(db: Session, name: str, location: str) -> Optional[models.Business]:
    """Get business by name and location (case-insensitive)"""
    return db.query(models.Business).filter(
        models.Business.name.ilike(f"%{name}%"),
        models.Business.location.ilike(f"%{location}%")
    ).first()


def get_or_create_business(db: Session, place_id: str, **kwargs) -> models.Business:
    """Get existing business or create new one"""
    business = get_business_by_place_id(db, place_id)
    if not business:
        business = create_business(db, place_id, **kwargs)
    return business


def update_business(db: Session, business_id: int, **kwargs) -> models.Business:
    """Update business information"""
    business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if business:
        for key, value in kwargs.items():
            if hasattr(business, key):
                setattr(business, key, value)
        db.commit()
        db.refresh(business)
    return business


def get_all_businesses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Business]:
    """Get all businesses with pagination"""
    return db.query(models.Business).offset(skip).limit(limit).all()


# ============ REVIEW CRUD ============

def create_review(
    db: Session,
    business_id: int,
    review_text: str,
    author_name: str = None,
    rating: float = None,
    review_date: datetime = None,
    source: str = "google_maps"
) -> models.Review:
    """Create a new review"""
    review = models.Review(
        business_id=business_id,
        review_text=review_text,
        author_name=author_name,
        rating=rating,
        review_date=review_date,
        source=source
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews_by_business(db: Session, business_id: int) -> List[models.Review]:
    """Get all reviews for a business"""
    return db.query(models.Review).filter(models.Review.business_id == business_id).all()


# ============ REVIEW SENTIMENT CRUD ============

def create_review_sentiment(
    db: Session,
    review_id: int,
    aspect: str,
    sentiment: str,
    confidence_score: float,
    sentence: str = None
) -> models.ReviewSentiment:
    """Create a sentiment record for a review"""
    sentiment_record = models.ReviewSentiment(
        review_id=review_id,
        aspect=aspect,
        sentiment=sentiment,
        confidence_score=confidence_score,
        sentence=sentence
    )
    db.add(sentiment_record)
    db.commit()
    db.refresh(sentiment_record)
    return sentiment_record


def get_sentiments_by_review(db: Session, review_id: int) -> List[models.ReviewSentiment]:
    """Get all sentiments for a review"""
    return db.query(models.ReviewSentiment).filter(
        models.ReviewSentiment.review_id == review_id
    ).all()


# ============ ANALYSIS CRUD ============

def create_analysis(
    db: Session,
    business_id: int,
    analysis_type: str,
    total_reviews_analyzed: int,
    aspect_results: Dict[str, Any],
    overall_sentiment: str = None,
    average_rating: float = None
) -> models.Analysis:
    """Create an analysis record"""
    analysis = models.Analysis(
        business_id=business_id,
        analysis_type=analysis_type,
        total_reviews_analyzed=total_reviews_analyzed,
        aspect_results=aspect_results,
        overall_sentiment=overall_sentiment,
        average_rating=average_rating
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_latest_analysis(db: Session, business_id: int, analysis_type: str = "absa") -> Optional[models.Analysis]:
    """Get the most recent analysis for a business"""
    return db.query(models.Analysis).filter(
        models.Analysis.business_id == business_id,
        models.Analysis.analysis_type == analysis_type
    ).order_by(desc(models.Analysis.analyzed_at)).first()


def get_all_analyses(db: Session, business_id: int) -> List[models.Analysis]:
    """Get all analyses for a business"""
    return db.query(models.Analysis).filter(
        models.Analysis.business_id == business_id
    ).order_by(desc(models.Analysis.analyzed_at)).all()


# ============ COMPETITOR ANALYSIS CRUD ============

def create_competitor_analysis(
    db: Session,
    main_business_id: int,
    competitor_place_id: str,
    competitor_name: str,
    competitor_rating: float,
    competitor_reviews: int,
    competitor_address: str,
    rank: int,
    rating_difference: float,
    review_difference: int,
    search_radius: int,
    search_category: str
) -> models.CompetitorAnalysis:
    """Create a competitor analysis record"""
    competitor = models.CompetitorAnalysis(
        main_business_id=main_business_id,
        competitor_place_id=competitor_place_id,
        competitor_name=competitor_name,
        competitor_rating=competitor_rating,
        competitor_reviews=competitor_reviews,
        competitor_address=competitor_address,
        rank=rank,
        rating_difference=rating_difference,
        review_difference=review_difference,
        search_radius=search_radius,
        search_category=search_category
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


def get_latest_competitors(db: Session, business_id: int) -> List[models.CompetitorAnalysis]:
    """Get the most recent competitor analysis"""
    # Get the latest analysis timestamp
    latest_analysis = db.query(func.max(models.CompetitorAnalysis.analyzed_at)).filter(
        models.CompetitorAnalysis.main_business_id == business_id
    ).scalar()
    
    if not latest_analysis:
        return []
    
    return db.query(models.CompetitorAnalysis).filter(
        models.CompetitorAnalysis.main_business_id == business_id,
        models.CompetitorAnalysis.analyzed_at == latest_analysis
    ).order_by(models.CompetitorAnalysis.rank).all()


# ============ INSIGHT REPORT CRUD ============

def create_insight_report(
    db: Session,
    business_id: int,
    executive_summary: str = None,
    marketing_recommendations: Dict = None,
    pr_recommendations: Dict = None,
    operational_improvements: Dict = None,
    competitive_positioning: Dict = None,
    priority_actions: Dict = None,
    full_insights_text: str = None,
    rag_enabled: bool = False,
    reviews_retrieved: int = 0
) -> models.InsightReport:
    """Create an insight report"""
    report = models.InsightReport(
        business_id=business_id,
        executive_summary=executive_summary,
        marketing_recommendations=marketing_recommendations,
        pr_recommendations=pr_recommendations,
        operational_improvements=operational_improvements,
        competitive_positioning=competitive_positioning,
        priority_actions=priority_actions,
        full_insights_text=full_insights_text,
        rag_enabled=rag_enabled,
        reviews_retrieved=reviews_retrieved
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_latest_insight_report(db: Session, business_id: int) -> Optional[models.InsightReport]:
    """Get the most recent insight report"""
    return db.query(models.InsightReport).filter(
        models.InsightReport.business_id == business_id
    ).order_by(desc(models.InsightReport.generated_at)).first()


# ============ ANALYSIS HISTORY CRUD ============

def log_analysis(
    db: Session,
    business_name: str,
    category: str,
    location: str,
    endpoint: str,
    status: str,
    error_message: str = None,
    execution_time_ms: int = None
) -> models.AnalysisHistory:
    """Log an analysis request to history"""
    history = models.AnalysisHistory(
        business_name=business_name,
        category=category,
        location=location,
        endpoint=endpoint,
        status=status,
        error_message=error_message,
        execution_time_ms=execution_time_ms
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_analysis_history(db: Session, limit: int = 50) -> List[models.AnalysisHistory]:
    """Get recent analysis history"""
    return db.query(models.AnalysisHistory).order_by(
        desc(models.AnalysisHistory.created_at)
    ).limit(limit).all()


def get_business_statistics(db: Session) -> Dict[str, Any]:
    """Get overall database statistics"""
    total_businesses = db.query(func.count(models.Business.id)).scalar()
    total_reviews = db.query(func.count(models.Review.id)).scalar()
    total_analyses = db.query(func.count(models.Analysis.id)).scalar()
    total_insights = db.query(func.count(models.InsightReport.id)).scalar()
    
    return {
        "total_businesses": total_businesses,
        "total_reviews": total_reviews,
        "total_analyses": total_analyses,
        "total_insight_reports": total_insights,
    }


# ============ WEB SCRAPING CRUD ============

def create_web_scraping_result(
    db: Session,
    business_id: int,
    query_term: str,
    headline: str,
    link: str,
    source_name: str = None
) -> models.WebScrapingResult:
    """Create a new web scraping result (article)"""
    # Check if link already exists to avoid duplicates
    existing = db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.link == link
    ).first()
    
    if existing:
        return existing  # Return existing record instead of creating duplicate
    
    result = models.WebScrapingResult(
        business_id=business_id,
        query_term=query_term,
        headline=headline,
        link=link,
        source_name=source_name
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_scraping_results_by_business(
    db: Session,
    business_id: int,
    limit: int = 50
) -> List[models.WebScrapingResult]:
    """Get all web scraping results for a business"""
    return db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.business_id == business_id
    ).order_by(desc(models.WebScrapingResult.scraped_at)).limit(limit).all()


def get_scraping_results_by_query(
    db: Session,
    query_term: str,
    limit: int = 50
) -> List[models.WebScrapingResult]:
    """Get all web scraping results for a specific query term"""
    return db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.query_term == query_term
    ).order_by(desc(models.WebScrapingResult.scraped_at)).limit(limit).all()


def get_latest_scraping_results(
    db: Session,
    limit: int = 100
) -> List[models.WebScrapingResult]:
    """Get most recent web scraping results across all businesses"""
    return db.query(models.WebScrapingResult).order_by(
        desc(models.WebScrapingResult.scraped_at)
    ).limit(limit).all()


def delete_old_scraping_results(db: Session, days: int = 30) -> int:
    """Delete web scraping results older than specified days"""
    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    
    deleted = db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.scraped_at < cutoff_date
    ).delete()
    
    db.commit()
    return deleted
