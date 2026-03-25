import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { TrendingUp, TrendingDown, Star, MessageSquare, Loader2, AlertCircle } from "lucide-react";
import { BusinessInsightsResponse } from "@/lib/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface OverallAnalysisProps {
  businessName: string;
  businessCategory?: string;
  businessLocation?: string;
  cachedData?: BusinessInsightsResponse | null;
  loading?: boolean;
  error?: string | null;
}

const OverallAnalysis = ({ 
  businessName, 
  businessCategory, 
  businessLocation,
  cachedData = null,
  loading = false,
  error = null
}: OverallAnalysisProps) => {
  const data = cachedData;

  const stripMarkdown = (text: string) => {
    const noBold = text.replace(/\*\*(.*?)\*\*/g, "$1");
    const noHeaders = noBold.replace(/^\s*#+\s*/gm, "");
    return noHeaders.trim();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">Analyzing business reviews...</p>
          <p className="text-sm text-muted-foreground">This may take 30-60 seconds</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!data || !data.analysis || !data.analysis.overall_sentiment || !data.analysis.aspect_analysis) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No Data</AlertTitle>
        <AlertDescription>No analysis data available. Please try analyzing a different business.</AlertDescription>
      </Alert>
    );
  }

  // Transform API data for charts
  const sentimentData = [
    { 
      name: "Positive", 
      value: data.analysis.overall_sentiment.positive_percentage, 
      color: "hsl(var(--success))" 
    },
    { 
      name: "Neutral", 
      value: data.analysis.overall_sentiment.neutral_percentage, 
      color: "hsl(var(--info))" 
    },
    { 
      name: "Negative", 
      value: data.analysis.overall_sentiment.negative_percentage, 
      color: "hsl(var(--destructive))" 
    },
  ];

  // Transform aspect analysis for bar chart
  const aspectData = Object.entries(data.analysis.aspect_analysis).map(([aspect, data]) => ({
    aspect: aspect,
    score: data.average_sentiment_score,
    reviews: data.mentions,
    positive: data.sentiment_distribution.positive,
    negative: data.sentiment_distribution.negative,
    neutral: data.sentiment_distribution.neutral,
  }));

  // Extract top keywords (most mentioned aspects)
  const keywordData = Object.entries(data.analysis.aspect_analysis)
    .sort((a, b) => b[1].mentions - a[1].mentions)
    .slice(0, 6)
    .map(([keyword, data]) => ({
      keyword: keyword,
      count: data.mentions,
    }));

  const overallRating = data.business_info?.rating || 0;
  const totalReviews = data.business_info?.total_ratings || 0;
  const reviewsAnalyzed = data.business_info?.reviews_analyzed || 0;
  const positivePercentage = Math.round(data.analysis.overall_sentiment.positive_percentage || 0);
  const overallSentiment = data.analysis.overall_sentiment.sentiment || 'neutral';
  const rawStrategicSummary = data.raw_strategic_insights || data.strategic_insights?.executive_summary || '';
  const sanitizedStrategicSummary = rawStrategicSummary ? stripMarkdown(rawStrategicSummary) : '';
  const strategicParagraphs = (data.strategic_insights_paragraphs || []).map(stripMarkdown);
  const strategicSummary = sanitizedStrategicSummary || rawStrategicSummary;
  
  return (
    <>
      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-soft">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Rating</CardTitle>
            <Star className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallRating.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <Star className="h-3 w-3 text-accent fill-accent" />
              Based on {totalReviews} reviews
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-soft">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Reviews Analyzed</CardTitle>
            <MessageSquare className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{reviewsAnalyzed}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <MessageSquare className="h-3 w-3 text-primary" />
              From Google Maps
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-soft">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Positive Sentiment</CardTitle>
            <TrendingUp className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{positivePercentage}%</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              {positivePercentage >= 60 ? (
                <>
                  <TrendingUp className="h-3 w-3 text-success" />
                  Excellent sentiment
                </>
              ) : positivePercentage >= 40 ? (
                <>
                  <TrendingUp className="h-3 w-3 text-warning" />
                  Good sentiment
                </>
              ) : (
                <>
                  <TrendingDown className="h-3 w-3 text-destructive" />
                  Needs improvement
                </>
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-soft">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Sentiment</CardTitle>
            <MessageSquare className="h-4 w-4 text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{overallSentiment}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              {data.analysis.overall_sentiment.confidence > 0.7 ? (
                <>High confidence</>
              ) : (
                <>Moderate confidence</>
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Sentiment Distribution */}
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle>Sentiment Distribution</CardTitle>
            <CardDescription>Overall customer sentiment breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Keywords */}
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle>Top Keywords</CardTitle>
            <CardDescription>Most mentioned words in reviews</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={keywordData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" />
                <YAxis dataKey="keyword" type="category" width={80} stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "var(--radius)",
                  }}
                />
                <Bar dataKey="count" fill="hsl(var(--primary))" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Aspect-Based Sentiment Analysis */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle>Aspect-Based Sentiment Analysis</CardTitle>
          <CardDescription>Detailed sentiment breakdown by business aspects</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={aspectData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="aspect" stroke="hsl(var(--muted-foreground))" />
              <YAxis domain={[0, 5]} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Bar dataKey="score" fill="hsl(var(--secondary))" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* AI Insights */}
     <Card className="shadow-lg border border-muted rounded-2xl overflow-hidden">
  <CardHeader className="bg-accent/10 border-b py-4 px-6 flex items-center justify-between">
    <div className="flex items-center gap-3">
      <span className="text-xl">✨</span>
      <div>
        <CardTitle className="text-lg font-bold text-primary leading-tight ">
          AI-Generated Insights
        </CardTitle>
        <CardDescription className="text-sm text-muted-foreground mt-1">
          {data.quick_summary || 'Generating insights...'}
        </CardDescription>
      </div>
    </div>
  </CardHeader>

  <CardContent className="space-y-6 p-6">

    {strategicSummary && (
      <div className="space-y-3">
        {strategicParagraphs.length > 0 ? (
          <div className="space-y-4">
            {strategicParagraphs.map((paragraph, idx) => (
              <p
                key={idx}
                className="text-sm leading-relaxed text-black bg-muted/20 p-3 rounded-lg border-l-4 border-l-accent"
              >
                {paragraph}
              </p>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground leading-relaxed">
            {strategicSummary}
          </p>
        )}
      </div>
    )}

  </CardContent>
</Card>

    </>
  );
};

export default OverallAnalysis;
