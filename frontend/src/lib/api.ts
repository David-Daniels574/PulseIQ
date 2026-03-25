/**
 * API Integration for GrowKaro ABSA Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface BusinessRequest {
  business_name: string;
  category?: string;
  location: string;
}

export interface AspectAnalysis {
  [aspect: string]: {
    positive: number;
    negative: number;
    neutral: number;
    mentions: number;
    sentiment_distribution: {
      positive: number;
      negative: number;
      neutral: number;
    };
    average_sentiment_score: number;
  };
}

export interface OverallSentiment {
  sentiment: string;
  confidence: number;
  positive_percentage: number;
  negative_percentage: number;
  neutral_percentage: number;
}

export interface ABSAResults {
  aspect_analysis: AspectAnalysis;
  overall_sentiment: OverallSentiment;
  total_reviews_analyzed: number;
  sentiment_summary: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export interface BusinessInfo {
  name: string;
  address: string;
  rating: number;
  total_ratings: number;
  reviews_analyzed: number;
}

export interface StrategicInsights {
  executive_summary?: string;
  marketing_recommendations?: string[];
  pr_recommendations?: string[];
  operational_improvements?: string[];
  competitive_positioning?: string[];
  priority_actions?: string[];
}

// Raw API response structure (what backend actually sends)
interface RawAspectData {
  total_mentions: number;
  sentiment_breakdown: {
    Positive: number;
    Negative: number;
    Neutral: number;
  };
  average_confidence: number;
  overall_sentiment: string;
}

interface RawAPIResponse {
  status: string;
  business_info: BusinessInfo;
  analysis: {
    [aspect: string]: RawAspectData;
  };
  strategic_insights: any;
  quick_summary: string;
}

// Transformed response (what frontend expects)
export interface BusinessInsightsResponse {
  status: string;
  business_info: BusinessInfo;
  analysis: ABSAResults;
  strategic_insights: StrategicInsights;
  quick_summary: string;
  raw_strategic_insights?: string;
  strategic_insights_paragraphs?: string[];
}

/**
 * Transform raw API response to frontend format
 */
function transformAPIResponse(raw: RawAPIResponse): BusinessInsightsResponse {
  // Transform aspect analysis
  const aspect_analysis: AspectAnalysis = {};
  let totalPositive = 0;
  let totalNegative = 0;
  let totalNeutral = 0;

  for (const [aspect, data] of Object.entries(raw.analysis)) {
    aspect_analysis[aspect] = {
      positive: data.sentiment_breakdown.Positive || 0,
      negative: data.sentiment_breakdown.Negative || 0,
      neutral: data.sentiment_breakdown.Neutral || 0,
      mentions: data.total_mentions,
      sentiment_distribution: {
        positive: data.sentiment_breakdown.Positive || 0,
        negative: data.sentiment_breakdown.Negative || 0,
        neutral: data.sentiment_breakdown.Neutral || 0,
      },
      average_sentiment_score: data.average_confidence,
    };

    totalPositive += data.sentiment_breakdown.Positive || 0;
    totalNegative += data.sentiment_breakdown.Negative || 0;
    totalNeutral += data.sentiment_breakdown.Neutral || 0;
  }

  // Evaluate overall sentiment
  const total = totalPositive + totalNegative + totalNeutral;
  const positivePercentage = total > 0 ? (totalPositive / total) * 100 : 0;
  const negativePercentage = total > 0 ? (totalNegative / total) * 100 : 0;
  const neutralPercentage = total > 0 ? (totalNeutral / total) * 100 : 0;

  let overallSentiment = 'neutral';
  if (positivePercentage > negativePercentage && positivePercentage > neutralPercentage) {
    overallSentiment = 'positive';
  } else if (negativePercentage > positivePercentage) {
    overallSentiment = 'negative';
  }

  // Fix extraction of strategic insights text from backend response
  const rawStrategicInsights =
    typeof raw.strategic_insights === 'string'
      ? raw.strategic_insights
      : typeof raw.strategic_insights?.strategic_insights === 'string'
      ? raw.strategic_insights.strategic_insights
      : typeof raw.strategic_insights?.executive_summary === 'string'
      ? raw.strategic_insights.executive_summary
      : undefined;

  // Split markdown text into paragraphs
  const insightsParagraphs = rawStrategicInsights
    ? rawStrategicInsights
        .split(/\n{2,}/)
        .map((p) => p.trim())
        .filter(Boolean)
    : [];

  return {
    status: raw.status,
    business_info: raw.business_info,
    analysis: {
      aspect_analysis,
      overall_sentiment: {
        sentiment: overallSentiment,
        confidence: 0.85,
        positive_percentage: positivePercentage,
        negative_percentage: negativePercentage,
        neutral_percentage: neutralPercentage,
      },
      total_reviews_analyzed: raw.business_info.reviews_analyzed,
      sentiment_summary: {
        positive: totalPositive,
        negative: totalNegative,
        neutral: totalNeutral,
      },
    },

    // Rebuild strategic insights consistently
    strategic_insights:
      typeof raw.strategic_insights === 'string'
        ? { executive_summary: raw.strategic_insights }
        : raw.strategic_insights || {},

    quick_summary: raw.quick_summary,
    raw_strategic_insights: rawStrategicInsights,
    strategic_insights_paragraphs: insightsParagraphs,
  };
}

/**
 * Fetch business insights with ABSA analysis
 */
export async function fetchBusinessInsights(
  request: BusinessRequest
): Promise<BusinessInsightsResponse> {
  console.log('Making API request with:', request);
  
  const response = await fetch(`${API_BASE_URL}/analyze/business/insights`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    console.error('API Error:', error);
    throw new Error(error.detail || 'Failed to fetch business insights');
  }

  const rawData: RawAPIResponse = await response.json();
  console.log('Raw API Response:', rawData);
  
  const transformedData = transformAPIResponse(rawData);
  console.log('Transformed Response:', transformedData);
  
  return transformedData;
}

/**
 * Fetch competitor analysis
 */
export interface CompetitorRequest {
  business_name: string;
  category: string;
  location: string;
  radius?: number;
}

export interface CompetitorOverview {
  name: string;
  place_id: string;
  rating: number;
  total_reviews: number;
  address?: string;
  is_open?: boolean;
  db_id?: number;
}

export interface AspectShowdownEntry {
  aspect: string;
  your_score: number | null;
  competitor_avg: number | null;
  scale: string;
}

export interface AspectShowdownData {
  aspects: AspectShowdownEntry[];
  methodology: string;
}

export interface CompetitiveAnalysisSummary {
  average_competitor_rating: number;
  average_competitor_reviews: number;
  your_rating_vs_average: string;
  your_reviews_vs_average: string;
  rating_difference: number;
  review_difference: number;
  market_position: string;
}

export interface CompetitorAnalysisResponse {
  status: string;
  main_business: CompetitorOverview;
  competitors: CompetitorOverview[];
  total_competitors_found: number;
  competitors_stored_in_db: number;
  competitive_analysis: CompetitiveAnalysisSummary | null;
  aspect_showdown: AspectShowdownData;
  competitor_aspect_scores: Record<string, Record<string, number>>;
  search_parameters: {
    category?: string;
    location: string;
    radius_meters: number;
    radius_miles: number;
  };
  data_source: string;
  execution_time_ms: number;
}

export async function fetchCompetitorAnalysis(
  request: CompetitorRequest
): Promise<CompetitorAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze/competitors`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch competitor analysis');
  }

  const data: CompetitorAnalysisResponse = await response.json();
  return data;
}

/**
 * Fetch market intelligence
 */
export interface MarketIntelligenceRequest {
  business_name: string;
  location?: string;
  include_competitors?: boolean;
  competitor_names?: string[];
}

export async function fetchMarketIntelligence(request: MarketIntelligenceRequest) {
  const response = await fetch(`${API_BASE_URL}/market-intelligence`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch market intelligence');
  }

  return response.json();
}

/**
 * Get stored market intelligence
 */
export async function getStoredMarketIntelligence(businessName: string, limit: number = 50) {
  const response = await fetch(
    `${API_BASE_URL}/market-intelligence/${encodeURIComponent(businessName)}?limit=${limit}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch stored market intelligence');
  }

  return response.json();
}

/**
 * Get analysis history
 */
export async function getAnalysisHistory(limit: number = 50) {
  const response = await fetch(`${API_BASE_URL}/history?limit=${limit}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch analysis history');
  }

  return response.json();
}

/**
 * Get all businesses
 */
export async function getAllBusinesses(category?: string) {
  const url = category
    ? `${API_BASE_URL}/businesses?category=${encodeURIComponent(category)}`
    : `${API_BASE_URL}/businesses`;

  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch businesses');
  }

  return response.json();
}

/**
 * Get business reports
 */
export async function getBusinessReports(placeId: string) {
  const response = await fetch(`${API_BASE_URL}/business/${encodeURIComponent(placeId)}/reports`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch business reports');
  }

  return response.json();
}

/**
 * Fetch star rating forecast
 */
export interface ForecastRequest {
  business_name: string;
  city: string;
  category: string;
  current_rating: number;
  sentiment_score: number;
  months_ahead?: number;
}

export interface ForecastDataPoint {
  month: string;
  forecast: number;
  actual: number | null;
}

export interface ForecastSummary {
  current_rating: number;
  predicted_rating: number;
  rating_change: number;
  percentage_change: number;
  trend: string;
  confidence: string;
}

export interface ForecastResponse {
  status: string;
  business_name: string;
  city: string;
  category: string;
  forecast_data: ForecastDataPoint[];
  summary: ForecastSummary;
  model: string;
  input_parameters: {
    current_rating: number;
    sentiment_score: number;
    months_ahead: number;
  };
  execution_time_ms: number;
  generated_at: string;
}

export async function fetchRatingForecast(request: ForecastRequest): Promise<ForecastResponse> {
  const response = await fetch(`${API_BASE_URL}/forecast`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch rating forecast');
  }

  return response.json();
}
