"""
Database Models — Full Schema (v2)
Covers: existing tables (minimally changed) + all new tables for
social sources, Framework Reports, ORM, Confidence metadata.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON,
    ForeignKey, Boolean, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class SentimentEnum(str, enum.Enum):
    positive = "Positive"
    negative = "Negative"
    neutral  = "Neutral"

class SourceEnum(str, enum.Enum):
    google_maps = "google_maps"
    twitter     = "twitter"
    news        = "news"

class FrameworkEnum(str, enum.Enum):
    swot     = "swot"
    pestel   = "pestel"
    four_ps  = "four_ps"
    bcg      = "bcg"
    vrio     = "vrio"
    ansoff   = "ansoff"
    mece     = "mece"
    six_sigma = "six_sigma"


# ─────────────────────────────────────────────
# EXISTING TABLE — Business  (extended)
# Added: social profile metadata
# ─────────────────────────────────────────────

class Business(Base):
    __tablename__ = "businesses"

    id             = Column(Integer, primary_key=True, index=True)
    place_id       = Column(String(255), unique=True, index=True, nullable=False)
    name           = Column(String(255), nullable=False)
    category       = Column(String(100), index=True)
    address        = Column(Text)
    location       = Column(String(255))   # city
    area           = Column(String(255))   # e.g. "Colaba"  ← NEW
    latitude       = Column(Float)
    longitude      = Column(Float)
    rating         = Column(Float)
    total_reviews  = Column(Integer, default=0)

    # ── Social source metadata ───────────────── NEW
    # Compatibility mapping: these attributes map to legacy DB columns.
    social_profile_url     = Column("zomato_url", Text)
    social_rating          = Column("zomato_rating", Float)
    social_reviews_count   = Column("zomato_reviews_count", Integer, default=0)
    photo_count    = Column(Integer, default=0)        # virality proxy
    price_range    = Column(String(50))                # e.g. "₹700 for two"
    cuisine_tags   = Column(JSON)                      # ["Continental","Mughlai"]

    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

    # ── Relationships ────────────────────────────────────────────────
    reviews            = relationship("Review",             back_populates="business", cascade="all, delete-orphan")
    analyses           = relationship("Analysis",           back_populates="business", cascade="all, delete-orphan")
    competitor_records = relationship("CompetitorAnalysis", back_populates="main_business", cascade="all, delete-orphan")
    social_reviews     = relationship("SocialReview",       back_populates="business", cascade="all, delete-orphan")
    social_menu_items  = relationship("SocialMenuItem",     back_populates="business", cascade="all, delete-orphan")
    framework_reports  = relationship("FrameworkReport",    back_populates="business", cascade="all, delete-orphan")  # NEW
    orm_reviews        = relationship("ORMReview",          back_populates="business", cascade="all, delete-orphan")  # NEW
    framework_citations = relationship("FrameworkCitation", back_populates="business", cascade="all, delete-orphan")
    web_scraping_results = relationship("WebScrapingResult", back_populates="business", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# EXISTING TABLE — Review  (unchanged)
# Google Maps reviews only
# ─────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"

    id           = Column(Integer, primary_key=True, index=True)
    business_id  = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    review_text  = Column(Text, nullable=False)
    author_name  = Column(String(255))
    rating       = Column(Float)
    review_date  = Column(DateTime(timezone=True))
    source       = Column(String(50), default="google_maps")
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    business   = relationship("Business",        back_populates="reviews")
    sentiments = relationship("ReviewSentiment", back_populates="review", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# EXISTING TABLE — ReviewSentiment  (unchanged)
# ─────────────────────────────────────────────

class ReviewSentiment(Base):
    __tablename__ = "review_sentiments"

    id               = Column(Integer, primary_key=True, index=True)
    review_id        = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    aspect           = Column(String(100), nullable=False)
    sentiment        = Column(String(50),  nullable=False)
    confidence_score = Column(Float)
    sentence         = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    review = relationship("Review", back_populates="sentiments")


# ─────────────────────────────────────────────
# EXISTING TABLE — Analysis  (extended)
# Added: date_from, date_to, sources_used
# ─────────────────────────────────────────────

class Analysis(Base):
    __tablename__ = "analyses"

    id                     = Column(Integer, primary_key=True, index=True)
    business_id            = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    analysis_type          = Column(String(50), default="absa")
    total_reviews_analyzed = Column(Integer, default=0)
    aspect_results         = Column(JSON)
    overall_sentiment      = Column(String(50))
    average_rating         = Column(Float)

    # ── Date range context ───────────────────── NEW
    date_from   = Column(DateTime(timezone=True))   # user-supplied range start
    date_to     = Column(DateTime(timezone=True))   # user-supplied range end
    months_back = Column(Integer)                   # e.g. 6 (alternative to explicit dates)

    # ── Source breakdown ─────────────────────── NEW
    # e.g. {"google_maps": 12, "twitter": 18}
    sources_used = Column(JSON)

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="analyses")


# ─────────────────────────────────────────────
# EXISTING TABLE — CompetitorAnalysis  (extended)
# Added: social source rating metadata and competitor_aspect_scores
# ─────────────────────────────────────────────

class CompetitorAnalysis(Base):
    __tablename__ = "competitor_analyses"

    id                  = Column(Integer, primary_key=True, index=True)
    main_business_id    = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    competitor_place_id = Column(String(255), nullable=False)
    competitor_name     = Column(String(255), nullable=False)
    competitor_rating   = Column(Float)
    competitor_reviews  = Column(Integer)
    competitor_address  = Column(Text)
    rank                = Column(Integer)
    rating_difference   = Column(Float)
    review_difference   = Column(Integer)
    search_radius       = Column(Integer)
    search_category     = Column(String(100))

    # ── Social source data for competitor ────── NEW
    # Compatibility mapping: map to legacy competitor columns in existing DB.
    competitor_social_url          = Column("competitor_zomato_url", Text)
    competitor_social_rating       = Column("competitor_zomato_rating", Float)
    competitor_social_reviews      = Column("competitor_zomato_reviews", Integer)
    # Aspect-level ABSA scores: {"Food": 3.8, "Service": 4.1, ...}
    competitor_aspect_scores       = Column(JSON)
    # Full lightweight ABSA result
    competitor_absa_summary        = Column(JSON)

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    main_business = relationship("Business", back_populates="competitor_records")


# ─────────────────────────────────────────────
# NEW TABLE — SocialReview
# Individual reviews scraped from social platforms
# ─────────────────────────────────────────────

class SocialReview(Base):
    __tablename__ = "zomato_reviews"

    id           = Column(Integer, primary_key=True, index=True)
    business_id  = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)

    review_text  = Column(Text, nullable=False)
    author_name  = Column(String(255))
    rating       = Column(Float)                        # reviewer's star rating

    # Date handling: store both raw string and resolved absolute date
    raw_date     = Column(String(100))                  # "2 months ago", "Jan 2024", etc.
    review_date  = Column(DateTime(timezone=True))      # resolved absolute date
    date_is_estimated = Column(Boolean, default=False)  # True if resolved from relative

    dining_type  = Column(String(50))                   # "Dining" | "Delivery" | "combined"
    scraped_at   = Column(DateTime(timezone=True), server_default=func.now())

    # ABSA results stored inline for this review
    # {"Food": {"sentiment": "Positive", "score": 0.91, "sentence": "..."}, ...}
    absa_results = Column(JSON)

    business = relationship("Business", back_populates="social_reviews")


# ─────────────────────────────────────────────
# NEW TABLE — SocialMenuItem
# Menu items persisted for strategy frameworks (social + OCR uploads)
# ─────────────────────────────────────────────

class SocialMenuItem(Base):
    __tablename__ = "menu_items"

    id          = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)

    name        = Column(String(255), nullable=False)
    price       = Column(Float)
    category    = Column(String(255))    # e.g. "Starters", "Mains"
    description = Column(Text)
    is_veg      = Column(Boolean)

    # Populated from scraped sources and/or OCR menu-image extraction
    mention_count      = Column(Integer, default=0)   # how many reviews mention this item
    positive_mentions  = Column(Integer, default=0)
    negative_mentions  = Column(Integer, default=0)
    # BCG classification assigned by Gemini
    bcg_category       = Column(String(50))           # "Star"|"Cash Cow"|"Dog"|"Question Mark"

    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="social_menu_items")



# ─────────────────────────────────────────────
# NEW TABLE — AggregatedABSA
# Cross-source ABSA summary with confidence scores
# One row per (business, analysis_run, aspect)
# ─────────────────────────────────────────────

class AggregatedABSA(Base):
    """
    Stores the per-aspect aggregated sentiment AFTER combining
    Google Maps + Twitter signals.

    confidence_score is the dynamic compound score (0-100).
    source_breakdown shows per-source contribution.
    conflict_flag is True when sources disagree significantly.
    """
    __tablename__ = "aggregated_absa"

    id          = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id",   ondelete="CASCADE"), nullable=True)

    aspect              = Column(String(100), nullable=False)  # "Food", "Service", ...
    overall_sentiment   = Column(String(50))                   # dominant across all sources
    confidence_score    = Column(Float)                        # 0-100 compound score

    # Per-source breakdown
    # {
    #   "google_maps": {"sentiment": "Positive", "score": 0.88, "mention_count": 12},
    #   "twitter":     {"sentiment": "Positive", "score": 0.82, "mention_count": 18},
    # }
    source_breakdown = Column(JSON)

    conflict_flag    = Column(Boolean, default=False)
    conflict_detail  = Column(Text)    # e.g. "Google Maps: Positive vs Twitter: Negative"

    # Pre-clustered complaint buckets for MECE (list of {cluster, sentences, count})
    mece_clusters    = Column(JSON)

    # Variance metric for Six Sigma
    sentiment_variance = Column(Float)

    computed_at = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────────
# NEW TABLE — FrameworkReport
# One row per framework per analysis run
# ─────────────────────────────────────────────

class FrameworkReport(Base):
    """
    Stores Gemini's output for each of the 8 frameworks.
    All 8 are generated in a single Gemini call and then split
    into 8 rows here for easy individual retrieval by the frontend.

    result_json structure varies per framework but always contains:
    {
      "points": [
        {
          "label": "...",
          "description": "...",
          "confidence": 82,          // 0-100
              "sources": ["google_maps", "twitter"],
          "conflict": false
        },
        ...
      ]
    }
    """
    __tablename__ = "framework_reports"

    id           = Column(Integer, primary_key=True, index=True)
    business_id  = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    analysis_id  = Column(Integer, ForeignKey("analyses.id",   ondelete="SET NULL"), nullable=True)

    framework    = Column(SAEnum(FrameworkEnum), nullable=False)   # "swot", "bcg", etc.
    result_json  = Column(JSON, nullable=False)                    # structured output (see docstring)

    # Which sources fed into this framework run
    sources_used = Column(JSON)    # ["google_maps", "twitter"]

    # Overall confidence for this framework (average of all point confidences)
    avg_confidence = Column(Float)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="framework_reports")
    citations = relationship("FrameworkCitation", back_populates="framework_report", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# NEW TABLE — FrameworkCitation
# Stores evidence references for each SWOT point
# ─────────────────────────────────────────────

class FrameworkCitation(Base):
    __tablename__ = "framework_citations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    framework_report_id = Column(Integer, ForeignKey("framework_reports.id", ondelete="CASCADE"), nullable=False)

    framework = Column(String(50), nullable=False, default="swot")
    quadrant = Column(String(50), nullable=False)     # strengths|weaknesses|opportunities|threats
    point_id = Column(String(100), nullable=False)    # swot_strength_1, etc.
    point_label = Column(String(255), nullable=False)

    confidence_pct = Column(Float)
    suggestion = Column(Text)
    derived_insight = Column(Text)

    source_type = Column(String(50), nullable=False)  # google_maps|twitter|news
    source_strength = Column(String(20))              # Low|Medium|High
    source_quote = Column(Text, nullable=False)
    source_reference = Column(String(255))            # review id / source name / handle
    source_url = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="framework_citations")
    framework_report = relationship("FrameworkReport", back_populates="citations")


# ─────────────────────────────────────────────
# NEW TABLE — ORMReview
# Negative reviews surfaced for owner action
# ─────────────────────────────────────────────

class ORMReview(Base):
    """
    Surfaces negative (or conflicted) reviews from any source
    so the owner can manually respond via the original link.
    """
    __tablename__ = "orm_reviews"

    id          = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)

    source       = Column(SAEnum(SourceEnum), nullable=False)  # where this review came from
    review_text  = Column(Text, nullable=False)
    author_name  = Column(String(255))
    rating       = Column(Float)
    review_date  = Column(DateTime(timezone=True))

    aspect       = Column(String(100))    # primary negative aspect
    sentiment    = Column(String(50))
    confidence   = Column(Float)          # how confident we are this is genuinely negative

    source_url   = Column(Text)           # direct link to review (if available)
    is_responded = Column(Boolean, default=False)   # owner marks as handled

    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="orm_reviews")


# ─────────────────────────────────────────────
# EXISTING TABLE — InsightReport  (extended)
# Added: framework_run_id, date_from, date_to
# ─────────────────────────────────────────────

class InsightReport(Base):
    __tablename__ = "insight_reports"

    id          = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)

    executive_summary        = Column(Text)
    marketing_recommendations = Column(JSON)
    pr_recommendations       = Column(JSON)
    operational_improvements = Column(JSON)
    competitive_positioning  = Column(JSON)
    priority_actions         = Column(JSON)
    full_insights_text       = Column(Text)

    rag_enabled      = Column(Boolean, default=False)
    reviews_retrieved = Column(Integer, default=0)

    # ── NEW: link to the framework reports generated in the same run
    # Stored as list of FrameworkReport IDs
    framework_report_ids = Column(JSON)

    # ── NEW: date range this report covers
    date_from   = Column(DateTime(timezone=True))
    date_to     = Column(DateTime(timezone=True))
    months_back = Column(Integer)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────────
# EXISTING TABLE — AnalysisHistory  (unchanged)
# ─────────────────────────────────────────────

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id               = Column(Integer, primary_key=True, index=True)
    business_name    = Column(String(255), nullable=False)
    category         = Column(String(100))
    location         = Column(String(255))
    endpoint         = Column(String(100))
    status           = Column(String(50))
    error_message    = Column(Text)
    execution_time_ms = Column(Integer)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────────
# EXISTING TABLE — WebScrapingResult  (unchanged)
# Google News articles
# ─────────────────────────────────────────────

class WebScrapingResult(Base):
    __tablename__ = "web_scraping_results"

    id          = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    query_term  = Column(String(255), nullable=False, index=True)
    headline    = Column(Text, nullable=False)
    link        = Column(Text, nullable=False, unique=True)
    source_name = Column(String(255))

    # ── NEW: resolved article date (parsed from article metadata if possible)
    article_date = Column(DateTime(timezone=True))

    scraped_at  = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="web_scraping_results")