"""
CRUD operations — merged v1 + v2
Covers all original tables (Business, Review, ReviewSentiment, Analysis,
CompetitorAnalysis, InsightReport, AnalysisHistory, WebScrapingResult)
plus all new v2 tables (SocialReview, SocialMenuItem,
AggregatedABSA, FrameworkReport, ORMReview).
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import db_models as models


# ─────────────────────────────────────────────────────────────────────
# BUSINESS
# ─────────────────────────────────────────────────────────────────────

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
    total_reviews: int = 0,
) -> models.Business:
    business = models.Business(
        place_id=place_id,
        name=name,
        category=category,
        address=address,
        location=location,
        latitude=latitude,
        longitude=longitude,
        rating=rating,
        total_reviews=total_reviews,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def get_business_by_place_id(db: Session, place_id: str) -> Optional[models.Business]:
    return db.query(models.Business).filter(models.Business.place_id == place_id).first()


def get_business_by_name(db: Session, name: str, location: str) -> Optional[models.Business]:
    return db.query(models.Business).filter(
        models.Business.name.ilike(f"%{name}%"),
        models.Business.location.ilike(f"%{location}%"),
    ).first()


def get_or_create_business(db: Session, place_id: str, **kwargs) -> models.Business:
    business = get_business_by_place_id(db, place_id)
    if not business:
        business = create_business(db, place_id, **kwargs)
    return business


def update_business(db: Session, business_id: int, **kwargs) -> Optional[models.Business]:
    business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if business:
        for key, value in kwargs.items():
            if hasattr(business, key):
                setattr(business, key, value)
        db.commit()
        db.refresh(business)
    return business


def upsert_business_social_info(
    db: Session,
    place_id: str,
    social_profile_url: str = None,
    social_rating: float = None,
    social_reviews_count: int = None,
    photo_count: int = None,
    price_range: str = None,
    cuisine_tags: list = None,
    area: str = None,
) -> Optional[models.Business]:
    """Update social-source fields on an existing Business record."""
    business = get_business_by_place_id(db, place_id)
    if not business:
        return None
    if social_profile_url is not None:
        business.social_profile_url = social_profile_url
    if social_rating is not None:
        business.social_rating = social_rating
    if social_reviews_count is not None:
        business.social_reviews_count = social_reviews_count
    if photo_count is not None:
        business.photo_count = photo_count
    if price_range is not None:
        business.price_range = price_range
    if cuisine_tags is not None:
        business.cuisine_tags = cuisine_tags
    if area is not None:
        business.area = area
    db.commit()
    db.refresh(business)
    return business


def get_all_businesses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Business]:
    return db.query(models.Business).offset(skip).limit(limit).all()


# ─────────────────────────────────────────────────────────────────────
# GOOGLE MAPS REVIEWS
# ─────────────────────────────────────────────────────────────────────

def create_review(
    db: Session,
    business_id: int,
    review_text: str,
    author_name: str = None,
    rating: float = None,
    review_date: datetime = None,
    source: str = "google_maps",
) -> models.Review:
    review = models.Review(
        business_id=business_id,
        review_text=review_text,
        author_name=author_name,
        rating=rating,
        review_date=review_date,
        source=source,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews_by_business(db: Session, business_id: int) -> List[models.Review]:
    return db.query(models.Review).filter(models.Review.business_id == business_id).all()


# ─────────────────────────────────────────────────────────────────────
# REVIEW SENTIMENT
# ─────────────────────────────────────────────────────────────────────

def create_review_sentiment(
    db: Session,
    review_id: int,
    aspect: str,
    sentiment: str,
    confidence_score: float,
    sentence: str = None,
) -> models.ReviewSentiment:
    record = models.ReviewSentiment(
        review_id=review_id,
        aspect=aspect,
        sentiment=sentiment,
        confidence_score=confidence_score,
        sentence=sentence,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_sentiments_by_review(db: Session, review_id: int) -> List[models.ReviewSentiment]:
    return db.query(models.ReviewSentiment).filter(
        models.ReviewSentiment.review_id == review_id
    ).all()


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────────────────────────────

def create_analysis(
    db: Session,
    business_id: int,
    analysis_type: str,
    total_reviews_analyzed: int,
    aspect_results: Dict[str, Any],
    overall_sentiment: str = None,
    average_rating: float = None,
    # v2 extensions — optional so existing callers don't break
    date_from: datetime = None,
    date_to: datetime = None,
    months_back: int = None,
    sources_used: Dict[str, int] = None,
) -> models.Analysis:
    analysis = models.Analysis(
        business_id=business_id,
        analysis_type=analysis_type,
        total_reviews_analyzed=total_reviews_analyzed,
        aspect_results=aspect_results,
        overall_sentiment=overall_sentiment,
        average_rating=average_rating,
        date_from=date_from,
        date_to=date_to,
        months_back=months_back,
        sources_used=sources_used,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_latest_analysis(
    db: Session, business_id: int, analysis_type: str = "absa"
) -> Optional[models.Analysis]:
    return db.query(models.Analysis).filter(
        models.Analysis.business_id == business_id,
        models.Analysis.analysis_type == analysis_type,
    ).order_by(desc(models.Analysis.analyzed_at)).first()


def get_all_analyses(db: Session, business_id: int) -> List[models.Analysis]:
    return db.query(models.Analysis).filter(
        models.Analysis.business_id == business_id
    ).order_by(desc(models.Analysis.analyzed_at)).all()


# ─────────────────────────────────────────────────────────────────────
# COMPETITOR ANALYSIS
# ─────────────────────────────────────────────────────────────────────

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
    search_category: str,
) -> models.CompetitorAnalysis:
    record = models.CompetitorAnalysis(
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
        search_category=search_category,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_competitors(db: Session, business_id: int) -> List[models.CompetitorAnalysis]:
    latest_ts = db.query(func.max(models.CompetitorAnalysis.analyzed_at)).filter(
        models.CompetitorAnalysis.main_business_id == business_id
    ).scalar()
    if not latest_ts:
        return []
    return db.query(models.CompetitorAnalysis).filter(
        models.CompetitorAnalysis.main_business_id == business_id,
        models.CompetitorAnalysis.analyzed_at == latest_ts,
    ).order_by(models.CompetitorAnalysis.rank).all()


def update_competitor_insights(
    db: Session,
    competitor_id: int,
    social_url: str = None,
    social_rating: float = None,
    social_reviews: int = None,
    aspect_scores: dict = None,
    absa_summary: dict = None,
) -> Optional[models.CompetitorAnalysis]:
    row = db.query(models.CompetitorAnalysis).filter(
        models.CompetitorAnalysis.id == competitor_id
    ).first()
    if not row:
        return None
    if social_url is not None:
        row.competitor_social_url = social_url
    if social_rating is not None:
        row.competitor_social_rating = social_rating
    if social_reviews is not None:
        row.competitor_social_reviews = social_reviews
    if aspect_scores is not None:
        row.competitor_aspect_scores = aspect_scores
    if absa_summary is not None:
        row.competitor_absa_summary = absa_summary
    db.commit()
    db.refresh(row)
    return row


# ─────────────────────────────────────────────────────────────────────
# INSIGHT REPORT
# ─────────────────────────────────────────────────────────────────────

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
    reviews_retrieved: int = 0,
    # v2 extensions
    framework_report_ids: list = None,
    date_from: datetime = None,
    date_to: datetime = None,
    months_back: int = None,
) -> models.InsightReport:
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
        reviews_retrieved=reviews_retrieved,
        framework_report_ids=framework_report_ids,
        date_from=date_from,
        date_to=date_to,
        months_back=months_back,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_latest_insight_report(db: Session, business_id: int) -> Optional[models.InsightReport]:
    return db.query(models.InsightReport).filter(
        models.InsightReport.business_id == business_id
    ).order_by(desc(models.InsightReport.generated_at)).first()


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS HISTORY
# ─────────────────────────────────────────────────────────────────────

def log_analysis(
    db: Session,
    business_name: str,
    category: str,
    location: str,
    endpoint: str,
    status: str,
    error_message: str = None,
    execution_time_ms: int = None,
) -> models.AnalysisHistory:
    history = models.AnalysisHistory(
        business_name=business_name,
        category=category,
        location=location,
        endpoint=endpoint,
        status=status,
        error_message=error_message,
        execution_time_ms=execution_time_ms,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_analysis_history(db: Session, limit: int = 50) -> List[models.AnalysisHistory]:
    return db.query(models.AnalysisHistory).order_by(
        desc(models.AnalysisHistory.created_at)
    ).limit(limit).all()


def get_business_statistics(db: Session) -> Dict[str, Any]:
    return {
        "total_businesses":     db.query(func.count(models.Business.id)).scalar(),
        "total_reviews":        db.query(func.count(models.Review.id)).scalar(),
        "total_analyses":       db.query(func.count(models.Analysis.id)).scalar(),
        "total_insight_reports": db.query(func.count(models.InsightReport.id)).scalar(),
    }


# ─────────────────────────────────────────────────────────────────────
# WEB SCRAPING (Google News)
# ─────────────────────────────────────────────────────────────────────

def create_web_scraping_result(
    db: Session,
    business_id: int,
    query_term: str,
    headline: str,
    link: str,
    source_name: str = None,
    article_date: datetime = None,
) -> models.WebScrapingResult:
    existing = db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.link == link
    ).first()
    if existing:
        return existing
    result = models.WebScrapingResult(
        business_id=business_id,
        query_term=query_term,
        headline=headline,
        link=link,
        source_name=source_name,
        article_date=article_date,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_scraping_results_by_business(
    db: Session, business_id: int, limit: int = 50
) -> List[models.WebScrapingResult]:
    return db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.business_id == business_id
    ).order_by(desc(models.WebScrapingResult.scraped_at)).limit(limit).all()


def get_scraping_results_by_query(
    db: Session, query_term: str, limit: int = 50
) -> List[models.WebScrapingResult]:
    return db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.query_term == query_term
    ).order_by(desc(models.WebScrapingResult.scraped_at)).limit(limit).all()


def get_latest_scraping_results(db: Session, limit: int = 100) -> List[models.WebScrapingResult]:
    return db.query(models.WebScrapingResult).order_by(
        desc(models.WebScrapingResult.scraped_at)
    ).limit(limit).all()


def delete_old_scraping_results(db: Session, days: int = 30) -> int:
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    deleted = db.query(models.WebScrapingResult).filter(
        models.WebScrapingResult.scraped_at < cutoff
    ).delete()
    db.commit()
    return deleted


# ─────────────────────────────────────────────────────────────────────
# SOCIAL REVIEWS
# ─────────────────────────────────────────────────────────────────────

def create_social_review(
    db: Session,
    business_id: int,
    review_text: str,
    author_name: str = None,
    rating: float = None,
    raw_date: str = None,
    review_date: datetime = None,
    date_is_estimated: bool = False,
    dining_type: str = "combined",
    absa_results: dict = None,
) -> models.SocialReview:
    review = models.SocialReview(
        business_id=business_id,
        review_text=review_text,
        author_name=author_name,
        rating=rating,
        raw_date=raw_date,
        review_date=review_date,
        date_is_estimated=date_is_estimated,
        dining_type=dining_type,
        absa_results=absa_results,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def bulk_create_social_reviews(
    db: Session, business_id: int, reviews: List[Dict[str, Any]]
) -> int:
    """Insert many social reviews. Returns count inserted."""
    count = 0
    for r in reviews:
        try:
            create_social_review(
                db=db,
                business_id=business_id,
                review_text=r.get("review_text", ""),
                author_name=r.get("author_name"),
                rating=r.get("rating"),
                raw_date=r.get("raw_date"),
                review_date=r.get("review_date"),
                date_is_estimated=r.get("date_is_estimated", False),
                dining_type=r.get("dining_type", "combined"),
                absa_results=r.get("absa_results"),
            )
            count += 1
        except Exception:
            db.rollback()
    return count


def get_social_reviews(
    db: Session, business_id: int, limit: int = 500
) -> List[models.SocialReview]:
    return (
        db.query(models.SocialReview)
        .filter(models.SocialReview.business_id == business_id)
        .order_by(desc(models.SocialReview.review_date))
        .limit(limit)
        .all()
    )


def delete_social_reviews(db: Session, business_id: int) -> int:
    deleted = (
        db.query(models.SocialReview)
        .filter(models.SocialReview.business_id == business_id)
        .delete()
    )
    db.commit()
    return deleted


# ─────────────────────────────────────────────────────────────────────
# SOCIAL MENU ITEMS
# ─────────────────────────────────────────────────────────────────────

def upsert_menu_items(
    db: Session, business_id: int, items: List[Dict[str, Any]]
) -> int:
    """Delete existing menu items and insert fresh ones. Returns count."""
    db.query(models.SocialMenuItem).filter(
        models.SocialMenuItem.business_id == business_id
    ).delete()
    db.commit()

    count = 0
    for item in items:
        mi = models.SocialMenuItem(
            business_id=business_id,
            name=item.get("name", ""),
            price=item.get("price"),
            category=item.get("category"),
            description=item.get("description"),
            is_veg=item.get("is_veg"),
            mention_count=item.get("mention_count", 0),
            positive_mentions=item.get("positive_mentions", 0),
            negative_mentions=item.get("negative_mentions", 0),
            bcg_category=item.get("bcg_category"),
        )
        db.add(mi)
        count += 1
    db.commit()
    return count


def get_menu_items(db: Session, business_id: int) -> List[models.SocialMenuItem]:
    return (
        db.query(models.SocialMenuItem)
        .filter(models.SocialMenuItem.business_id == business_id)
        .all()
    )



# ─────────────────────────────────────────────────────────────────────
# AGGREGATED ABSA
# ─────────────────────────────────────────────────────────────────────

def save_aggregated_absa(
    db: Session,
    business_id: int,
    analysis_id: int,
    aspect_confidence_list: List[Dict[str, Any]],
    mece_clusters: List[Dict[str, Any]],
    sentiment_variances: Dict[str, float],
) -> List[models.AggregatedABSA]:
    """
    Save one AggregatedABSA row per aspect.
    Clears existing rows for this business first.
    mece_clusters is stored only on the first aspect row to avoid duplication.
    """
    db.query(models.AggregatedABSA).filter(
        models.AggregatedABSA.business_id == business_id
    ).delete()
    db.commit()

    rows = []
    for idx, item in enumerate(aspect_confidence_list):
        aspect = item["aspect"]
        row = models.AggregatedABSA(
            business_id=business_id,
            analysis_id=analysis_id,
            aspect=aspect,
            overall_sentiment=item.get("overall_sentiment"),
            confidence_score=item.get("confidence_score"),
            source_breakdown=item.get("source_breakdown"),
            conflict_flag=item.get("conflict_flag", False),
            conflict_detail=item.get("conflict_detail"),
            # Store MECE clusters only on first row to avoid bloat
            mece_clusters=mece_clusters if idx == 0 else None,
            sentiment_variance=sentiment_variances.get(aspect, 0.0),
        )
        db.add(row)
        rows.append(row)

    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


def get_aggregated_absa(
    db: Session, business_id: int
) -> List[models.AggregatedABSA]:
    return (
        db.query(models.AggregatedABSA)
        .filter(models.AggregatedABSA.business_id == business_id)
        .order_by(desc(models.AggregatedABSA.confidence_score))
        .all()
    )


def get_mece_clusters(db: Session, business_id: int) -> Optional[List[Dict[str, Any]]]:
    """Retrieve MECE clusters stored on the first AggregatedABSA row."""
    row = (
        db.query(models.AggregatedABSA)
        .filter(
            models.AggregatedABSA.business_id == business_id,
            models.AggregatedABSA.mece_clusters.isnot(None),
        )
        .first()
    )
    return row.mece_clusters if row else None


# ─────────────────────────────────────────────────────────────────────
# FRAMEWORK REPORTS
# ─────────────────────────────────────────────────────────────────────

def save_framework_reports(
    db: Session,
    business_id: int,
    analysis_id: int,
    frameworks: Dict[str, Any],
    avg_confidence_per_framework: Dict[str, float],
    sources_used: List[str],
) -> List[models.FrameworkReport]:
    """
    Save one FrameworkReport row per framework (8 rows total).
    Clears previous rows for this business first.
    """
    db.query(models.FrameworkReport).filter(
        models.FrameworkReport.business_id == business_id
    ).delete()
    db.commit()

    rows = []
    for fw_name, fw_data in frameworks.items():
        row = models.FrameworkReport(
            business_id=business_id,
            analysis_id=analysis_id,
            framework=fw_name,
            result_json=fw_data,
            sources_used=sources_used,
            avg_confidence=avg_confidence_per_framework.get(fw_name),
        )
        db.add(row)
        rows.append(row)

    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


def get_framework_report(
    db: Session, business_id: int, framework: str
) -> Optional[models.FrameworkReport]:
    return (
        db.query(models.FrameworkReport)
        .filter(
            models.FrameworkReport.business_id == business_id,
            models.FrameworkReport.framework == framework,
        )
        .order_by(desc(models.FrameworkReport.generated_at))
        .first()
    )


def get_all_framework_reports(
    db: Session, business_id: int
) -> List[models.FrameworkReport]:
    return (
        db.query(models.FrameworkReport)
        .filter(models.FrameworkReport.business_id == business_id)
        .order_by(models.FrameworkReport.framework)
        .all()
    )


# ─────────────────────────────────────────────────────────────────────
# ORM REVIEWS
# ─────────────────────────────────────────────────────────────────────

def save_orm_reviews(
    db: Session, business_id: int, reviews: List[Dict[str, Any]]
) -> int:
    """
    Save negative/conflict reviews for ORM display.
    Clears previous ORM entries for this business first.
    """
    db.query(models.ORMReview).filter(
        models.ORMReview.business_id == business_id
    ).delete()
    db.commit()

    count = 0
    for r in reviews:
        row = models.ORMReview(
            business_id=business_id,
            source=r.get("source", "google_maps"),
            review_text=r.get("review_text", ""),
            author_name=r.get("author_name"),
            rating=r.get("rating"),
            review_date=r.get("review_date"),
            aspect=r.get("aspect"),
            sentiment=r.get("sentiment", "Negative"),
            confidence=r.get("confidence"),
            source_url=r.get("source_url"),
            is_responded=False,
        )
        db.add(row)
        count += 1
    db.commit()
    return count


def get_orm_reviews(
    db: Session,
    business_id: int,
    only_unresponded: bool = True,
    limit: int = 100,
) -> List[models.ORMReview]:
    q = db.query(models.ORMReview).filter(
        models.ORMReview.business_id == business_id
    )
    if only_unresponded:
        q = q.filter(models.ORMReview.is_responded == False)  # noqa: E712
    return q.order_by(desc(models.ORMReview.confidence)).limit(limit).all()


def mark_orm_review_responded(
    db: Session, orm_review_id: int
) -> Optional[models.ORMReview]:
    row = db.query(models.ORMReview).filter(
        models.ORMReview.id == orm_review_id
    ).first()
    if row:
        row.is_responded = True
        db.commit()
        db.refresh(row)
    return row