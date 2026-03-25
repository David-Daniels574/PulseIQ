"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Newspaper, ExternalLink, TrendingUp, TrendingDown, Minus,
  RefreshCw, Hash, AlertCircle, RotateCcw,
} from "lucide-react"
import { useDashboardData } from "@/hooks/use-dashboard-data"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, ReferenceLine,
} from "recharts"

// ── Skeleton ──────────────────────────────────────────────────────
function SkeletonBlock({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-secondary/60 ${className}`} />
}

function ForecastSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="border-border/50">
            <CardContent className="p-6 space-y-3">
              <SkeletonBlock className="h-3 w-24" />
              <SkeletonBlock className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card className="border-border/50">
        <CardContent className="p-6">
          <SkeletonBlock className="h-[350px] w-full" />
        </CardContent>
      </Card>
      <Card className="border-border/50">
        <CardContent className="p-6 space-y-4">
          {[...Array(5)].map((_, i) => (
            <SkeletonBlock key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────
export function MarketIntelligence() {
  const {
    forecastData,
    marketIntelligence,
    isMarketLoading,
    marketIntelligenceError,
    onRetryMarketIntelligence,
  } = useDashboardData()
  const { forecast_data, summary } = forecastData

  // Full-page skeleton on first load
  if (isMarketLoading && forecast_data.length === 0 && !marketIntelligenceError) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          Fetching market intelligence &amp; XGBoost forecast — this takes ~30–60 s…
        </div>
        <ForecastSkeleton />
      </div>
    )
  }

  // Error state — show retry button
  if (marketIntelligenceError && forecast_data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
        <AlertCircle className="h-10 w-10 text-destructive opacity-60" />
        <div>
          <p className="font-medium text-foreground">Market intelligence failed to load</p>
          <p className="mt-1 max-w-sm text-sm text-muted-foreground">{marketIntelligenceError}</p>
        </div>
        <Button variant="outline" className="gap-2" onClick={onRetryMarketIntelligence}>
          <RotateCcw className="h-4 w-4" />
          Retry
        </Button>
      </div>
    )
  }

  // Helpers
  const getTrendIcon = (trend: string) => {
    if (trend === "improving") return <TrendingUp className="h-4 w-4 text-chart-2" />
    if (trend === "declining") return <TrendingDown className="h-4 w-4 text-chart-3" />
    return <Minus className="h-4 w-4 text-muted-foreground" />
  }

  const getTrendColor = (trend: string) => {
    if (trend === "improving") return "bg-chart-2/20 text-chart-2"
    if (trend === "declining") return "bg-chart-3/20 text-chart-3"
    return "bg-muted text-muted-foreground"
  }

  const allValues = forecast_data.flatMap((d) =>
    [d.forecast, d.actual].filter((v): v is number => v !== null),
  )
  const yMin = allValues.length ? Math.max(1, Math.floor((Math.min(...allValues) - 0.1) * 10) / 10) : 1
  const yMax = allValues.length ? Math.min(5, Math.ceil((Math.max(...allValues) + 0.1) * 10) / 10) : 5
  const changeSign = (summary.rating_change ?? 0) >= 0 ? "+" : ""

  return (
    <div className="space-y-6">
      {/* Refreshing-over-old-data banner */}
      {isMarketLoading && (
        <div className="flex items-center gap-2 rounded-md border border-border/50 bg-secondary/30 px-4 py-2 text-sm text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          Updating market intelligence data…
        </div>
      )}

      {/* Partial error banner */}
      {marketIntelligenceError && forecast_data.length > 0 && (
        <div className="flex items-center justify-between gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-2 text-sm text-destructive">
          <span className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {marketIntelligenceError}
          </span>
          <Button size="sm" variant="outline" className="gap-1 shrink-0" onClick={onRetryMarketIntelligence}>
            <RotateCcw className="h-3 w-3" /> Retry
          </Button>
        </div>
      )}

      {/* ── Forecast Summary Cards ─── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Current Rating</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {summary.current_rating > 0 ? summary.current_rating.toFixed(2) : "—"}
            </p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Predicted Rating</p>
            <p className="mt-2 text-3xl font-bold text-primary">
              {summary.predicted_rating > 0 ? summary.predicted_rating.toFixed(2) : "—"}
            </p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Expected Change</p>
            <div className="mt-2 flex items-center gap-2">
              <span className={`text-3xl font-bold ${(summary.rating_change ?? 0) >= 0 ? "text-chart-2" : "text-chart-3"}`}>
                {changeSign}{(summary.rating_change ?? 0).toFixed(2)}
              </span>
              <span className="text-sm text-muted-foreground">
                ({changeSign}{(summary.percentage_change ?? 0).toFixed(1)}%)
              </span>
            </div>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Trend &amp; Confidence</p>
            <div className="mt-2 flex items-center gap-2">
              <Badge className={getTrendColor(summary.trend)}>{summary.trend}</Badge>
              <Badge variant="outline" className="capitalize">{summary.confidence}</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ── Forecast Chart ─── */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle>Star Rating Forecast</CardTitle>
          <CardDescription>
            XGBoost ML model predictions for the next {forecast_data.length} months
          </CardDescription>
        </CardHeader>
        <CardContent>
          {forecast_data.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={forecast_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis
                    domain={[yMin, yMax]}
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickFormatter={(v: number) => v.toFixed(1)}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                    formatter={(value: number) => value.toFixed(2)}
                  />
                  <Legend />
                  {summary.current_rating > 0 && (
                    <ReferenceLine
                      y={summary.current_rating}
                      stroke="hsl(var(--muted-foreground))"
                      strokeDasharray="5 5"
                      label={{ value: "Current", position: "right", fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                    />
                  )}
                  <Line type="monotone" dataKey="actual" name="Actual"
                    stroke="hsl(var(--chart-2))" strokeWidth={3}
                    dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2 }} connectNulls={false} />
                  <Line type="monotone" dataKey="forecast" name="Forecast"
                    stroke="hsl(var(--primary))" strokeWidth={2} strokeDasharray="5 5"
                    dot={{ fill: "hsl(var(--primary))", strokeWidth: 2 }} />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 flex items-center justify-center gap-2">
                {getTrendIcon(summary.trend)}
                <span className="text-sm text-muted-foreground">
                  Rating is <span className="font-medium text-foreground">{summary.trend}</span> with {summary.confidence} confidence
                </span>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center gap-3 h-[350px] text-muted-foreground">
              <p className="text-sm">No forecast data available.</p>
              <Button variant="outline" size="sm" className="gap-2" onClick={onRetryMarketIntelligence} disabled={isMarketLoading}>
                <RotateCcw className="h-4 w-4" /> Fetch Forecast
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── News & Intelligence ─── */}
      <Card className="border-border/50">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5" />
              Market Intelligence News
            </CardTitle>
            <CardDescription>
              Industry-level news and trends · <span className="font-medium">{marketIntelligence.media_visibility}</span> media visibility
            </CardDescription>
          </div>
          {!isMarketLoading && (
            <Button variant="outline" size="sm" className="gap-2" onClick={onRetryMarketIntelligence}>
              <RefreshCw className="h-4 w-4" /> Refresh
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {/* Stats */}
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-secondary/50 p-4">
              <p className="text-sm text-muted-foreground">Total Articles</p>
              <p className="mt-1 text-2xl font-bold text-foreground">{marketIntelligence.total_articles}</p>
            </div>
            <div className="rounded-lg bg-secondary/50 p-4">
              <p className="text-sm text-muted-foreground">Media Visibility</p>
              <Badge className={`mt-2 ${
                marketIntelligence.media_visibility === "High"
                  ? "bg-chart-2/20 text-chart-2"
                  : marketIntelligence.media_visibility === "Medium"
                  ? "bg-chart-5/20 text-chart-5"
                  : "bg-muted text-muted-foreground"
              }`}>
                {marketIntelligence.media_visibility}
              </Badge>
            </div>
            <div className="rounded-lg bg-secondary/50 p-4">
              <p className="text-sm text-muted-foreground">Top Sources</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {marketIntelligence.top_sources.slice(0, 3).map((s, i) => (
                  <Badge key={i} variant="outline" className="text-xs">{s.source}</Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Trending keywords */}
          {marketIntelligence.trend_topics?.length > 0 && (
            <div className="mb-6">
              <p className="mb-2 text-sm font-medium text-muted-foreground">Trending Keywords</p>
              <div className="flex flex-wrap gap-2">
                {marketIntelligence.trend_topics.map((t, i) => (
                  <Badge key={i} variant="secondary" className="flex items-center gap-1 text-xs">
                    <Hash className="h-3 w-3" />
                    {t.topic}
                    <span className="ml-1 opacity-60">×{t.count}</span>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Articles */}
          {marketIntelligence.articles.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground">
              <Newspaper className="h-8 w-8 opacity-30" />
              <p className="text-sm">No articles found. Try refreshing.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {marketIntelligence.articles.map((article, index) => (
                <div
                  key={index}
                  className="flex items-start justify-between gap-4 rounded-lg border border-border p-4 transition-colors hover:bg-secondary/30"
                >
                  <div className="flex-1 min-w-0">
                    <a
                      href={article.link}
                      className="font-medium text-foreground hover:text-primary hover:underline line-clamp-2"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {article.headline}
                    </a>
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                      <span className="font-medium">{article.source_name}</span>
                      {article.query && (
                        <Badge variant="outline" className="text-xs py-0 h-5">{article.query}</Badge>
                      )}
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" asChild className="shrink-0">
                    <a href={article.link} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
