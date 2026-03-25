"""
Database Models for ABSA Application
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Business(Base):
    """
    Business entity - stores business information
    """
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), index=True)
    address = Column(Text)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    total_reviews = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="business", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="business", cascade="all, delete-orphan")
    competitor_records = relationship("CompetitorAnalysis", back_populates="main_business", cascade="all, delete-orphan")


class Review(Base):
    """
    Review entity - stores individual reviews for businesses
    """
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    review_text = Column(Text, nullable=False)
    author_name = Column(String(255))
    rating = Column(Float)
    review_date = Column(DateTime(timezone=True))
    source = Column(String(50), default="google_maps")  # google_maps, manual, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="reviews")
    sentiments = relationship("ReviewSentiment", back_populates="review", cascade="all, delete-orphan")


class ReviewSentiment(Base):
    """
    Review Sentiment - stores aspect-based sentiment analysis results
    """
    __tablename__ = "review_sentiments"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    aspect = Column(String(100), nullable=False)  # Food, Service, Ambiance, Price, etc.
    sentiment = Column(String(50), nullable=False)  # Positive, Negative, Neutral
    confidence_score = Column(Float)
    sentence = Column(Text)  # The sentence that triggered this sentiment
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="sentiments")


class Analysis(Base):
    """
    Analysis entity - stores aggregated ABSA results for a business
    """
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(50), default="absa")  # absa, competitor, insights
    total_reviews_analyzed = Column(Integer, default=0)
    
    # ABSA Results (stored as JSON)
    aspect_results = Column(JSON)  # {"Food": {...}, "Service": {...}}
    
    # Overall metrics
    overall_sentiment = Column(String(50))
    average_rating = Column(Float)
    
    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="analyses")


class CompetitorAnalysis(Base):
    """
    Competitor Analysis - stores competitor comparison data
    """
    __tablename__ = "competitor_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    main_business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    
    # Competitor business info (denormalized for historical tracking)
    competitor_place_id = Column(String(255), nullable=False)
    competitor_name = Column(String(255), nullable=False)
    competitor_rating = Column(Float)
    competitor_reviews = Column(Integer)
    competitor_address = Column(Text)
    
    # Analysis metrics
    rank = Column(Integer)  # 1-4 (top 4 competitors)
    rating_difference = Column(Float)  # main_business_rating - competitor_rating
    review_difference = Column(Integer)
    
    # Search parameters
    search_radius = Column(Integer)
    search_category = Column(String(100))
    
    # Timestamp
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    main_business = relationship("Business", back_populates="competitor_records")


class InsightReport(Base):
    """
    Insight Report - stores LLM-generated strategic insights
    """
    __tablename__ = "insight_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    
    # Report content
    executive_summary = Column(Text)
    marketing_recommendations = Column(JSON)
    pr_recommendations = Column(JSON)
    operational_improvements = Column(JSON)
    competitive_positioning = Column(JSON)
    priority_actions = Column(JSON)
    
    # RAG metadata
    rag_enabled = Column(Boolean, default=False)
    reviews_retrieved = Column(Integer, default=0)
    
    # Full insights (complete LLM output)
    full_insights_text = Column(Text)
    
    # Timestamp
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisHistory(Base):
    """
    Analysis History - tracks all analysis requests for auditing
    """
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    category = Column(String(100))
    location = Column(String(255))
    endpoint = Column(String(100))  # /analyze/business, /analyze/competitors, etc.
    status = Column(String(50))  # success, error
    error_message = Column(Text)
    execution_time_ms = Column(Integer)  # Execution time in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WebScrapingResult(Base):
    """
    Web Scraping Results - stores news articles and mentions from Google News
    """
    __tablename__ = "web_scraping_results"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    query_term = Column(String(255), nullable=False, index=True)  # "Kyani & Co." or "Competitor A"
    headline = Column(Text, nullable=False)
    link = Column(Text, nullable=False, unique=True)  # unique=True prevents duplicates
    source_name = Column(String(255))  # The Times of India, Mid-Day, etc.
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    business = relationship("Business")

