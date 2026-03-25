import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, Target, TrendingUp, Users, DollarSign, MessageSquare } from "lucide-react";

interface RecommendationsProps {
  businessName: string;
}

const recommendations = [
  {
    category: "Marketing",
    icon: Target,
    priority: "high",
    title: "Launch Social Media Campaign Highlighting Ambiance",
    description:
      "Your ambiance receives the highest ratings (4.7/5). Create Instagram and Facebook content showcasing your cozy atmosphere with professional photos. Use hashtags like #CozyDining #AuthenticAmbiance #BandraEats to reach local food enthusiasts.",
    expectedImpact: "15-20% increase in foot traffic",
    timeline: "Immediate",
    steps: [
      "Hire professional photographer for interior shots",
      "Post 3x per week during peak dining decision times (4-6 PM)",
      "Collaborate with local food influencers for authentic reviews",
      "Run targeted ads within 5km radius focusing on ambiance seekers",
    ],
  },
  {
    category: "Operations",
    icon: Users,
    priority: "high",
    title: "Optimize Service During Peak Hours",
    description:
      "Service ratings (4.2/5) lag behind food quality and ambiance. Customer reviews mention slow service during lunch (12-2 PM) and dinner (7-9 PM) rushes. Address this to improve overall satisfaction.",
    expectedImpact: "0.3-0.5 star rating increase",
    timeline: "2-4 weeks",
    steps: [
      "Hire additional server for peak hours",
      "Implement kitchen display system to streamline orders",
      "Train staff on efficiency protocols",
      "Pre-prep popular items during non-peak hours",
    ],
  },
  {
    category: "Pricing",
    icon: DollarSign,
    priority: "medium",
    title: "Adjust Value Perception Through Portion Strategy",
    description:
      "Price ratings (3.8/5) indicate customers perceive items as expensive. Rather than reducing prices, consider increasing portion sizes slightly or adding complementary items to enhance perceived value.",
    expectedImpact: "12-18% improvement in price satisfaction",
    timeline: "4-6 weeks",
    steps: [
      "Analyze top 10 best-selling dishes for portion optimization",
      "Add complimentary appetizer or drink with main courses",
      "Introduce value combo meals during lunch hours",
      "Clearly communicate portion sizes on menu with photos",
    ],
  },
  {
    category: "PR",
    icon: MessageSquare,
    priority: "medium",
    title: "Increase Review Response Rate",
    description:
      "Your response rate dropped to 78% (-3% from last month). Responding to reviews, especially negative ones, shows you value customer feedback and can convert critics into advocates.",
    expectedImpact: "5-8% increase in positive sentiment",
    timeline: "Immediate",
    steps: [
      "Designate team member to monitor reviews daily",
      "Create response templates for common feedback types",
      "Respond to all reviews within 24 hours",
      "Offer resolution for negative reviews (discount/complimentary item)",
    ],
  },
  {
    category: "Growth",
    icon: TrendingUp,
    priority: "low",
    title: "Capitalize on Competitor A's Expansion",
    description:
      "Competitor A is opening a second location, which may spread their resources thin. This is an opportunity to capture market share by emphasizing your consistent quality and personalized service.",
    expectedImpact: "10-15% new customer acquisition",
    timeline: "Next 3 months",
    steps: [
      "Launch 'Loyal Customer' referral program with incentives",
      "Emphasize single-location focus in marketing materials",
      "Host community events to strengthen local ties",
      "Partner with nearby businesses for cross-promotion",
    ],
  },
];

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case "high":
      return "bg-destructive text-destructive-foreground";
    case "medium":
      return "bg-warning text-warning-foreground";
    case "low":
      return "bg-info text-info-foreground";
    default:
      return "bg-secondary text-secondary-foreground";
  }
};

const Recommendations = ({ businessName }: RecommendationsProps) => {
  return (
    <>
      {/* Header Card */}
      <Card className="shadow-soft border-l-4 border-l-accent bg-gradient-to-br from-card to-accent/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-6 w-6 text-accent" />
            AI-Powered Strategic Recommendations
          </CardTitle>
          <CardDescription>
            Actionable insights generated from comprehensive analysis of your reviews, competitor data, market trends, and predictive forecasts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
            <span>Last updated: November 12, 2024</span>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <div className="space-y-6">
        {recommendations.map((rec, index) => {
          const IconComponent = rec.icon;
          return (
            <Card key={index} className="shadow-medium hover:shadow-strong transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <IconComponent className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="text-xs">
                          {rec.category}
                        </Badge>
                        <Badge className={`text-xs ${getPriorityColor(rec.priority)}`}>{rec.priority} priority</Badge>
                      </div>
                      <CardTitle className="text-lg">{rec.title}</CardTitle>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">{rec.description}</p>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="p-3 bg-success/10 rounded-lg border border-success/20">
                    <p className="text-xs font-semibold text-success mb-1">Expected Impact</p>
                    <p className="text-sm">{rec.expectedImpact}</p>
                  </div>
                  <div className="p-3 bg-info/10 rounded-lg border border-info/20">
                    <p className="text-xs font-semibold text-info mb-1">Timeline</p>
                    <p className="text-sm">{rec.timeline}</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-semibold mb-2">Action Steps:</p>
                  <ol className="list-decimal list-inside space-y-2">
                    {rec.steps.map((step, stepIndex) => (
                      <li key={stepIndex} className="text-sm text-muted-foreground ml-2">
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Summary Card */}
      <Card className="shadow-soft bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="text-lg">Implementation Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center pb-2 border-b">
            <span className="text-sm font-medium">Total Recommendations</span>
            <span className="text-lg font-bold">{recommendations.length}</span>
          </div>
          <div className="flex justify-between items-center pb-2 border-b">
            <span className="text-sm font-medium">High Priority Actions</span>
            <span className="text-lg font-bold text-destructive">{recommendations.filter((r) => r.priority === "high").length}</span>
          </div>
          <div className="flex justify-between items-center pb-2 border-b">
            <span className="text-sm font-medium">Expected Rating Improvement</span>
            <span className="text-lg font-bold text-success">+0.5 to +0.8 stars</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Projected Implementation Timeline</span>
            <span className="text-lg font-bold">2-3 months</span>
          </div>
        </CardContent>
      </Card>
    </>
  );
};

export default Recommendations;
