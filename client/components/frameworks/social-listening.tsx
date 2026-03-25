"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { TrendingUp, TrendingDown, Minus, ExternalLink, Users, Hash } from "lucide-react"
import { socialListeningData } from "@/lib/mock-data"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts"

export function SocialListening() {
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up": return <TrendingUp className="h-4 w-4 text-chart-2" />
      case "down": return <TrendingDown className="h-4 w-4 text-chart-3" />
      default: return <Minus className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "up": return "text-chart-2"
      case "down": return "text-chart-3"
      default: return "text-muted-foreground"
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "Positive": return "bg-chart-2/20 text-chart-2"
      case "Negative": return "bg-chart-3/20 text-chart-3"
      default: return "bg-chart-4/20 text-chart-4"
    }
  }

  const totalMentions = socialListeningData.sources.reduce((acc, s) => acc + s.mentions, 0)
  const totalInfluencers = Object.values(socialListeningData.influencerMentions).reduce((a, b) => a + b, 0)

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Total Mentions</p>
            <p className="mt-2 text-3xl font-bold text-foreground">{totalMentions}</p>
            <p className="mt-1 text-sm text-chart-2">Across all platforms</p>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Active Platforms</p>
            <p className="mt-2 text-3xl font-bold text-foreground">{socialListeningData.sources.length}</p>
            <p className="mt-1 text-sm text-muted-foreground">Social networks tracked</p>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Influencer Mentions</p>
            <p className="mt-2 text-3xl font-bold text-foreground">{totalInfluencers}</p>
            <p className="mt-1 text-sm text-muted-foreground">Verified accounts</p>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Trending Topics</p>
            <p className="mt-2 text-3xl font-bold text-foreground">{socialListeningData.trendingTopics.length}</p>
            <p className="mt-1 text-sm text-muted-foreground">Active hashtags</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Platform Breakdown */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle>Platform Mentions</CardTitle>
            <CardDescription>Weekly mention breakdown by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={socialListeningData.sources} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  width={80} 
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
                <Bar dataKey="mentions" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
            
            <div className="mt-4 space-y-2">
              {socialListeningData.sources.map((source, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div 
                      className="h-3 w-3 rounded-full" 
                      style={{ backgroundColor: source.color }}
                    />
                    <span className="text-foreground">{source.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {getTrendIcon(source.trend)}
                    <span className={getTrendColor(source.trend)}>
                      {source.change > 0 ? '+' : ''}{source.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Trending Topics */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-5 w-5" />
              Trending Topics
            </CardTitle>
            <CardDescription>Popular hashtags and topics this week</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {socialListeningData.trendingTopics.map((topic, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between rounded-lg bg-secondary/50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-bold text-muted-foreground">
                      #{index + 1}
                    </span>
                    <div>
                      <p className="font-medium text-primary">{topic.tag}</p>
                      <p className="text-sm text-muted-foreground">
                        {topic.count} mentions
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {topic.change > 0 ? (
                      <TrendingUp className="h-4 w-4 text-chart-2" />
                    ) : topic.change < 0 ? (
                      <TrendingDown className="h-4 w-4 text-chart-3" />
                    ) : (
                      <Minus className="h-4 w-4 text-muted-foreground" />
                    )}
                    <span className={`text-sm font-medium ${
                      topic.change > 0 ? 'text-chart-2' : topic.change < 0 ? 'text-chart-3' : 'text-muted-foreground'
                    }`}>
                      {topic.change > 0 ? '+' : ''}{topic.change}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Influencer Breakdown */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Influencer Mentions by Follower Count
          </CardTitle>
          <CardDescription>Breakdown of mentions by account size</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-3">
            {Object.entries(socialListeningData.influencerMentions).map(([bracket, count]) => (
              <div 
                key={bracket}
                className="rounded-lg border border-border p-4 text-center"
              >
                <p className="text-3xl font-bold text-foreground">{count}</p>
                <p className="mt-1 text-sm text-muted-foreground">{bracket} followers</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Mentions Table */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle>Recent Mentions</CardTitle>
          <CardDescription>Latest social media mentions across platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Source</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Content</TableHead>
                  <TableHead>Sentiment</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {socialListeningData.recentMentions.map((mention, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Badge variant="outline">{mention.source}</Badge>
                    </TableCell>
                    <TableCell className="font-medium text-primary">
                      {mention.user}
                    </TableCell>
                    <TableCell className="max-w-[300px]">
                      <p className="line-clamp-2 text-sm">{mention.text}</p>
                    </TableCell>
                    <TableCell>
                      <Badge className={getSentimentColor(mention.sentiment)}>
                        {mention.sentiment}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {mention.date}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
