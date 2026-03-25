"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star, MessageSquare, TrendingUp, Sparkles, Globe, ShieldCheck } from "lucide-react"
import {
  sentimentAnalysis,
  strategicInsights,
  businessInfo,
  reviewVolumeData,
  sourceBreakdownData,
} from "@/lib/mock-data"
import {
  PieChart, Pie, Cell,
  BarChart, Bar,
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts"

const TOOLTIP_STYLE = {
  backgroundColor: "hsl(var(--card))",
  border: "1px solid hsl(var(--border))",
  borderRadius: "8px",
  color: "hsl(var(--card-foreground))",
  fontSize: "12px",
}

const SOURCE_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--chart-3))",
]

export function OverallAnalysis() {
  const { overall_sentiment, aspects } = sentimentAnalysis

  const sentimentPieData = [
    { name: "Positive", value: overall_sentiment.positive_percentage,  color: "hsl(var(--chart-2))" },
    { name: "Negative", value: overall_sentiment.negative_percentage,  color: "hsl(var(--chart-3))" },
    { name: "Neutral",  value: overall_sentiment.neutral_percentage,   color: "hsl(var(--chart-4))" },
  ]

  const aspectData = Object.entries(aspects)
    .map(([name, data]) => ({
      name,
      mentions: data.total_mentions,
      sentiment: data.overall_sentiment,
    }))
    .sort((a, b) => b.mentions - a.mentions)

  const aspectSentimentData = Object.entries(aspects).map(([name, data]) => ({
    name,
    Positive: data.sentiment_breakdown.Positive,
    Negative: data.sentiment_breakdown.Negative,
    Neutral:  data.sentiment_breakdown.Neutral,
  }))

  return (
    <div className="space-y-6">

      {/* ── Key Metrics ─────────────────────────────────────────────────────── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <Card className="border-border/60">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-chart-4/15">
              <Star className="h-5 w-5 text-chart-4" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Overall Rating</p>
              <p className="text-2xl font-bold text-foreground font-serif">{businessInfo.rating}</p>
              <p className="text-xs text-muted-foreground">{businessInfo.total_ratings.toLocaleString()} total</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/15">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Reviews Analyzed</p>
              <p className="text-2xl font-bold text-foreground font-serif">{businessInfo.reviews_analyzed}</p>
              <p className="text-xs text-muted-foreground">last 90 days</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-chart-2/15">
              <TrendingUp className="h-5 w-5 text-chart-2" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Positive Sentiment</p>
              <p className="text-2xl font-bold text-foreground font-serif">{overall_sentiment.positive_percentage}%</p>
              <p className="text-xs text-muted-foreground">of all mentions</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-chart-5/15">
              <ShieldCheck className="h-5 w-5 text-chart-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Confidence Score</p>
              <p className="text-2xl font-bold text-foreground font-serif">{businessInfo.confidenceScore}%</p>
              <p className="text-xs text-muted-foreground">AI accuracy</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ── Sentiment Distribution + Aspect Mentions ────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2">

        {/* Sentiment Donut */}
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold">Sentiment Distribution</CardTitle>
            <CardDescription>Overall breakdown across all reviews</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={sentimentPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={62}
                  outerRadius={100}
                  paddingAngle={4}
                  dataKey="value"
                  label={({ name, value }) => `${name} ${value}%`}
                  labelLine={false}
                >
                  {sentimentPieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>
            {/* Legend */}
            <div className="mt-2 flex justify-center gap-5">
              {sentimentPieData.map((d) => (
                <div key={d.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  {d.name}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Aspects Horizontal Bar */}
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold">Top Mentioned Aspects</CardTitle>
            <CardDescription>Frequency of aspect mentions in reviews</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={aspectData} layout="vertical" margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
                <YAxis dataKey="name" type="category" width={76} stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Bar dataKey="mentions" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* ── Review Volume Trend ──────────────────────────────────────────────── */}
      <Card className="border-border/60">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold">Review Volume Trend</CardTitle>
          <CardDescription>Monthly review counts split by sentiment — last 10 months</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={reviewVolumeData} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="gradPos" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="hsl(var(--chart-2))" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gradNeg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="hsl(var(--chart-3))" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="hsl(var(--chart-3))" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gradNeu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="hsl(var(--chart-4))" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="hsl(var(--chart-4))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "12px" }} />
              <Area type="monotone" dataKey="positive" name="Positive" stroke="hsl(var(--chart-2))" fill="url(#gradPos)" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="neutral"  name="Neutral"  stroke="hsl(var(--chart-4))" fill="url(#gradNeu)" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="negative" name="Negative" stroke="hsl(var(--chart-3))" fill="url(#gradNeg)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* ── Source Breakdown + Aspect Sentiment ─────────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2">

        {/* Source Breakdown */}
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-primary" />
              <CardTitle className="text-base font-semibold">Review Source Breakdown</CardTitle>
            </div>
            <CardDescription>Distribution of {businessInfo.total_ratings.toLocaleString()} reviews by platform</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-2">
            {sourceBreakdownData.map((s, i) => (
              <div key={s.source} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-foreground">{s.source}</span>
                  <span className="text-muted-foreground">{s.count.toLocaleString()} <span className="text-xs">({s.percentage}%)</span></span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${s.percentage}%`,
                      backgroundColor: SOURCE_COLORS[i],
                    }}
                  />
                </div>
              </div>
            ))}
            {/* Mini donut in footer */}
            <div className="mt-4 flex items-center gap-3 flex-wrap">
              {sourceBreakdownData.map((s, i) => (
                <div key={s.source} className="flex items-center gap-1 text-[11px] text-muted-foreground">
                  <span className="h-2 w-2 rounded-full" style={{ backgroundColor: SOURCE_COLORS[i] }} />
                  {s.source}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Aspect Sentiment Stacked Bar */}
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold">Aspect-Level Sentiment</CardTitle>
            <CardDescription>Positive / Neutral / Negative by category</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={aspectSentimentData} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
                <Bar dataKey="Positive" stackId="a" fill="hsl(var(--chart-2))" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Neutral"  stackId="a" fill="hsl(var(--chart-4))" />
                <Bar dataKey="Negative" stackId="a" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* ── AI Strategic Insights ────────────────────────────────────────────── */}
      <Card className="border-primary/25 bg-primary/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <CardTitle className="text-base font-semibold">AI-Generated Strategic Insights</CardTitle>
          </div>
          <CardDescription>Powered by advanced sentiment analysis</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg bg-card p-4">
            <h4 className="mb-2 text-sm font-semibold text-foreground">Executive Summary</h4>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {strategicInsights.executive_summary}
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-card p-4">
              <h4 className="mb-3 flex items-center gap-1.5 text-sm font-semibold text-foreground">
                <span className="h-2 w-2 rounded-full bg-primary" />
                Marketing
              </h4>
              <ul className="space-y-2">
                {strategicInsights.marketing_recommendations.slice(0, 3).map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-lg bg-card p-4">
              <h4 className="mb-3 flex items-center gap-1.5 text-sm font-semibold text-foreground">
                <span className="h-2 w-2 rounded-full bg-chart-2" />
                Operations
              </h4>
              <ul className="space-y-2">
                {strategicInsights.operational_improvements.slice(0, 3).map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-chart-2" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-lg bg-card p-4">
              <h4 className="mb-3 flex items-center gap-1.5 text-sm font-semibold text-foreground">
                <span className="h-2 w-2 rounded-full bg-chart-4" />
                PR
              </h4>
              <ul className="space-y-2">
                {strategicInsights.pr_recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-chart-4" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

    </div>
  )
}
