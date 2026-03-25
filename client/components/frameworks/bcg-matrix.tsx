"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star, DollarSign, HelpCircle, AlertTriangle } from "lucide-react"
import { useDashboardData } from "@/hooks/use-dashboard-data"

const quadrantConfig = {
  stars: {
    title: "Stars",
    subtitle: "High Growth, High Share",
    description: "Invest heavily - these are your future cash cows",
    icon: Star,
    bgColor: "bg-chart-2/10",
    borderColor: "border-chart-2/30",
    iconColor: "text-chart-2",
    badgeColor: "bg-chart-2/20 text-chart-2"
  },
  cashCows: {
    title: "Cash Cows",
    subtitle: "Low Growth, High Share",
    description: "Maximize profits - these generate steady revenue",
    icon: DollarSign,
    bgColor: "bg-primary/10",
    borderColor: "border-primary/30",
    iconColor: "text-primary",
    badgeColor: "bg-primary/20 text-primary"
  },
  questionMarks: {
    title: "Question Marks",
    subtitle: "High Growth, Low Share",
    description: "Evaluate potential - invest or divest strategically",
    icon: HelpCircle,
    bgColor: "bg-chart-4/10",
    borderColor: "border-chart-4/30",
    iconColor: "text-chart-4",
    badgeColor: "bg-chart-4/20 text-chart-4"
  },
  dogs: {
    title: "Dogs",
    subtitle: "Low Growth, Low Share",
    description: "Consider removal - these drain resources",
    icon: AlertTriangle,
    bgColor: "bg-chart-3/10",
    borderColor: "border-chart-3/30",
    iconColor: "text-chart-3",
    badgeColor: "bg-chart-3/20 text-chart-3"
  }
}

interface QuadrantCardProps {
  type: keyof typeof quadrantConfig
  items: Array<{ name: string; mentions: number; sentimentAvg: number }>
}

function QuadrantCard({ type, items }: QuadrantCardProps) {
  const config = quadrantConfig[type]
  const Icon = config.icon

  return (
    <Card className={`${config.bgColor} ${config.borderColor} border-2`}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className={`rounded-lg bg-background p-2 ${config.iconColor}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-lg">{config.title}</CardTitle>
            <CardDescription className="text-xs">{config.subtitle}</CardDescription>
          </div>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">{config.description}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.length > 0 ? (
            items.map((item, index) => (
              <div 
                key={index}
                className="flex items-center justify-between rounded-lg bg-background/80 p-3"
              >
                <div>
                  <p className="font-medium text-foreground">{item.name}</p>
                  <p className="text-xs text-muted-foreground">{item.mentions} mentions</p>
                </div>
                <Badge className={config.badgeColor}>
                  {item.sentimentAvg.toFixed(1)}
                </Badge>
              </div>
            ))
          ) : (
            <div className="rounded-lg bg-background/50 p-4 text-center text-sm text-muted-foreground">
              No items in this quadrant
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export function BCGMatrix() {
  const { bcgMatrixData } = useDashboardData()
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-border/50">
        <CardContent className="p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-foreground">BCG Growth-Share Matrix</h3>
              <p className="text-sm text-muted-foreground">
                Strategic analysis of menu items based on customer sentiment and popularity
              </p>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-chart-2" />
                <span className="text-muted-foreground">High Sentiment</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-chart-3" />
                <span className="text-muted-foreground">Low Sentiment</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Matrix Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        <QuadrantCard type="stars" items={bcgMatrixData.stars} />
        <QuadrantCard type="cashCows" items={bcgMatrixData.cashCows} />
        <QuadrantCard type="questionMarks" items={bcgMatrixData.questionMarks} />
        <QuadrantCard type="dogs" items={bcgMatrixData.dogs} />
      </div>

      {/* Summary Stats */}
      <Card className="border-border/50">
        <CardContent className="p-6">
          <div className="grid gap-4 sm:grid-cols-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-chart-2">{bcgMatrixData.stars.length}</p>
              <p className="text-sm text-muted-foreground">Star Items</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">{bcgMatrixData.cashCows.length}</p>
              <p className="text-sm text-muted-foreground">Cash Cows</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-chart-4">{bcgMatrixData.questionMarks.length}</p>
              <p className="text-sm text-muted-foreground">Question Marks</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-chart-3">{bcgMatrixData.dogs.length}</p>
              <p className="text-sm text-muted-foreground">Dogs</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
