"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Megaphone, Clock, DollarSign, Newspaper, TrendingUp, Sparkles, Target, CheckCircle2 } from "lucide-react"
import { useDashboardData } from "@/hooks/use-dashboard-data"

const categoryIcons: Record<string, React.ElementType> = {
  Marketing: Megaphone,
  Operations: Clock,
  Pricing: DollarSign,
  PR: Newspaper,
  Growth: TrendingUp
}

const priorityColors: Record<string, string> = {
  High: "bg-chart-3/20 text-chart-3 border-chart-3/30",
  Medium: "bg-chart-4/20 text-chart-4 border-chart-4/30",
  Low: "bg-chart-2/20 text-chart-2 border-chart-2/30"
}

const categoryColors: Record<string, string> = {
  Marketing: "bg-primary/20 text-primary",
  Operations: "bg-chart-4/20 text-chart-4",
  Pricing: "bg-chart-2/20 text-chart-2",
  PR: "bg-chart-5/20 text-chart-5",
  Growth: "bg-accent/20 text-accent"
}

export function Recommendations() {
  const { recommendations } = useDashboardData()
  const highPriorityCount = recommendations.filter(r => r.priority === "High").length
  const totalSteps = recommendations.reduce((acc, r) => acc + r.steps.length, 0)

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="rounded-xl bg-primary/10 p-3">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-foreground">AI-Powered Strategic Recommendations</h3>
              <p className="mt-1 text-muted-foreground">
                Actionable insights generated from comprehensive business analysis
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card className="border-border/50">
          <CardContent className="p-6 text-center">
            <p className="text-3xl font-bold text-foreground">{recommendations.length}</p>
            <p className="text-sm text-muted-foreground">Total Recommendations</p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="p-6 text-center">
            <p className="text-3xl font-bold text-chart-3">{highPriorityCount}</p>
            <p className="text-sm text-muted-foreground">High Priority Actions</p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="p-6 text-center">
            <p className="text-3xl font-bold text-chart-2">+0.5 to +0.8</p>
            <p className="text-sm text-muted-foreground">Expected Rating Improvement</p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="p-6 text-center">
            <p className="text-3xl font-bold text-primary">{totalSteps}</p>
            <p className="text-sm text-muted-foreground">Action Steps</p>
          </CardContent>
        </Card>
      </div>

      {/* Recommendation Cards */}
      <div className="space-y-4">
        {recommendations.map((rec) => {
          const Icon = categoryIcons[rec.category] || Target
          
          return (
            <Card 
              key={rec.id} 
              className="border-border/50 transition-all hover:border-primary/30 hover:shadow-md"
            >
              <CardHeader className="pb-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className={`rounded-xl p-2.5 ${categoryColors[rec.category]}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{rec.title}</CardTitle>
                      <div className="mt-1 flex items-center gap-2">
                        <Badge className={categoryColors[rec.category]}>
                          {rec.category}
                        </Badge>
                        <Badge variant="outline" className={priorityColors[rec.priority]}>
                          {rec.priority} Priority
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    {rec.timeline}
                  </div>
                </div>
                <CardDescription className="mt-3">{rec.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Impact */}
                <div className="rounded-lg bg-chart-2/10 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-chart-2">
                    <TrendingUp className="h-4 w-4" />
                    Expected Impact
                  </div>
                  <p className="mt-1 text-sm text-foreground">{rec.impact}</p>
                </div>
                
                {/* Action Steps */}
                <div>
                  <p className="mb-3 text-sm font-semibold text-foreground">Action Steps</p>
                  <div className="space-y-2">
                    {rec.steps.map((step, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                          {index + 1}
                        </div>
                        <p className="text-sm text-muted-foreground">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Implementation Roadmap */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            Implementation Roadmap
          </CardTitle>
          <CardDescription>Suggested timeline for executing recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <div className="absolute left-4 top-0 h-full w-0.5 bg-border" />
            
            <div className="space-y-6">
              {[
                { phase: "Week 1-2", title: "Quick Wins", items: ["Set up review monitoring", "Create response templates", "Train staff on protocols"] },
                { phase: "Week 3-4", title: "Foundation", items: ["Implement table management system", "Launch loyalty program beta", "Update menu descriptions"] },
                { phase: "Month 2", title: "Growth", items: ["Social media campaign launch", "Corporate partnerships outreach", "Seasonal menu introduction"] },
                { phase: "Month 3+", title: "Optimization", items: ["Analyze results and iterate", "Scale successful initiatives", "Plan next quarter strategies"] }
              ].map((phase, index) => (
                <div key={index} className="relative pl-10">
                  <div className="absolute left-2.5 top-1 h-3 w-3 rounded-full border-2 border-primary bg-background" />
                  <div className="rounded-lg bg-secondary/50 p-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">{phase.phase}</Badge>
                      <span className="font-semibold text-foreground">{phase.title}</span>
                    </div>
                    <ul className="mt-3 space-y-1">
                      {phase.items.map((item, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                          <CheckCircle2 className="h-4 w-4 text-muted-foreground/50" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
