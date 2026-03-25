// Hardcoded mock data for 360° Restaurant Oracle

export const businessInfo = {
  name: "The Golden Fork",
  address: "123 Culinary Ave, New York, NY 10001",
  category: "Fine Dining Restaurant",
  rating: 4.5,
  total_ratings: 1847,
  reviews_analyzed: 150,
  mediaMentions: 24,
  confidenceScore: 91,
  lastUpdated: "2026-03-25T10:30:00Z"
}

export const reviewVolumeData = [
  { month: "Jun", total: 18, positive: 13, negative: 3, neutral: 2 },
  { month: "Jul", total: 22, positive: 15, negative: 4, neutral: 3 },
  { month: "Aug", total: 31, positive: 22, negative: 5, neutral: 4 },
  { month: "Sep", total: 27, positive: 20, negative: 4, neutral: 3 },
  { month: "Oct", total: 35, positive: 26, negative: 5, neutral: 4 },
  { month: "Nov", total: 42, positive: 32, negative: 6, neutral: 4 },
  { month: "Dec", total: 38, positive: 28, negative: 6, neutral: 4 },
  { month: "Jan", total: 29, positive: 21, negative: 5, neutral: 3 },
  { month: "Feb", total: 33, positive: 24, negative: 6, neutral: 3 },
  { month: "Mar", total: 25, positive: 19, negative: 3, neutral: 3 },
]

export const sourceBreakdownData = [
  { source: "Google Maps", count: 612, percentage: 33 },
  { source: "Twitter",     count: 487, percentage: 26 },
  { source: "TripAdvisor", count: 371, percentage: 20 },
  { source: "Yelp",        count: 224, percentage: 12 },
  { source: "Reddit",      count: 153, percentage:  8 },
]

export const sentimentAnalysis = {
  overall_sentiment: {
    sentiment: "Positive",
    positive_percentage: 72,
    negative_percentage: 15,
    neutral_percentage: 13
  },
  aspects: {
    Food: {
      total_mentions: 287,
      sentiment_breakdown: { Positive: 245, Negative: 22, Neutral: 20 },
      average_confidence: 0.92,
      overall_sentiment: "Positive"
    },
    Service: {
      total_mentions: 198,
      sentiment_breakdown: { Positive: 142, Negative: 38, Neutral: 18 },
      average_confidence: 0.87,
      overall_sentiment: "Positive"
    },
    Ambiance: {
      total_mentions: 156,
      sentiment_breakdown: { Positive: 128, Negative: 12, Neutral: 16 },
      average_confidence: 0.89,
      overall_sentiment: "Positive"
    },
    Price: {
      total_mentions: 134,
      sentiment_breakdown: { Positive: 45, Negative: 67, Neutral: 22 },
      average_confidence: 0.78,
      overall_sentiment: "Negative"
    },
    Location: {
      total_mentions: 89,
      sentiment_breakdown: { Positive: 72, Negative: 8, Neutral: 9 },
      average_confidence: 0.85,
      overall_sentiment: "Positive"
    },
    Cleanliness: {
      total_mentions: 67,
      sentiment_breakdown: { Positive: 58, Negative: 4, Neutral: 5 },
      average_confidence: 0.91,
      overall_sentiment: "Positive"
    }
  }
}

export const strategicInsights = {
  executive_summary: `Based on comprehensive analysis of 150 customer reviews, The Golden Fork demonstrates strong performance in food quality and ambiance, positioning it as a premium dining destination. The establishment shows exceptional strength in culinary execution with a 92% confidence score in food-related sentiment. However, price perception emerges as the primary area requiring strategic attention, with 50% of pricing mentions carrying negative sentiment. Service consistency shows room for improvement, particularly during peak hours as indicated by multiple mentions of wait times. Immediate opportunities include implementing dynamic pricing strategies and service recovery protocols to address customer concerns proactively.`,
  marketing_recommendations: [
    "Leverage exceptional food quality scores in social media campaigns with user-generated content",
    "Create premium experience packages that justify pricing through added value",
    "Develop influencer partnerships focusing on signature dishes and ambiance",
    "Launch seasonal menu promotions to create urgency and perceived value"
  ],
  pr_recommendations: [
    "Proactively respond to negative reviews within 24 hours with personalized solutions",
    "Feature chef interviews and behind-the-scenes content to humanize the brand",
    "Partner with local food critics for exclusive tasting events"
  ],
  operational_improvements: [
    "Implement table management system to reduce wait times during peak hours",
    "Train staff on handling price objections with value-focused responses",
    "Create express lunch menu for time-conscious diners",
    "Establish regular menu engineering sessions to optimize profitability"
  ]
}

export const competitorData = {
  main_business: {
    name: "The Golden Fork",
    rating: 4.5,
    total_reviews: 1847,
    address: "123 Culinary Ave, New York, NY"
  },
  competitors: [
    { name: "Bella Italia", rating: 4.7, total_reviews: 2341, address: "456 Food St", is_open: true, category: "Italian" },
    { name: "Ocean Blue", rating: 4.3, total_reviews: 1567, address: "789 Seafood Ln", is_open: true, category: "Seafood" },
    { name: "The Grill House", rating: 4.6, total_reviews: 2089, address: "321 Steak Blvd", is_open: false, category: "Steakhouse" },
    { name: "Garden Fresh", rating: 4.2, total_reviews: 987, address: "654 Veggie Way", is_open: true, category: "Vegetarian" },
    { name: "Spice Route", rating: 4.4, total_reviews: 1654, address: "987 Curry Ave", is_open: true, category: "Indian" }
  ],
  competitive_analysis: {
    average_competitor_rating: 4.44,
    average_competitor_reviews: 1728,
    your_rating_vs_average: "above",
    your_reviews_vs_average: "above",
    rating_difference: 0.06,
    review_difference: 119,
    market_position: "Leader"
  },
  aspect_showdown: [
    { aspect: "Food", your_score: 4.7, competitor_avg: 4.4 },
    { aspect: "Service", your_score: 4.2, competitor_avg: 4.1 },
    { aspect: "Ambiance", your_score: 4.6, competitor_avg: 4.3 },
    { aspect: "Price", your_score: 3.8, competitor_avg: 4.0 },
    { aspect: "Location", your_score: 4.5, competitor_avg: 4.2 }
  ]
}

export const forecastData = {
  forecast_data: [
    { month: "Oct", forecast: 4.45, actual: 4.45 },
    { month: "Nov", forecast: 4.48, actual: 4.47 },
    { month: "Dec", forecast: 4.52, actual: 4.50 },
    { month: "Jan", forecast: 4.55, actual: null },
    { month: "Feb", forecast: 4.58, actual: null },
    { month: "Mar", forecast: 4.62, actual: null },
    { month: "Apr", forecast: 4.65, actual: null },
    { month: "May", forecast: 4.68, actual: null },
    { month: "Jun", forecast: 4.72, actual: null }
  ],
  summary: {
    current_rating: 4.50,
    predicted_rating: 4.72,
    rating_change: 0.22,
    percentage_change: 4.9,
    trend: "improving",
    confidence: "high"
  }
}

export const marketIntelligence = {
  total_articles_found: 24,
  media_visibility: "High",
  articles: [
    { headline: "NYC's Hidden Gem: The Golden Fork Redefines Fine Dining", link: "#", source_name: "NY Times Food", date: "2026-03-20" },
    { headline: "Top 10 Restaurants in Manhattan for 2026", link: "#", source_name: "Eater NY", date: "2026-03-18" },
    { headline: "The Golden Fork Chef Wins Culinary Excellence Award", link: "#", source_name: "Food & Wine", date: "2026-03-15" },
    { headline: "Restaurant Week Preview: Best Prix Fixe Menus", link: "#", source_name: "Time Out NY", date: "2026-03-12" },
    { headline: "Sustainable Dining: The Golden Fork's Farm-to-Table Initiative", link: "#", source_name: "Grub Street", date: "2026-03-08" }
  ],
  top_sources: {
    "NY Times Food": 8,
    "Eater NY": 6,
    "Food & Wine": 5,
    "Time Out NY": 3,
    "Grub Street": 2
  }
}

export const bcgMatrixData = {
  stars: [
    { name: "Truffle Risotto", mentions: 145, sentimentAvg: 4.9 },
    { name: "Wagyu Steak", mentions: 132, sentimentAvg: 4.8 },
    { name: "Lobster Thermidor", mentions: 98, sentimentAvg: 4.7 }
  ],
  cashCows: [
    { name: "Classic Caesar Salad", mentions: 187, sentimentAvg: 4.3 },
    { name: "Grilled Salmon", mentions: 165, sentimentAvg: 4.4 },
    { name: "Pasta Carbonara", mentions: 156, sentimentAvg: 4.2 }
  ],
  questionMarks: [
    { name: "Vegan Tasting Menu", mentions: 34, sentimentAvg: 4.1 },
    { name: "Molecular Dessert", mentions: 28, sentimentAvg: 3.9 }
  ],
  dogs: [
    { name: "House Soup", mentions: 12, sentimentAvg: 2.8 },
    { name: "Basic Bread Basket", mentions: 8, sentimentAvg: 2.5 }
  ]
}

export const ansoffMatrixData = {
  marketPenetration: {
    description: "Increase market share with existing products in existing markets",
    recommendations: [
      "Launch customer loyalty program with tiered rewards",
      "Increase social media advertising by 40%",
      "Implement dynamic pricing for off-peak hours",
      "Partner with corporate accounts for regular bookings"
    ],
    riskLevel: "Low",
    expectedROI: "15-25%"
  },
  productDevelopment: {
    description: "Introduce new products to existing market",
    recommendations: [
      "Launch chef's tasting menu experience",
      "Introduce seasonal rotating specials",
      "Create premium wine pairing packages",
      "Develop take-home gourmet meal kits"
    ],
    riskLevel: "Medium",
    expectedROI: "20-35%"
  },
  marketDevelopment: {
    description: "Enter new markets with existing products",
    recommendations: [
      "Open pop-up locations in high-traffic areas",
      "Partner with food delivery platforms",
      "Explore catering services for events",
      "Launch virtual cooking classes"
    ],
    riskLevel: "Medium",
    expectedROI: "18-30%"
  },
  diversification: {
    description: "New products in new markets",
    recommendations: [
      "Launch branded food products in retail",
      "Create franchise model for expansion",
      "Develop restaurant consulting services",
      "Open cooking school with certification"
    ],
    riskLevel: "High",
    expectedROI: "25-50%"
  }
}

export const ormData = {
  reviews: [
    { id: 1, rating: 5, text: "Absolutely phenomenal experience! The truffle risotto was divine and the service was impeccable.", aspect: "Food", sentiment: "Positive", source: "Google Maps", date: "2026-03-24", status: "Responded" },
    { id: 2, rating: 2, text: "Waited 45 minutes for our table despite having a reservation. Very disappointed.", aspect: "Service", sentiment: "Negative", source: "Twitter", date: "2026-03-23", status: "Pending" },
    { id: 3, rating: 4, text: "Great ambiance and food, but prices are a bit steep for the portion sizes.", aspect: "Price", sentiment: "Neutral", source: "Google Maps", date: "2026-03-22", status: "Responded" },
    { id: 4, rating: 5, text: "The chef's special was outstanding! Will definitely be back.", aspect: "Food", sentiment: "Positive", source: "TripAdvisor", date: "2026-03-21", status: "Pending" },
    { id: 5, rating: 1, text: "Food was cold and the waiter was rude. Never coming back.", aspect: "Service", sentiment: "Negative", source: "Twitter", date: "2026-03-20", status: "Pending" },
    { id: 6, rating: 4, text: "Beautiful interior and great cocktails. Food was good too!", aspect: "Ambiance", sentiment: "Positive", source: "Google Maps", date: "2026-03-19", status: "Responded" }
  ],
  analytics: {
    responseRate: 78,
    avgResponseTime: "18 hours",
    pendingNegative: 2,
    sentimentTrend: "improving"
  }
}

export const socialListeningData = {
  sources: [
    { name: "Twitter/X", mentions: 234, change: 45, trend: "up", color: "#1DA1F2" },
    { name: "Twitter/X", mentions: 156, change: -12, trend: "down", color: "#1DA1F2" },
    { name: "Reddit", mentions: 89, change: 0, trend: "stable", color: "#FF4500" },
    { name: "Facebook", mentions: 178, change: 23, trend: "up", color: "#1877F2" },
    { name: "TikTok", mentions: 312, change: 87, trend: "up", color: "#000000" }
  ],
  trendingTopics: [
    { tag: "#GoldenForkNYC", count: 456, change: 23 },
    { tag: "#NYCFineDining", count: 234, change: 12 },
    { tag: "#TruffleRisotto", count: 189, change: 45 },
    { tag: "#FoodieNYC", count: 156, change: -5 }
  ],
  influencerMentions: {
    "100k+": 3,
    "10k-100k": 12,
    "1k-10k": 34
  },
  recentMentions: [
    { source: "Twitter", user: "@nycfoodie", text: "The truffle risotto at @goldenfork is absolutely incredible!", sentiment: "Positive", date: "2026-03-24" },
    { source: "Twitter", user: "@foodcritic_ny", text: "Finally tried Golden Fork. Lived up to the hype!", sentiment: "Positive", date: "2026-03-23" },
    { source: "Reddit", user: "u/manhattandiner", text: "Is Golden Fork worth the price? Thinking of going for anniversary", sentiment: "Neutral", date: "2026-03-22" }
  ]
}

export const advancedReportingData = {
  sentimentOverTime: [
    { date: "Week 1", positive: 65, negative: 20, neutral: 15 },
    { date: "Week 2", positive: 68, negative: 18, neutral: 14 },
    { date: "Week 3", positive: 72, negative: 15, neutral: 13 },
    { date: "Week 4", positive: 70, negative: 17, neutral: 13 },
    { date: "Week 5", positive: 74, negative: 14, neutral: 12 },
    { date: "Week 6", positive: 76, negative: 12, neutral: 12 }
  ],
  ratingEvolution: [
    { date: "Jan", rating: 4.3 },
    { date: "Feb", rating: 4.35 },
    { date: "Mar", rating: 4.4 },
    { date: "Apr", rating: 4.42 },
    { date: "May", rating: 4.45 },
    { date: "Jun", rating: 4.5 }
  ],
  seasonalPatterns: {
    Food: [4.5, 4.6, 4.7, 4.8, 4.6, 4.5, 4.4, 4.5, 4.6, 4.7, 4.8, 4.7],
    Service: [4.0, 4.1, 4.2, 4.3, 4.1, 3.9, 3.8, 4.0, 4.2, 4.3, 4.2, 4.1],
    Ambiance: [4.4, 4.5, 4.5, 4.6, 4.5, 4.4, 4.4, 4.5, 4.6, 4.6, 4.7, 4.6],
    Price: [3.5, 3.6, 3.7, 3.8, 3.6, 3.5, 3.4, 3.5, 3.6, 3.7, 3.8, 3.7]
  },
  alerts: [
    { type: "warning", message: "Service complaints increased 15% this week", date: "2026-03-24" },
    { type: "success", message: "Food quality mentions at all-time high", date: "2026-03-23" }
  ]
}

export const recommendations = [
  {
    id: 1,
    category: "Marketing",
    priority: "High",
    icon: "megaphone",
    title: "Launch User-Generated Content Campaign",
    description: "Leverage your high food quality scores by encouraging customers to share their dining experiences on social media with a branded hashtag.",
    impact: "Expected 25% increase in social media engagement and 15% increase in new customer acquisition",
    timeline: "2-4 weeks",
    steps: [
      "Create branded hashtag #GoldenForkMoments",
      "Offer 10% discount for customers who post with hashtag",
      "Feature best posts on restaurant social channels",
      "Partner with 3-5 micro-influencers for launch"
    ]
  },
  {
    id: 2,
    category: "Operations",
    priority: "High",
    icon: "clock",
    title: "Implement Smart Table Management",
    description: "Address wait time complaints by implementing a modern reservation and table management system with real-time updates.",
    impact: "Reduce wait time complaints by 40% and improve table turnover efficiency by 20%",
    timeline: "4-6 weeks",
    steps: [
      "Research and select table management software",
      "Train staff on new system",
      "Implement SMS notification for table readiness",
      "Set up real-time wait time display"
    ]
  },
  {
    id: 3,
    category: "Pricing",
    priority: "Medium",
    icon: "dollar",
    title: "Value Perception Enhancement",
    description: "Combat negative price perception by creating value-focused menu options and communicating the quality behind pricing.",
    impact: "Improve price sentiment by 30% and increase average check by 12%",
    timeline: "3-4 weeks",
    steps: [
      "Introduce prix fixe lunch menu at accessible price point",
      "Add 'Chef's Story' cards explaining ingredient sourcing",
      "Create weekend brunch specials",
      "Train servers on value-focused upselling"
    ]
  },
  {
    id: 4,
    category: "PR",
    priority: "Medium",
    icon: "newspaper",
    title: "Proactive Review Response Program",
    description: "Establish a systematic approach to responding to all reviews, especially negative ones, within 24 hours.",
    impact: "Increase response rate to 95% and improve overall rating by 0.2 stars",
    timeline: "1-2 weeks",
    steps: [
      "Create response templates for common scenarios",
      "Assign daily review monitoring responsibilities",
      "Set up alerts for negative reviews",
      "Track response metrics weekly"
    ]
  },
  {
    id: 5,
    category: "Growth",
    priority: "Low",
    icon: "trending-up",
    title: "Corporate Partnership Program",
    description: "Develop B2B relationships with nearby offices for regular corporate dining and event catering.",
    impact: "Generate additional revenue stream of $15-20k monthly",
    timeline: "6-8 weeks",
    steps: [
      "Identify top 20 corporate offices within 1 mile",
      "Create corporate packages and pricing",
      "Develop outreach materials",
      "Schedule introductory meetings"
    ]
  }
]

// ── SWOT Analysis Data ──────────────────────────────────────────
export type SwotItem = {
  text: string
  confidence: "High" | "Medium" | "Low"
  platform: string
  sourceText: string
  sourceUrl: string
}

export const swotData: Record<"strengths" | "weaknesses" | "opportunities" | "threats", SwotItem[]> = {
  strengths: [
    { text: "Signature truffle risotto consistently rated best-in-class across all review platforms", confidence: "High", platform: "Google Maps", sourceText: "The truffle risotto here is absolutely divine — the best I've had in NYC. Rich, perfectly seasoned, and worth every penny.", sourceUrl: "#" },
    { text: "Premium ambiance and interior design generates organic social mentions", confidence: "High", platform: "Twitter", sourceText: "This place is so photogenic! The lighting and decor are stunning. #GoldenForkNYC", sourceUrl: "#" },
    { text: "Chef's farm-to-table positioning attracts high-value food critic coverage", confidence: "High", platform: "NY Times", sourceText: "Chef's commitment to hyper-local sourcing elevates every dish beyond mere fine dining.", sourceUrl: "#" },
    { text: "Creative cocktail and wine program differentiates from key competitors", confidence: "Medium", platform: "Google Maps", sourceText: "The sommelier recommendations were spot-on and the cocktail menu is inventive without being gimmicky.", sourceUrl: "#" },
    { text: "Sunday brunch offering drives repeat visits and new customer acquisition", confidence: "Medium", platform: "Twitter", sourceText: "Best brunch in the neighborhood by far. We come every few weeks and always bring friends.", sourceUrl: "#" },
  ],
  weaknesses: [
    { text: "Long wait times during peak hours leading to customer frustration", confidence: "High", platform: "Twitter", sourceText: "Waited 45 minutes even with a reservation on Friday night. Management needs to get this under control.", sourceUrl: "#" },
    { text: "Delivery experience is poor — cold food, late arrivals, packaging issues", confidence: "High", platform: "Twitter", sourceText: "Food arrived cold and 30 minutes late. Great dine-in experience but delivery is not worth it.", sourceUrl: "#" },
    { text: "Inconsistency in food quality across visits reported by repeat customers", confidence: "Medium", platform: "Google Maps", sourceText: "First visit was magical, second visit the same dish was noticeably worse. Needs more consistency.", sourceUrl: "#" },
    { text: "Limited parking availability reduces accessibility for non-transit customers", confidence: "Medium", platform: "Reddit", sourceText: "Great food but parking nearby is a nightmare. Lost 20 mins circling the block.", sourceUrl: "#" },
    { text: "Service staff attitude issues escalating in recent negative reviews", confidence: "Low", platform: "Yelp", sourceText: "Our waiter seemed annoyed the whole time. Felt like we were bothering him.", sourceUrl: "#" },
  ],
  opportunities: [
    { text: "Growing demand for chef's table and private dining experiences in NYC", confidence: "High", platform: "Market Research", sourceText: "NYC fine dining reservations for private events are up 34% YoY — high willingness to pay for exclusivity.", sourceUrl: "#" },
    { text: "Expand corporate catering to capitalize on Midtown office return", confidence: "High", platform: "Industry Report", sourceText: "NYC office occupancy is at 75% and corporate lunch/event spend is recovering strongly.", sourceUrl: "#" },
    { text: "Launch branded meal kits to capture at-home premium dining trend", confidence: "Medium", platform: "TrendData", sourceText: "Premium at-home dining kits from restaurants are growing at 22% annually in major metros.", sourceUrl: "#" },
    { text: "Untapped TikTok food content potential — competitor restaurants gaining viral traction", confidence: "Medium", platform: "Social Analysis", sourceText: "Peer restaurants in NYC are getting 500K-2M views per food video. Golden Fork has zero TikTok presence.", sourceUrl: "#" },
  ],
  threats: [
    { text: "Three new upscale competitors opening within 0.5 miles in Q2 2026", confidence: "High", platform: "Local News", sourceText: "NYC restaurant boom: Three fine dining spots set to open in the area by April 2026, intensifying competition.", sourceUrl: "#" },
    { text: "Food cost inflation eroding margins — beef and seafood up 18% YoY", confidence: "High", platform: "Industry Report", sourceText: "Restaurant food costs hit a 5-year high in Q1 2026, with protein categories up 15-22% annually.", sourceUrl: "#" },
    { text: "Social feed algorithm changes reducing organic discovery visibility", confidence: "Medium", platform: "Twitter", sourceText: "Restaurant owners in NYC report a 25% drop in organic profile views since the latest feed update.", sourceUrl: "#" },
    { text: "Rising minimum wage in NYC tightening labor cost structure", confidence: "Medium", platform: "Policy Watch", sourceText: "NYC minimum wage set to increase to $18/hr by end of 2026, adding pressure to hospitality operating costs.", sourceUrl: "#" },
  ]
}

// ── PESTEL Analysis Data ────────────────────────────────────────
export type PestelItem = {
  factor: string
  impact: "Positive" | "Negative" | "Neutral"
  severity: "High" | "Medium" | "Low"
  description: string
  implication: string
}

export const pestelData: Record<string, { label: string; color: string; items: PestelItem[] }> = {
  political: { label: "Political", color: "hsl(213 93% 68%)", items: [
    { factor: "NYC Health Code Reforms", impact: "Neutral", severity: "Medium", description: "New NYC health inspection standards effective Q3 2026 require digital record keeping.", implication: "Invest in compliance software to avoid penalties and maintain Grade A." },
    { factor: "Outdoor Dining Permits", impact: "Positive", severity: "Medium", description: "City extending sidewalk cafe permits through 2028 following pandemic-era success.", implication: "Expand outdoor seating capacity to increase covers without renovation cost." },
  ]},
  economic: { label: "Economic", color: "hsl(38 82% 58%)", items: [
    { factor: "Food Cost Inflation", impact: "Negative", severity: "High", description: "Beef, seafood, and dairy costs up 15-22% YoY in metro markets.", implication: "Renegotiate supplier contracts and introduce seasonal menu flexibility to manage margin." },
    { factor: "Rising Disposable Income", impact: "Positive", severity: "Medium", description: "NYC household incomes growing 4.2% annually, strengthening premium dining spend.", implication: "Fine dining positioning remains strong — lean into premium experiences." },
    { factor: "Minimum Wage Increases", impact: "Negative", severity: "High", description: "NYC minimum wage rising to $18/hr by end of 2026.", implication: "Model labor cost scenarios and evaluate service charge models." },
  ]},
  social: { label: "Social", color: "hsl(142 69% 58%)", items: [
    { factor: "Farm-to-Table Movement", impact: "Positive", severity: "High", description: "72% of NYC diners now actively research ingredient sourcing before choosing a restaurant.", implication: "Amplify farm-to-table story across menus, social, and media partnerships." },
    { factor: "Health & Wellness Dining", impact: "Positive", severity: "Medium", description: "Growing demand for nutritionally conscious options in fine dining context.", implication: "Introduce a wellness-focused tasting menu with macro-nutritional callouts." },
    { factor: "Post-Pandemic Social Dining", impact: "Positive", severity: "Medium", description: "Large group and celebration dining recovering strongly — up 31% vs 2023.", implication: "Build private dining and celebration package offerings." },
  ]},
  technological: { label: "Technological", color: "hsl(30 6% 72%)", items: [
    { factor: "AI-Powered Review Platforms", impact: "Neutral", severity: "Medium", description: "Review aggregators increasingly using AI summaries that may distort nuanced feedback.", implication: "Monitor AI-generated summaries on key platforms and proactively respond to inaccuracies." },
    { factor: "Digital Ordering & POS", impact: "Positive", severity: "Medium", description: "Next-gen POS systems offering real-time inventory and demand forecasting.", implication: "Upgrade to integrated POS to reduce waste and improve kitchen efficiency." },
  ]},
  environmental: { label: "Environmental", color: "hsl(162 69% 48%)", items: [
    { factor: "Single-Use Plastic Bans", impact: "Neutral", severity: "Low", description: "NYC expanding single-use plastics ban to include more food service categories in 2026.", implication: "Audit packaging and transition to compostable alternatives — communicate as brand value." },
    { factor: "Local Sourcing Mandates", impact: "Positive", severity: "Low", description: "Tax incentives for restaurants sourcing 30%+ ingredients from NY State farms.", implication: "Document local sourcing % and apply for available tax credits." },
  ]},
  legal: { label: "Legal", color: "hsl(30 6% 55%)", items: [
    { factor: "Tipping Transparency Laws", impact: "Neutral", severity: "Medium", description: "New York requiring clear disclosure of service charges and tip pooling policies.", implication: "Update menus and digital ordering flows to include transparent service charge disclosure." },
    { factor: "Allergen Labeling Requirements", impact: "Neutral", severity: "High", description: "FDA expanding allergen labeling requirements for restaurant menus effective 2026.", implication: "Conduct full menu allergen audit and update all print/digital menus accordingly." },
  ]}
}

// ── 4 P's Framework Data ────────────────────────────────────────
export const fourPsData = {
  product: { score: 88, summary: "Strong product differentiation through premium ingredients and chef-led innovation. Signature dishes drive loyalty.", highlights: ["Truffle risotto and wagyu steak are category leaders in sentiment score (4.8-4.9/5)", "Seasonal rotating menu creates urgency and repeat visits", "Farm-to-table sourcing story gives authentic premium positioning", "Cocktail and wine program supports premium check average"], gaps: ["Delivery product experience is poor — packaging doesn't maintain quality", "Vegan/plant-based offering underdeveloped vs market demand"] },
  price: { score: 62, summary: "Pricing is premium but perception gap exists — customers feel value doesn't always match price point.", highlights: ["Price positioning correctly targets affluent NYC diner segment", "Chef's tasting menu provides anchor for daily a la carte pricing", "Wine program pricing in line with comparable fine dining"], gaps: ["50% of price-related reviews carry negative sentiment", "Lunch offering lacks accessible entry point for new customers", "Portion sizes flagged in 23% of value-related comments"] },
  place: { score: 74, summary: "Prime location with strong foot traffic and transit access. Physical ambiance is a competitive strength.", highlights: ["Location generates organic walk-in traffic from neighborhood foot traffic", "Interior design cited as a reason to visit by 28% of reviewers", "Close to transit improves accessibility for non-driving diners"], gaps: ["No dedicated parking — limits suburban and outer-borough visitors", "Delivery radius is limited and experience is subpar", "Online presence (Twitter, Google) photos are outdated"] },
  promotion: { score: 57, summary: "Offline presence is strong but digital and social media strategy is significantly underdeveloped.", highlights: ["Media coverage in NYT Food and Eater NY drives awareness", "Strong word-of-mouth with 40% of new customers via referral", "Chef's personal brand adds credibility"], gaps: ["No TikTok presence despite viral potential of food content", "Twitter posts averaging 3x lower engagement than competitor set", "Email marketing list underutilized — last campaign was 4 months ago", "Zero paid social media advertising"] }
}

export type InsightsPayload = {
  business_info?: {
    name?: string
    address?: string
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

export function applyInsightsToDashboard(payload: InsightsPayload) {
  const positive = Math.round(payload.sentiment_breakdown?.positive ?? 0)
  const neutral = Math.round(payload.sentiment_breakdown?.neutral ?? 0)
  const negative = Math.round(payload.sentiment_breakdown?.negative ?? 0)

  if (payload.business_info?.name) businessInfo.name = payload.business_info.name
  if (payload.business_info?.address) businessInfo.address = payload.business_info.address
  if (typeof payload.summary_stats?.avg_rating === "number") {
    businessInfo.rating = Number(payload.summary_stats.avg_rating.toFixed(2))
  }
  if (typeof payload.summary_stats?.total_reviews === "number") {
    businessInfo.total_ratings = payload.summary_stats.total_reviews
    businessInfo.reviews_analyzed = payload.summary_stats.total_reviews
  }
  if (typeof payload.summary_stats?.media_mentions === "number") {
    businessInfo.mediaMentions = payload.summary_stats.media_mentions
  }
  if (typeof payload.summary_stats?.overall_confidence === "number") {
    businessInfo.confidenceScore = Math.round(payload.summary_stats.overall_confidence)
  }
  businessInfo.lastUpdated = new Date().toISOString()

  sentimentAnalysis.overall_sentiment = {
    sentiment: positive >= negative ? "Positive" : "Negative",
    positive_percentage: positive,
    negative_percentage: negative,
    neutral_percentage: neutral,
  }

  const aspectsTarget = sentimentAnalysis.aspects as unknown as Record<string, {
    total_mentions: number
    sentiment_breakdown: { Positive: number; Negative: number; Neutral: number }
    average_confidence: number
    overall_sentiment: string
  }>

  for (const key of Object.keys(aspectsTarget)) {
    delete aspectsTarget[key]
  }

  for (const item of payload.aspect_sentiment ?? []) {
    const mentions = item.mention_count ?? 0
    const p = item.overall_sentiment === "Positive" ? mentions : 0
    const n = item.overall_sentiment === "Negative" ? mentions : 0
    const u = item.overall_sentiment === "Neutral" ? mentions : 0
    aspectsTarget[item.aspect] = {
      total_mentions: mentions,
      sentiment_breakdown: { Positive: p, Negative: n, Neutral: u },
      average_confidence: Number(item.confidence_score.toFixed(2)),
      overall_sentiment: item.overall_sentiment,
    }
  }

  const trend = (payload.review_volume_trend ?? []).map((row) => {
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
  if (trend.length > 0) {
    reviewVolumeData.splice(0, reviewVolumeData.length, ...trend)
  }

  const sourceEntries = Object.entries(payload.source_breakdown ?? {})
  const totalCount = sourceEntries.reduce((sum, [, value]) => {
    const count = Number((value.review_count as number) ?? (value.article_count as number) ?? 0)
    return sum + (Number.isFinite(count) ? count : 0)
  }, 0)
  const mappedSources = sourceEntries
    .map(([source, value]) => {
      const count = Number((value.review_count as number) ?? (value.article_count as number) ?? 0)
      const percentage = totalCount > 0 ? Math.round((count / totalCount) * 100) : 0
      return { source: titleCase(source), count, percentage }
    })
    .filter((row) => row.count > 0)
  if (mappedSources.length > 0) {
    sourceBreakdownData.splice(0, sourceBreakdownData.length, ...mappedSources)
  }

  if ((payload.top_keywords ?? []).length > 0) {
    const tops = payload.top_keywords ?? []
    bcgMatrixData.stars = tops.slice(0, 3).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 4.7 }))
    bcgMatrixData.cashCows = tops.slice(3, 6).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 4.3 }))
    bcgMatrixData.questionMarks = tops.slice(6, 8).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 3.8 }))
    bcgMatrixData.dogs = tops.slice(8, 10).map((x) => ({ name: x.keyword, mentions: x.count, sentimentAvg: 3.0 }))
  }
}
