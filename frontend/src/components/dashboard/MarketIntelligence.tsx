import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { TrendingUp, Newspaper, Calendar, Loader2, AlertCircle, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { fetchMarketIntelligence, fetchRatingForecast, ForecastResponse } from "@/lib/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

interface MarketIntelligenceProps {
  businessName: string;
  businessLocation?: string;
  businessCategory?: string;
  currentRating?: number;
  sentimentScore?: number;
}

interface Article {
  headline: string;
  link: string;
  source_name: string;
}

interface MarketIntelligenceData {
  status: string;
  business_name: string;
  location: string;
  total_articles_found: number;
  articles_stored_in_db: number;
  queries_searched: string[];
  results: Record<string, { article_count: number; articles: Article[] }>;
  insights: {
    main_business_mentions: number;
    competitor_mentions: number;
    top_sources: Record<string, number>;
    media_visibility: string;
  };
  execution_time_ms: number;
  scraped_at: string;
}



const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case "positive":
      return "bg-success text-success-foreground";
    case "negative":
      return "bg-destructive text-destructive-foreground";
    default:
      return "bg-info text-info-foreground";
  }
};

const MarketIntelligence = ({ 
  businessName, 
  businessLocation = "Mumbai",
  businessCategory = "Restaurant",
  currentRating = 4.3,
  sentimentScore = 0.75
}: MarketIntelligenceProps) => {
  const [data, setData] = useState<MarketIntelligenceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastError, setForecastError] = useState<string | null>(null);

  const loadForecast = async () => {
    try {
      setForecastLoading(true);
      setForecastError(null);

      const response = await fetchRatingForecast({
        business_name: businessName,
        city: businessLocation,
        category: businessCategory,
        current_rating: currentRating,
        sentiment_score: sentimentScore,
        months_ahead: 6
      });

      setForecastData(response);
    } catch (err) {
      console.error('Error loading forecast:', err);
      setForecastError(err instanceof Error ? err.message : "Failed to load forecast");
    } finally {
      setForecastLoading(false);
    }
  };

  const loadMarketIntelligence = async () => {
    if (!businessName) {
      setError("Business name is required");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetchMarketIntelligence({
        business_name: businessName,
        location: businessLocation,
        include_competitors: false,
      });

      setData(response);
    } catch (err) {
      console.error('Error loading market intelligence:', err);
      setError(err instanceof Error ? err.message : "Failed to load market intelligence");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Auto-load forecast when component mounts
    if (businessName && currentRating && sentimentScore) {
      loadForecast();
    }
  }, [businessName, businessLocation, businessCategory, currentRating, sentimentScore]);

  // Extract articles for display
  const allArticles: (Article & { query: string })[] = [];
  if (data?.results) {
    Object.entries(data.results).forEach(([query, queryData]) => {
      queryData.articles.forEach((article) => {
        allArticles.push({ ...article, query });
      });
    });
  }

  // Generate visibility data from insights
  const visibilityData = data?.insights
    ? [
        { month: "Current", mentions: data.insights.main_business_mentions },
      ]
    : [];

  return (
    <>
      {/* Star Rating Forecast */}
      <Card className="shadow-soft">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Star Rating Forecast
              </CardTitle>
              <CardDescription>XGBoost ML model prediction based on sentiment and market trends</CardDescription>
            </div>
            {forecastError && (
              <Button onClick={loadForecast} size="sm" variant="outline">
                Retry
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {forecastLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-12 w-12 animate-spin text-primary" />
            </div>
          )}

          {forecastError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{forecastError}</AlertDescription>
            </Alert>
          )}

          {!forecastLoading && !forecastError && forecastData && (
            <>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={forecastData.forecast_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                  <YAxis domain={[3.5, 5]} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "var(--radius)",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="hsl(var(--primary))"
                    strokeWidth={3}
                    name="Current Rating"
                    dot={{ fill: "hsl(var(--primary))", r: 5 }}
                    connectNulls={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="forecast"
                    stroke="hsl(var(--accent))"
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    name="Predicted Rating"
                    dot={{ fill: "hsl(var(--accent))", r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <p className="text-sm font-semibold mb-2">📊 Forecast Summary ({forecastData.model} Model)</p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Current Rating</p>
                    <p className="text-xl font-bold">{forecastData.summary.current_rating.toFixed(2)} ⭐</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Predicted Rating</p>
                    <p className="text-xl font-bold">{forecastData.summary.predicted_rating.toFixed(2)} ⭐</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Expected Change</p>
                    <p className={`text-xl font-bold ${forecastData.summary.rating_change >= 0 ? 'text-success' : 'text-destructive'}`}>
                      {forecastData.summary.rating_change >= 0 ? '+' : ''}{forecastData.summary.rating_change.toFixed(2)} ({forecastData.summary.percentage_change >= 0 ? '+' : ''}{forecastData.summary.percentage_change.toFixed(1)}%)
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Trend</p>
                    <Badge className={
                      forecastData.summary.trend === 'improving' ? 'bg-success' :
                      forecastData.summary.trend === 'declining' ? 'bg-destructive' : 'bg-info'
                    }>
                      {forecastData.summary.trend.charAt(0).toUpperCase() + forecastData.summary.trend.slice(1)}
                    </Badge>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Model inputs: {forecastData.city} • {forecastData.category} • Sentiment: {(forecastData.input_parameters.sentiment_score * 100).toFixed(0)}%
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Media Visibility Trend */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Newspaper className="h-5 w-5 text-secondary" />
            Media Visibility Trend
          </CardTitle>
          <CardDescription>Mentions across local news, blogs, and publications</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={visibilityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Area type="monotone" dataKey="mentions" stroke="hsl(var(--secondary))" fill="hsl(var(--secondary) / 0.3)" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* News & Market Intelligence */}
      <Card className="shadow-soft">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-info" />
                Recent Market Intelligence
              </CardTitle>
              <CardDescription>Latest mentions of your business from Google News scraping</CardDescription>
            </div>
            <Button onClick={loadMarketIntelligence} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Newspaper className="h-4 w-4 mr-2" />
                  Scan News
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
                <p className="text-muted-foreground">Scraping Google News for mentions...</p>
                <p className="text-sm text-muted-foreground">This may take 10-20 seconds</p>
              </div>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {!loading && !error && !data && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Newspaper className="h-16 w-16 text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-2">No market intelligence data yet</p>
              <p className="text-sm text-muted-foreground mb-4">Click "Scan News" to search for recent mentions</p>
            </div>
          )}

          {!loading && !error && data && (
            <>
              {/* Insights Summary */}
              <div className="mb-6 p-4 bg-muted rounded-lg space-y-2">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground">Total Articles</p>
                    <p className="text-2xl font-bold">{data.total_articles_found}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Your Mentions</p>
                    <p className="text-2xl font-bold">{data.insights.main_business_mentions}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Media Visibility</p>
                    <Badge
                      className={`text-xs ${
                        data.insights.media_visibility === "High"
                          ? "bg-success"
                          : data.insights.media_visibility === "Medium"
                          ? "bg-warning"
                          : "bg-muted"
                      }`}
                    >
                      {data.insights.media_visibility}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Sources</p>
                    <p className="text-2xl font-bold">{Object.keys(data.insights.top_sources).length}</p>
                  </div>
                </div>
              </div>

              {/* Articles List */}
              <div className="space-y-4">
                {allArticles.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No articles found for this business</p>
                    <p className="text-sm text-muted-foreground mt-2">Try searching for a more popular business or location</p>
                  </div>
                ) : (
                  allArticles.map((article, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-l-primary pl-4 py-2 hover:bg-muted/50 transition-colors rounded-r"
                    >
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div className="flex-1">
                          <a
                            href={article.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-semibold text-sm mb-1 hover:text-primary flex items-center gap-2"
                          >
                            {article.headline}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                          <div className="flex items-center gap-2 text-xs mt-2">
                            <span className="text-muted-foreground">{article.source_name}</span>
                            <span className="text-muted-foreground">•</span>
                            <Badge variant="outline" className="text-xs">
                              {article.query}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Scraped timestamp */}
              <div className="mt-4 text-xs text-muted-foreground text-center">
                Last scanned: {new Date(data.scraped_at).toLocaleString()} • Took {(data.execution_time_ms / 1000).toFixed(1)}s
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </>
  );
};

export default MarketIntelligence;
