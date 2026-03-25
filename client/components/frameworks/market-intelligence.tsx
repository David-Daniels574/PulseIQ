"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Newspaper, ExternalLink, TrendingUp, TrendingDown, Minus, Search, Clock } from "lucide-react"
import { forecastData, marketIntelligence } from "@/lib/mock-data"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from "recharts"
import { format } from "date-fns"

export function MarketIntelligence() {
  const { forecast_data, summary } = forecastData

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "improving":
        return <TrendingUp className="h-4 w-4 text-chart-2" />
      case "declining":
        return <TrendingDown className="h-4 w-4 text-chart-3" />
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "improving":
        return "bg-chart-2/20 text-chart-2"
      case "declining":
        return "bg-chart-3/20 text-chart-3"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <div className="space-y-6">
      {/* Forecast Summary Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Current Rating</p>
            <p className="mt-2 text-3xl font-bold text-foreground">{summary.current_rating}</p>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Predicted Rating</p>
            <p className="mt-2 text-3xl font-bold text-primary">{summary.predicted_rating}</p>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Expected Change</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-3xl font-bold text-chart-2">
                +{summary.rating_change}
              </span>
              <span className="text-sm text-muted-foreground">
                ({summary.percentage_change}%)
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Trend & Confidence</p>
            <div className="mt-2 flex items-center gap-2">
              <Badge className={getTrendColor(summary.trend)}>
                {summary.trend}
              </Badge>
              <Badge variant="outline" className="capitalize">
                {summary.confidence}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Star Rating Forecast Chart */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle>Star Rating Forecast</CardTitle>
          <CardDescription>
            XGBoost ML model predictions for the next 6 months
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={forecast_data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="month" 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={12}
              />
              <YAxis 
                domain={[4.2, 4.9]} 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={12}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))', 
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <ReferenceLine 
                y={summary.current_rating} 
                stroke="hsl(var(--muted-foreground))" 
                strokeDasharray="5 5"
                label={{ value: 'Current', position: 'right', fill: 'hsl(var(--muted-foreground))' }}
              />
              <Line 
                type="monotone" 
                dataKey="actual" 
                name="Actual"
                stroke="hsl(var(--chart-2))" 
                strokeWidth={3}
                dot={{ fill: 'hsl(var(--chart-2))', strokeWidth: 2 }}
                connectNulls={false}
              />
              <Line 
                type="monotone" 
                dataKey="forecast" 
                name="Forecast"
                stroke="hsl(var(--primary))" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-center gap-2">
            {getTrendIcon(summary.trend)}
            <span className="text-sm text-muted-foreground">
              Rating is <span className="font-medium text-foreground">{summary.trend}</span> with {summary.confidence} confidence
            </span>
          </div>
        </CardContent>
      </Card>

      {/* News Section */}
      <Card className="border-border/50">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5" />
              Market Intelligence News
            </CardTitle>
            <CardDescription>
              Recent news mentions and media coverage
            </CardDescription>
          </div>
          <Button variant="outline" className="gap-2">
            <Search className="h-4 w-4" />
            Scan News
          </Button>
        </CardHeader>
        <CardContent>
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-secondary/50 p-4">
              <p className="text-sm text-muted-foreground">Total Articles</p>
              <p className="mt-1 text-2xl font-bold text-foreground">
                {marketIntelligence.total_articles_found}
              </p>
            </div>
            <div className="rounded-lg bg-secondary/50 p-4">
              <p className="text-sm text-muted-foreground">Media Visibility</p>
              <Badge className="mt-2 bg-chart-2/20 text-chart-2">
                {marketIntelligence.media_visibility}
              </Badge>
            </div>
            <div className="rounded-lg bg-secondary/50 p-4">
              <p className="text-sm text-muted-foreground">Top Sources</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {Object.keys(marketIntelligence.top_sources).slice(0, 3).map((source, i) => (
                  <Badge key={i} variant="outline" className="text-xs">
                    {source}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {marketIntelligence.articles.map((article, index) => (
              <div 
                key={index}
                className="flex items-start justify-between gap-4 rounded-lg border border-border p-4 transition-colors hover:bg-secondary/30"
              >
                <div className="flex-1">
                  <a 
                    href={article.link} 
                    className="font-medium text-foreground hover:text-primary hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {article.headline}
                  </a>
                  <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{article.source_name}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {format(new Date(article.date), "MMM d, yyyy")}
                    </span>
                  </div>
                </div>
                <Button variant="ghost" size="icon" asChild>
                  <a href={article.link} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
