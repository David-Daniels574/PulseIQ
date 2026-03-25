"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Target, Lightbulb, Globe, Rocket, AlertCircle, TrendingUp } from "lucide-react"
import { ansoffMatrixData } from "@/lib/mock-data"

const quadrantConfig = {
  marketPenetration: {
    title: "Market Penetration",
    axes: "Existing Products × Existing Markets",
    icon: Target,
    bgColor: "bg-chart-2/10",
    borderColor: "border-chart-2/30",
    iconBg: "bg-chart-2/20",
    iconColor: "text-chart-2"
  },
  productDevelopment: {
    title: "Product Development",
    axes: "New Products × Existing Markets",
    icon: Lightbulb,
    bgColor: "bg-primary/10",
    borderColor: "border-primary/30",
    iconBg: "bg-primary/20",
    iconColor: "text-primary"
  },
  marketDevelopment: {
    title: "Market Development",
    axes: "Existing Products × New Markets",
    icon: Globe,
    bgColor: "bg-chart-4/10",
    borderColor: "border-chart-4/30",
    iconBg: "bg-chart-4/20",
    iconColor: "text-chart-4"
  },
  diversification: {
    title: "Diversification",
    axes: "New Products × New Markets",
    icon: Rocket,
    bgColor: "bg-chart-5/10",
    borderColor: "border-chart-5/30",
    iconBg: "bg-chart-5/20",
    iconColor: "text-chart-5"
  }
}

const riskColors = {
  Low: "bg-chart-2/20 text-chart-2",
  Medium: "bg-chart-4/20 text-chart-4",
  High: "bg-chart-3/20 text-chart-3"
}

interface StrategyCardProps {
  type: keyof typeof quadrantConfig
  data: {
    description: string
    recommendations: string[]
    riskLevel: string
    expectedROI: string
  }
}

function StrategyCard({ type, data }: StrategyCardProps) {
  const config = quadrantConfig[type]
  const Icon = config.icon

  return (
    <Card className={`${config.bgColor} ${config.borderColor} border-2 transition-all hover:shadow-lg`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`rounded-xl ${config.iconBg} p-3`}>
              <Icon className={`h-6 w-6 ${config.iconColor}`} />
            </div>
            <div>
              <CardTitle className="text-lg">{config.title}</CardTitle>
              <CardDescription className="text-xs">{config.axes}</CardDescription>
            </div>
          </div>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">{data.description}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <Badge className={riskColors[data.riskLevel as keyof typeof riskColors]}>
            <AlertCircle className="mr-1 h-3 w-3" />
            {data.riskLevel} Risk
          </Badge>
          <Badge variant="outline" className="gap-1">
            <TrendingUp className="h-3 w-3" />
            ROI: {data.expectedROI}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Recommendations
          </p>
          <ul className="space-y-2">
            {data.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className={`mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full ${config.iconColor.replace('text-', 'bg-')}`} />
                <span className="text-foreground">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

export function AnsoffMatrix() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-border/50">
        <CardContent className="p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-foreground">Ansoff Growth Matrix</h3>
              <p className="text-sm text-muted-foreground">
                Strategic framework for business growth opportunities based on market and product analysis
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {Object.entries(riskColors).map(([level, color]) => (
                <Badge key={level} className={color}>
                  {level} Risk
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Matrix Grid */}
      <div className="grid gap-4 lg:grid-cols-2">
        <StrategyCard type="marketPenetration" data={ansoffMatrixData.marketPenetration} />
        <StrategyCard type="productDevelopment" data={ansoffMatrixData.productDevelopment} />
        <StrategyCard type="marketDevelopment" data={ansoffMatrixData.marketDevelopment} />
        <StrategyCard type="diversification" data={ansoffMatrixData.diversification} />
      </div>

      {/* Strategic Insight */}
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="rounded-xl bg-primary/10 p-3">
              <Target className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h4 className="font-semibold text-foreground">Strategic Recommendation</h4>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                Based on your current market position and sentiment analysis, we recommend prioritizing 
                <span className="font-medium text-foreground"> Market Penetration </span> 
                strategies in the short term to maximize ROI with minimal risk. In parallel, consider 
                <span className="font-medium text-foreground"> Product Development </span>
                initiatives like seasonal menus and premium experiences to capture additional market share 
                from existing customers.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
