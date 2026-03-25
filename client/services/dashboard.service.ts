export type InsightsRequest = {
  business_name: string
  area: string
  city: string
  twitter_query?: string
  months_back?: number
}

export type CompetitorRequest = {
  business_name: string
  area: string
  city: string
  category?: string
  radius?: number
}

export type InsightsResponse = {
  status: string
  business_info?: {
    name?: string
    area?: string
    city?: string
    address?: string
    place_id?: string
    months_back?: number
  }
  summary_stats?: {
    total_reviews?: number
    avg_rating?: number
    media_mentions?: number
    overall_confidence?: number
  }
  sentiment_breakdown?: {
    positive?: number
    neutral?: number
    negative?: number
  }
  source_breakdown?: Record<string, Record<string, unknown>>
  review_volume_trend?: Array<{ month: string; count: number }>
  top_keywords?: Array<{ keyword: string; count: number }>
  aspect_sentiment?: Array<{
    aspect: string
    overall_sentiment: "Positive" | "Negative" | "Neutral"
    confidence_score: number
    mention_count?: number
  }>
}

export type CompetitorResponse = {
  status: string
  main_business?: {
    name?: string
    rating?: number
    total_reviews?: number
    address?: string
  }
  market_position?: {
    position?: string
    your_rating?: number
    avg_competitor_rating?: number
    avg_competitor_reviews?: number
    rating_vs_avg?: number
  }
  competitors?: Array<{
    name?: string
    rating?: number
    reviews?: number
    status?: string
    category?: string
    address?: string
  }>
  aspect_showdown?: Array<{
    aspect?: string
    your_score?: number | null
    competitor_avg?: number | null
  }>
}

export type DashboardData = {
  businessInfo: {
    name: string
    address: string
    category: string
    rating: number
    total_ratings: number
    reviews_analyzed: number
    mediaMentions: number
    confidenceScore: number
    lastUpdated: string
  }
  reviewVolumeData: Array<{ month: string; total: number; positive: number; negative: number; neutral: number }>
  sourceBreakdownData: Array<{ source: string; count: number; percentage: number }>
  sentimentAnalysis: {
    overall_sentiment: {
      sentiment: string
      positive_percentage: number
      negative_percentage: number
      neutral_percentage: number
    }
    aspects: Record<string, {
      total_mentions: number
      sentiment_breakdown: { Positive: number; Negative: number; Neutral: number }
      average_confidence: number
      overall_sentiment: string
    }>
  }
  strategicInsights: {
    executive_summary: string
    marketing_recommendations: string[]
    pr_recommendations: string[]
    operational_improvements: string[]
  }
  competitorData: {
    main_business: { name: string; rating: number; total_reviews: number; address: string }
    competitors: Array<{ name: string; rating: number; total_reviews: number; address: string; is_open: boolean; category: string }>
    competitive_analysis: {
      average_competitor_rating: number
      average_competitor_reviews: number
      your_rating_vs_average: string
      your_reviews_vs_average: string
      rating_difference: number
      review_difference: number
      market_position: string
    }
    aspect_showdown: Array<{ aspect: string; your_score: number; competitor_avg: number }>
  }
  forecastData: {
    forecast_data: Array<{ month: string; forecast: number; actual: number | null }>
    summary: {
      current_rating: number
      predicted_rating: number
      rating_change: number
      percentage_change: number
      trend: string
      confidence: string
    }
  }
  marketIntelligence: {
    total_articles: number
    media_visibility: string
    articles: Array<{ headline: string; link: string; source_name: string; query?: string }>
    top_sources: Array<{ source: string; count: number }>
    trend_topics: Array<{ topic: string; count: number }>
  }
  bcgMatrixData: {
    stars: Array<{ name: string; mentions: number; sentimentAvg: number }>
    cashCows: Array<{ name: string; mentions: number; sentimentAvg: number }>
    questionMarks: Array<{ name: string; mentions: number; sentimentAvg: number }>
    dogs: Array<{ name: string; mentions: number; sentimentAvg: number }>
  }
  ansoffMatrixData: {
    marketPenetration: { description: string; recommendations: string[]; riskLevel: string; expectedROI: string }
    productDevelopment: { description: string; recommendations: string[]; riskLevel: string; expectedROI: string }
    marketDevelopment: { description: string; recommendations: string[]; riskLevel: string; expectedROI: string }
    diversification: { description: string; recommendations: string[]; riskLevel: string; expectedROI: string }
  }
  ormData: {
    reviews: Array<{ id: number; rating: number; text: string; aspect: string; sentiment: string; source: string; date: string; status: string }>
    analytics: { responseRate: number; avgResponseTime: string; pendingNegative: number; sentimentTrend: string }
  }
  socialListeningData: {
    sources: Array<{ name: string; mentions: number; change: number; trend: string; color: string }>
    trendingTopics: Array<{ tag: string; count: number; change: number }>
    influencerMentions: { "100k+": number; "10k-100k": number; "1k-10k": number }
    recentMentions: Array<{ source: string; user: string; text: string; sentiment: string; date: string }>
  }
  advancedReportingData: {
    sentimentOverTime: Array<{ date: string; positive: number; negative: number; neutral: number }>
    ratingEvolution: Array<{ date: string; rating: number }>
    seasonalPatterns: { Food: number[]; Service: number[]; Ambiance: number[]; Price: number[] }
    alerts: Array<{ type: string; message: string; date: string }>
  }
  recommendations: Array<{
    id: number
    category: string
    priority: string
    icon: string
    title: string
    description: string
    impact: string
    timeline: string
    steps: string[]
  }>
  swotData: {
    strengths: Array<{ text: string; confidence: "High" | "Medium" | "Low"; platform: string; sourceText: string; sourceUrl: string }>
    weaknesses: Array<{ text: string; confidence: "High" | "Medium" | "Low"; platform: string; sourceText: string; sourceUrl: string }>
    opportunities: Array<{ text: string; confidence: "High" | "Medium" | "Low"; platform: string; sourceText: string; sourceUrl: string }>
    threats: Array<{ text: string; confidence: "High" | "Medium" | "Low"; platform: string; sourceText: string; sourceUrl: string }>
  }
  pestelData: Record<string, { label: string; color: string; items: Array<{ factor: string; impact: "Positive" | "Negative" | "Neutral"; severity: "High" | "Medium" | "Low"; description: string; implication: string }> }>
  fourPsData: {
    product: { score: number; summary: string; highlights: string[]; gaps: string[] }
    price: { score: number; summary: string; highlights: string[]; gaps: string[] }
    place: { score: number; summary: string; highlights: string[]; gaps: string[] }
    promotion: { score: number; summary: string; highlights: string[]; gaps: string[] }
  }
}

const EMPTY_DASHBOARD_DATA: DashboardData = {
  businessInfo: {
    name: "",
    address: "",
    category: "Restaurant",
    rating: 0,
    total_ratings: 0,
    reviews_analyzed: 0,
    mediaMentions: 0,
    confidenceScore: 0,
    lastUpdated: "",
  },
  reviewVolumeData: [],
  sourceBreakdownData: [],
  sentimentAnalysis: {
    overall_sentiment: { sentiment: "Neutral", positive_percentage: 0, negative_percentage: 0, neutral_percentage: 0 },
    aspects: {},
  },
  strategicInsights: {
    executive_summary: "",
    marketing_recommendations: ["No API data yet"],
    pr_recommendations: ["No API data yet"],
    operational_improvements: ["No API data yet"],
  },
  competitorData: {
    main_business: { name: "", rating: 0, total_reviews: 0, address: "" },
    competitors: [],
    competitive_analysis: {
      average_competitor_rating: 0,
      average_competitor_reviews: 0,
      your_rating_vs_average: "equal",
      your_reviews_vs_average: "equal",
      rating_difference: 0,
      review_difference: 0,
      market_position: "Unknown",
    },
    aspect_showdown: [],
  },
  forecastData: {
    forecast_data: [],
    summary: {
      current_rating: 0,
      predicted_rating: 0,
      rating_change: 0,
      percentage_change: 0,
      trend: "stable",
      confidence: "low",
    },
  },
  marketIntelligence: {
    total_articles: 0,
    media_visibility: "Low",
    articles: [],
    top_sources: [],
    trend_topics: [],
  },
  bcgMatrixData: { stars: [], cashCows: [], questionMarks: [], dogs: [] },
  ansoffMatrixData: {
    marketPenetration: { description: "", recommendations: [], riskLevel: "Low", expectedROI: "0%" },
    productDevelopment: { description: "", recommendations: [], riskLevel: "Medium", expectedROI: "0%" },
    marketDevelopment: { description: "", recommendations: [], riskLevel: "Medium", expectedROI: "0%" },
    diversification: { description: "", recommendations: [], riskLevel: "High", expectedROI: "0%" },
  },
  ormData: {
    reviews: [],
    analytics: { responseRate: 0, avgResponseTime: "N/A", pendingNegative: 0, sentimentTrend: "stable" },
  },
  socialListeningData: {
    sources: [],
    trendingTopics: [],
    influencerMentions: { "100k+": 0, "10k-100k": 0, "1k-10k": 0 },
    recentMentions: [],
  },
  advancedReportingData: {
    sentimentOverTime: [],
    ratingEvolution: [],
    seasonalPatterns: {
      Food: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      Service: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      Ambiance: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      Price: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    alerts: [],
  },
  recommendations: [],
  swotData: { strengths: [], weaknesses: [], opportunities: [], threats: [] },
  pestelData: {
    political: { label: "Political", color: "hsl(213 93% 68%)", items: [] },
    economic: { label: "Economic", color: "hsl(38 82% 58%)", items: [] },
    social: { label: "Social", color: "hsl(142 69% 58%)", items: [] },
    technological: { label: "Technological", color: "hsl(30 6% 72%)", items: [] },
    environmental: { label: "Environmental", color: "hsl(162 69% 48%)", items: [] },
    legal: { label: "Legal", color: "hsl(30 6% 55%)", items: [] },
  },
  fourPsData: {
    product: { score: 0, summary: "", highlights: [], gaps: [] },
    price: { score: 0, summary: "", highlights: [], gaps: [] },
    place: { score: 0, summary: "", highlights: [], gaps: [] },
    promotion: { score: 0, summary: "", highlights: [], gaps: [] },
  },
}

function normalizeMonth(monthValue: string): string {
  const date = new Date(`${monthValue}-01T00:00:00`)
  if (Number.isNaN(date.getTime())) return monthValue
  return date.toLocaleString("en-US", { month: "short" })
}

function titleCase(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase())
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Request failed (${response.status}): ${errorText}`)
  }

  return (await response.json()) as T
}

// ── Market Intelligence ───────────────────────────────────────────
export type MarketIntelligenceRequest = {
  business_name: string
  city: string
  category?: string
  current_rating?: number
  sentiment_score?: number
  months_ahead?: number
  location?: string
}

export type MarketIntelligenceAPIResponse = {
  status: string
  forecast: {
    current_rating: number
    predicted_rating: number
    expected_change: number
    expected_change_pct: number
    trend: string
    confidence: string
    sentiment_score_used: number
  }
  forecast_data: Array<{ month: string; forecast: number; actual: number | null }>
  market_intelligence_news: {
    total_articles: number
    media_visibility: string
    top_sources: Array<{ source: string; count: number }>
    trend_topics: Array<{ topic: string; count: number }>
    articles: Array<{ headline: string; link: string; source_name: string; query?: string }>
  }
}

export async function getMarketIntelligence(
  payload: MarketIntelligenceRequest,
): Promise<MarketIntelligenceAPIResponse> {
  return postJson<MarketIntelligenceAPIResponse>("/market-intelligence", payload)
}

export function mapMarketIntelligenceToDashboardFields(
  resp: MarketIntelligenceAPIResponse,
): {
  forecastData: DashboardData["forecastData"]
  marketIntelligence: DashboardData["marketIntelligence"]
} {
  const f = resp.forecast
  return {
    forecastData: {
      forecast_data: resp.forecast_data,
      summary: {
        current_rating: f.current_rating,
        predicted_rating: f.predicted_rating,
        rating_change: f.expected_change,
        percentage_change: f.expected_change_pct,
        trend: f.trend,
        confidence: f.confidence,
      },
    },
    marketIntelligence: {
      total_articles: resp.market_intelligence_news.total_articles,
      media_visibility: resp.market_intelligence_news.media_visibility,
      top_sources: resp.market_intelligence_news.top_sources,
      trend_topics: resp.market_intelligence_news.trend_topics,
      articles: resp.market_intelligence_news.articles,
    },
  }
}

export async function getBusinessInsights(payload: InsightsRequest): Promise<InsightsResponse> {
  return postJson<InsightsResponse>("/analyze/business/insights", payload)
}

export async function getCompetitorInsights(payload: CompetitorRequest): Promise<CompetitorResponse> {
  return postJson<CompetitorResponse>("/analyze/competitors", payload)
}

export function mapCompetitorToDashboardData(payload: CompetitorResponse): DashboardData["competitorData"] {
  const yourRating = Number(payload.market_position?.your_rating ?? payload.main_business?.rating ?? 0)
  const avgCompetitorRating = Number(payload.market_position?.avg_competitor_rating ?? 0)
  const yourReviews = Number(payload.main_business?.total_reviews ?? 0)
  const avgCompetitorReviews = Number(payload.market_position?.avg_competitor_reviews ?? 0)

  return {
    main_business: {
      name: payload.main_business?.name ?? "",
      rating: yourRating,
      total_reviews: yourReviews,
      address: payload.main_business?.address ?? "",
    },
    competitors: (payload.competitors ?? []).map((c) => ({
      name: c.name ?? "",
      rating: Number(c.rating ?? 0),
      total_reviews: Number(c.reviews ?? 0),
      address: c.address ?? "",
      is_open: (c.status ?? "").toLowerCase() === "open",
      category: c.category ?? "Restaurant",
    })),
    competitive_analysis: {
      average_competitor_rating: avgCompetitorRating,
      average_competitor_reviews: avgCompetitorReviews,
      your_rating_vs_average: yourRating >= avgCompetitorRating ? "above" : "below",
      your_reviews_vs_average: yourReviews >= avgCompetitorReviews ? "above" : "below",
      rating_difference: Math.abs(Number((yourRating - avgCompetitorRating).toFixed(2))),
      review_difference: Math.abs(Math.round(yourReviews - avgCompetitorReviews)),
      market_position: payload.market_position?.position ?? "Unknown",
    },
    aspect_showdown: (payload.aspect_showdown ?? []).map((row) => ({
      aspect: row.aspect ?? "",
      your_score: Number(row.your_score ?? 0),
      competitor_avg: Number(row.competitor_avg ?? 0),
    })),
  }
}

export function mapInsightsToDashboardData(payload: InsightsResponse): DashboardData {
  const positive = Math.round(payload.sentiment_breakdown?.positive ?? 0)
  const neutral = Math.round(payload.sentiment_breakdown?.neutral ?? 0)
  const negative = Math.round(payload.sentiment_breakdown?.negative ?? 0)

  const sourceEntries = Object.entries(payload.source_breakdown ?? {})
  const totalSourceCount = sourceEntries.reduce((sum, [, value]) => {
    const count = Number((value.review_count as number) ?? (value.article_count as number) ?? 0)
    return sum + (Number.isFinite(count) ? count : 0)
  }, 0)

  const sourceBreakdownData = sourceEntries
    .map(([source, value]) => {
      const count = Number((value.review_count as number) ?? (value.article_count as number) ?? 0)
      const percentage = totalSourceCount > 0 ? Math.round((count / totalSourceCount) * 100) : 0
      return { source: titleCase(source), count, percentage }
    })
    .filter((x) => x.count > 0)

  const reviewVolumeData = (payload.review_volume_trend ?? []).map((row) => {
    const posCount = Math.round((row.count * positive) / 100)
    const negCount = Math.round((row.count * negative) / 100)
    const neuCount = Math.max(0, row.count - posCount - negCount)
    return {
      month: normalizeMonth(row.month),
      total: row.count,
      positive: posCount,
      negative: negCount,
      neutral: neuCount,
    }
  })

  const aspects: DashboardData["sentimentAnalysis"]["aspects"] = {}
  for (const aspect of payload.aspect_sentiment ?? []) {
    const mentions = aspect.mention_count ?? 0
    aspects[aspect.aspect] = {
      total_mentions: mentions,
      sentiment_breakdown: {
        Positive: aspect.overall_sentiment === "Positive" ? mentions : 0,
        Negative: aspect.overall_sentiment === "Negative" ? mentions : 0,
        Neutral: aspect.overall_sentiment === "Neutral" ? mentions : 0,
      },
      average_confidence: Number(aspect.confidence_score.toFixed(2)),
      overall_sentiment: aspect.overall_sentiment,
    }
  }

  const topKeywords = payload.top_keywords ?? []
  const bcgMatrixData: DashboardData["bcgMatrixData"] = {
    stars: topKeywords.slice(0, 3).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 4.7 })),
    cashCows: topKeywords.slice(3, 6).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 4.3 })),
    questionMarks: topKeywords.slice(6, 8).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 3.9 })),
    dogs: topKeywords.slice(8, 10).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 3.0 })),
  }

  const newsArticles = Number(payload.summary_stats?.media_mentions ?? 0)
  const data: DashboardData = {
    ...EMPTY_DASHBOARD_DATA,
    businessInfo: {
      name: payload.business_info?.name ?? "",
      address: payload.business_info?.address ?? "",
      category: "Restaurant",
      rating: Number((payload.summary_stats?.avg_rating ?? 0).toFixed(2)),
      total_ratings: payload.summary_stats?.total_reviews ?? 0,
      reviews_analyzed: payload.summary_stats?.total_reviews ?? 0,
      mediaMentions: newsArticles,
      confidenceScore: Math.round(payload.summary_stats?.overall_confidence ?? 0),
      lastUpdated: new Date().toISOString(),
    },
    reviewVolumeData,
    sourceBreakdownData,
    sentimentAnalysis: {
      overall_sentiment: {
        sentiment: positive >= negative ? "Positive" : "Negative",
        positive_percentage: positive,
        negative_percentage: negative,
        neutral_percentage: neutral,
      },
      aspects,
    },
    strategicInsights: {
      executive_summary:
        `Analyzed ${payload.summary_stats?.total_reviews ?? 0} reviews for ${payload.business_info?.name ?? "the business"}. ` +
        `Overall sentiment is ${positive}% positive with ${Math.round(payload.summary_stats?.overall_confidence ?? 0)}% confidence.`,
      marketing_recommendations: [
        "Promote highest-mentioned positive aspects in campaigns.",
        "Use top keywords as ad copy anchors.",
        "Highlight customer proof in social creatives.",
      ],
      pr_recommendations: [
        "Respond to negative trends within 24 hours.",
        "Publish quality-improvement updates monthly.",
        "Pitch sentiment milestones to local media.",
      ],
      operational_improvements: [
        "Assign owners to low-sentiment aspects.",
        "Run weekly fixes against negative mentions.",
        "Track closure SLA for complaint categories.",
      ],
    },
    competitorData: {
      ...EMPTY_DASHBOARD_DATA.competitorData,
      main_business: {
        name: payload.business_info?.name ?? "",
        rating: Number((payload.summary_stats?.avg_rating ?? 0).toFixed(2)),
        total_reviews: payload.summary_stats?.total_reviews ?? 0,
        address: payload.business_info?.address ?? "",
      },
      aspect_showdown: (payload.aspect_sentiment ?? []).slice(0, 5).map((a) => ({
        aspect: a.aspect,
        your_score: Number((1 + 4 * a.confidence_score).toFixed(1)),
        competitor_avg: Number((Math.max(1, 1 + 4 * (a.confidence_score - 0.08))).toFixed(1)),
      })),
    },
    forecastData: {
      forecast_data: [],
      summary: {
        current_rating: Number((payload.summary_stats?.avg_rating ?? 0).toFixed(2)),
        predicted_rating: Number(((payload.summary_stats?.avg_rating ?? 0) + 0.15).toFixed(2)),
        rating_change: 0.15,
        percentage_change: 0,
        trend: "improving",
        confidence: "medium",
      },
    },
    marketIntelligence: {
      total_articles: newsArticles,
      media_visibility: newsArticles >= 10 ? "High" : newsArticles >= 4 ? "Medium" : "Low",
      articles: [],
      top_sources: [],
      trend_topics: [],
    },
    bcgMatrixData,
    ormData: {
      reviews: (payload.aspect_sentiment ?? []).slice(0, 6).map((a, i) => ({
        id: i + 1,
        rating: a.overall_sentiment === "Positive" ? 5 : a.overall_sentiment === "Negative" ? 2 : 3,
        text: `${a.aspect} sentiment is ${a.overall_sentiment.toLowerCase()} (${Math.round(a.confidence_score * 100)}% confidence).`,
        aspect: a.aspect,
        sentiment: a.overall_sentiment,
        source: "Google Maps",
        date: new Date().toISOString().slice(0, 10),
        status: i % 2 === 0 ? "Pending" : "Responded",
      })),
      analytics: {
        responseRate: 80,
        avgResponseTime: "24 hours",
        pendingNegative: (payload.aspect_sentiment ?? []).filter((a) => a.overall_sentiment === "Negative").length,
        sentimentTrend: positive >= negative ? "improving" : "declining",
      },
    },
    socialListeningData: {
      sources: sourceBreakdownData.map((s, i) => ({
        name: s.source,
        mentions: s.count,
        change: i % 2 === 0 ? 10 : -5,
        trend: i % 2 === 0 ? "up" : "down",
        color: i % 2 === 0 ? "#1DA1F2" : "#FF4500",
      })),
      trendingTopics: topKeywords.slice(0, 4).map((k, i) => ({
        tag: `#${String(k.keyword).replace(/\s+/g, "")}`,
        count: k.count,
        change: i % 2 === 0 ? 12 : -4,
      })),
      influencerMentions: { "100k+": 0, "10k-100k": 0, "1k-10k": 0 },
      recentMentions: [],
    },
    advancedReportingData: {
      ...EMPTY_DASHBOARD_DATA.advancedReportingData,
      sentimentOverTime: reviewVolumeData.slice(-6).map((x, i) => ({
        date: `Week ${i + 1}`,
        positive: x.positive,
        negative: x.negative,
        neutral: x.neutral,
      })),
      ratingEvolution: reviewVolumeData.slice(-6).map((x) => ({ date: x.month, rating: Number((payload.summary_stats?.avg_rating ?? 0).toFixed(2)) })),
    },
    recommendations: [
      {
        id: 1,
        category: "Operations",
        priority: "High",
        icon: "target",
        title: "Address Negative Aspect Trends",
        description: "Prioritize actions for aspects with persistent negative sentiment.",
        impact: "Improve sentiment mix and response quality.",
        timeline: "2-4 weeks",
        steps: ["Identify top negative aspects", "Assign owners", "Track weekly trend"],
      },
    ],
    swotData: {
      strengths: (payload.aspect_sentiment ?? [])
        .filter((a) => a.overall_sentiment === "Positive")
        .slice(0, 4)
        .map((a) => ({
          text: `${a.aspect} is a current strength`,
          confidence: "High",
          platform: "ABSA",
          sourceText: `${a.aspect} trending positive`,
          sourceUrl: "#",
        })),
      weaknesses: (payload.aspect_sentiment ?? [])
        .filter((a) => a.overall_sentiment === "Negative")
        .slice(0, 4)
        .map((a) => ({
          text: `${a.aspect} needs improvement`,
          confidence: "High",
          platform: "ABSA",
          sourceText: `${a.aspect} trending negative`,
          sourceUrl: "#",
        })),
      opportunities: [],
      threats: [],
    },
  }

  data.forecastData.summary.percentage_change = data.forecastData.summary.current_rating > 0
    ? Number(((data.forecastData.summary.rating_change / data.forecastData.summary.current_rating) * 100).toFixed(1))
    : 0

  return data
}
