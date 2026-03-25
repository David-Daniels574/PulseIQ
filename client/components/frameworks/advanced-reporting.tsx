"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileDown, AlertTriangle, CheckCircle, TrendingUp, Calendar } from "lucide-react"
import { advancedReportingData } from "@/lib/mock-data"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts"

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

export function AdvancedReporting() {
  const heatmapData = Object.entries(advancedReportingData.seasonalPatterns).map(([aspect, values]) => ({
    aspect,
    values: values as number[]
  }))

  const getHeatmapColor = (value: number) => {
    if (value >= 4.5) return 'bg-chart-2'
    if (value >= 4.0) return 'bg-chart-2/70'
    if (value >= 3.5) return 'bg-chart-4'
    return 'bg-chart-3/70'
  }

  return (
    <div className="space-y-6">
      {/* Export Button Header */}
      <Card className="border-border/50">
        <CardContent className="flex flex-col items-center justify-between gap-4 p-6 sm:flex-row">
          <div>
            <h3 className="text-lg font-semibold text-foreground">Intelligence Report</h3>
            <p className="text-sm text-muted-foreground">
              Export comprehensive PDF report with all analytics and recommendations
            </p>
          </div>
          <Button size="lg" className="gap-2">
            <FileDown className="h-5 w-5" />
            Export PDF Report
          </Button>
        </CardContent>
      </Card>

      {/* Alerts */}
      {advancedReportingData.alerts.length > 0 && (
        <div className="space-y-3">
          {advancedReportingData.alerts.map((alert, index) => (
            <Card 
              key={index} 
              className={`border-l-4 ${
                alert.type === 'warning' 
                  ? 'border-l-chart-4 bg-chart-4/5' 
                  : 'border-l-chart-2 bg-chart-2/5'
              }`}
            >
              <CardContent className="flex items-center gap-4 p-4">
                {alert.type === 'warning' ? (
                  <AlertTriangle className="h-5 w-5 text-chart-4" />
                ) : (
                  <CheckCircle className="h-5 w-5 text-chart-2" />
                )}
                <div className="flex-1">
                  <p className="font-medium text-foreground">{alert.message}</p>
                  <p className="text-sm text-muted-foreground">{alert.date}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Sentiment Over Time */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle>Sentiment Over Time</CardTitle>
            <CardDescription>Weekly sentiment trends over the past 6 weeks</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={advancedReportingData.sentimentOverTime}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))', 
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="positive" 
                  name="Positive"
                  stackId="1"
                  stroke="hsl(var(--chart-2))" 
                  fill="hsl(var(--chart-2))"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="neutral" 
                  name="Neutral"
                  stackId="1"
                  stroke="hsl(var(--chart-4))" 
                  fill="hsl(var(--chart-4))"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="negative" 
                  name="Negative"
                  stackId="1"
                  stroke="hsl(var(--chart-3))" 
                  fill="hsl(var(--chart-3))"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Rating Evolution */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-chart-2" />
              Rating Evolution
            </CardTitle>
            <CardDescription>How your rating has changed over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={advancedReportingData.ratingEvolution}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis 
                  domain={[4, 5]} 
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
                <Line 
                  type="monotone" 
                  dataKey="rating" 
                  name="Rating"
                  stroke="hsl(var(--primary))" 
                  strokeWidth={3}
                  dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Seasonal Pattern Heatmap */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Seasonal Pattern Analysis
          </CardTitle>
          <CardDescription>
            Monthly sentiment patterns by aspect - darker colors indicate higher scores
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <div className="min-w-[600px]">
              {/* Header */}
              <div className="mb-2 flex">
                <div className="w-24 flex-shrink-0" />
                {months.map((month) => (
                  <div 
                    key={month} 
                    className="flex-1 text-center text-xs font-medium text-muted-foreground"
                  >
                    {month}
                  </div>
                ))}
              </div>
              
              {/* Rows */}
              {heatmapData.map((row, rowIndex) => (
                <div key={rowIndex} className="mb-1 flex items-center">
                  <div className="w-24 flex-shrink-0 pr-2 text-sm font-medium text-foreground">
                    {row.aspect}
                  </div>
                  {row.values.map((value, colIndex) => (
                    <div key={colIndex} className="flex-1 p-0.5">
                      <div 
                        className={`flex h-8 items-center justify-center rounded text-xs font-medium text-white ${getHeatmapColor(value)}`}
                        title={`${row.aspect} - ${months[colIndex]}: ${value.toFixed(1)}`}
                      >
                        {value.toFixed(1)}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
          
          {/* Legend */}
          <div className="mt-6 flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded bg-chart-2" />
              <span className="text-muted-foreground">Excellent (4.5+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded bg-chart-2/70" />
              <span className="text-muted-foreground">Good (4.0-4.5)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded bg-chart-4" />
              <span className="text-muted-foreground">Fair (3.5-4.0)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded bg-chart-3/70" />
              <span className="text-muted-foreground">Needs Work ({'<'}3.5)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Insights Summary */}
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardHeader>
          <CardTitle>Seasonal Insights</CardTitle>
          <CardDescription>Key patterns identified from historical data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg bg-card/50 p-4">
              <p className="mb-2 text-sm font-medium text-foreground">Peak Performance</p>
              <p className="text-sm text-muted-foreground">
                Food quality scores peak during April-May and October-November, coinciding with 
                seasonal menu changes and fresh ingredient availability.
              </p>
            </div>
            <div className="rounded-lg bg-card/50 p-4">
              <p className="mb-2 text-sm font-medium text-foreground">Service Challenges</p>
              <p className="text-sm text-muted-foreground">
                Service scores dip during summer months (July-August), likely due to increased 
                tourist traffic and staff turnover.
              </p>
            </div>
            <div className="rounded-lg bg-card/50 p-4">
              <p className="mb-2 text-sm font-medium text-foreground">Price Sensitivity</p>
              <p className="text-sm text-muted-foreground">
                Price perception improves during holiday season (November-December), suggesting 
                customers are more willing to spend during celebrations.
              </p>
            </div>
            <div className="rounded-lg bg-card/50 p-4">
              <p className="mb-2 text-sm font-medium text-foreground">Recommended Action</p>
              <p className="text-sm text-muted-foreground">
                Consider implementing dynamic pricing and staffing adjustments based on these 
                seasonal patterns to optimize customer satisfaction year-round.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
