"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Star, TrendingUp, TrendingDown, Minus, MapPin } from "lucide-react"
import { competitorData } from "@/lib/mock-data"
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
  Cell,
  ZAxis
} from "recharts"

export function CompetitorAnalysis() {
  const { main_business, competitors, competitive_analysis, aspect_showdown } = competitorData

  // Scatter plot data
  const scatterData = [
    {
      name: main_business.name,
      x: main_business.total_reviews,
      y: main_business.rating,
      z: 400,
      isMain: true
    },
    ...competitors.map(c => ({
      name: c.name,
      x: c.total_reviews,
      y: c.rating,
      z: 200,
      isMain: false
    }))
  ]

  const getPositionBadge = (rating: number) => {
    if (rating >= 4.6) return { label: "Leader", color: "bg-chart-2 text-chart-2" }
    if (rating >= 4.4) return { label: "Challenger", color: "bg-chart-4 text-chart-4" }
    return { label: "Follower", color: "bg-muted text-muted-foreground" }
  }

  return (
    <div className="space-y-6">
      {/* Market Position Summary */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Market Position</p>
            <div className="mt-2 flex items-center gap-2">
              <Badge className="bg-chart-2/20 text-chart-2 hover:bg-chart-2/30">
                {competitive_analysis.market_position}
              </Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Your Rating vs Average</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-2xl font-bold text-foreground">
                {competitive_analysis.your_rating_vs_average === "above" ? "+" : "-"}
                {competitive_analysis.rating_difference.toFixed(2)}
              </span>
              {competitive_analysis.your_rating_vs_average === "above" ? (
                <TrendingUp className="h-5 w-5 text-chart-2" />
              ) : (
                <TrendingDown className="h-5 w-5 text-chart-3" />
              )}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Avg Competitor Rating</p>
            <div className="mt-2 flex items-center gap-2">
              <Star className="h-5 w-5 fill-chart-4 text-chart-4" />
              <span className="text-2xl font-bold text-foreground">
                {competitive_analysis.average_competitor_rating.toFixed(2)}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">Avg Competitor Reviews</p>
            <p className="mt-2 text-2xl font-bold text-foreground">
              {competitive_analysis.average_competitor_reviews.toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Competitive Positioning Map */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle>Competitive Positioning Map</CardTitle>
            <CardDescription>Rating vs Review Volume - Your business highlighted</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="x" 
                  name="Reviews" 
                  type="number"
                  stroke="hsl(var(--muted-foreground))" 
                  fontSize={12}
                  label={{ value: 'Total Reviews', position: 'bottom', offset: -5 }}
                />
                <YAxis 
                  dataKey="y" 
                  name="Rating" 
                  type="number"
                  domain={[3.5, 5]}
                  stroke="hsl(var(--muted-foreground))" 
                  fontSize={12}
                  label={{ value: 'Rating', angle: -90, position: 'insideLeft' }}
                />
                <ZAxis dataKey="z" range={[100, 400]} />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))', 
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                  formatter={(value: number, name: string) => [
                    name === 'x' ? value.toLocaleString() : value.toFixed(1),
                    name === 'x' ? 'Reviews' : 'Rating'
                  ]}
                  labelFormatter={(_, payload) => payload[0]?.payload?.name || ''}
                />
                <Scatter data={scatterData}>
                  {scatterData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.isMain ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))'}
                      stroke={entry.isMain ? 'hsl(var(--primary))' : 'transparent'}
                      strokeWidth={entry.isMain ? 3 : 0}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            <div className="mt-4 flex items-center justify-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-primary" />
                <span className="text-muted-foreground">Your Business</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-muted-foreground" />
                <span className="text-muted-foreground">Competitors</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Aspect Showdown */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle>Aspect Showdown</CardTitle>
            <CardDescription>Your scores vs competitor average by category</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={aspect_showdown} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  type="number" 
                  domain={[0, 5]} 
                  stroke="hsl(var(--muted-foreground))" 
                  fontSize={12}
                />
                <YAxis 
                  dataKey="aspect" 
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
                <Legend />
                <Bar 
                  dataKey="your_score" 
                  name="Your Score" 
                  fill="hsl(var(--primary))" 
                  radius={[0, 4, 4, 0]}
                />
                <Bar 
                  dataKey="competitor_avg" 
                  name="Competitor Avg" 
                  fill="hsl(var(--muted-foreground))" 
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Competitor Table */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle>Detailed Competitor Comparison</CardTitle>
          <CardDescription>All competitors in your area ranked by rating</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Business Name</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Reviews</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="hidden md:table-cell">Category</TableHead>
                  <TableHead>Position</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow className="bg-primary/5">
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      {main_business.name}
                      <Badge variant="outline" className="text-xs">You</Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-chart-4 text-chart-4" />
                      {main_business.rating}
                    </div>
                  </TableCell>
                  <TableCell>{main_business.total_reviews.toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge className="bg-chart-2/20 text-chart-2">Open</Badge>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">Fine Dining</TableCell>
                  <TableCell>
                    <Badge className={`${getPositionBadge(main_business.rating).color} bg-opacity-20`}>
                      {getPositionBadge(main_business.rating).label}
                    </Badge>
                  </TableCell>
                </TableRow>
                {competitors
                  .sort((a, b) => b.rating - a.rating)
                  .map((competitor, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{competitor.name}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-chart-4 text-chart-4" />
                          {competitor.rating}
                        </div>
                      </TableCell>
                      <TableCell>{competitor.total_reviews.toLocaleString()}</TableCell>
                      <TableCell>
                        <Badge 
                          className={competitor.is_open 
                            ? "bg-chart-2/20 text-chart-2" 
                            : "bg-chart-3/20 text-chart-3"
                          }
                        >
                          {competitor.is_open ? "Open" : "Closed"}
                        </Badge>
                      </TableCell>
                      <TableCell className="hidden md:table-cell">{competitor.category}</TableCell>
                      <TableCell>
                        <Badge className={`${getPositionBadge(competitor.rating).color} bg-opacity-20`}>
                          {getPositionBadge(competitor.rating).label}
                        </Badge>
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
