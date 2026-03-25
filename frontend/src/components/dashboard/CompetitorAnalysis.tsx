import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  BarChart,
  Bar,
  Legend,
} from "recharts";
import { Badge } from "@/components/ui/badge";
import {
  fetchCompetitorAnalysis,
  CompetitorAnalysisResponse,
  AspectShowdownEntry,
} from "@/lib/api";

interface CompetitorAnalysisProps {
  businessName: string;
  businessCategory: string;
  businessLocation: string;
  radius?: number;
}

const competitorColors = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--chart-6, var(--primary)))",
];

const getCategoryColor = (category: string) => {
  switch (category) {
    case "Leader":
      return "bg-success text-success-foreground";
    case "Challenger":
      return "bg-warning text-warning-foreground";
    case "Follower":
      return "bg-muted text-muted-foreground";
    default:
      return "bg-secondary text-secondary-foreground";
  }
};

const getPointSize = (reviews: number) => {
  if (!Number.isFinite(reviews)) {
    return 200;
  }
  return Math.max(200, Math.sqrt(Math.max(reviews, 0)) * 25);
};

const categorizeCompetitor = (competitorRating: number, mainRating: number) => {
  if (!Number.isFinite(mainRating) || mainRating === 0) {
    return "Competitor";
  }
  if (competitorRating >= mainRating + 0.15) {
    return "Leader";
  }
  if (competitorRating >= mainRating - 0.15) {
    return "Challenger";
  }
  return "Follower";
};

const formatNumber = (value: number | null | undefined) => {
  if (!Number.isFinite(value ?? NaN)) {
    return "-";
  }
  return Number(value).toLocaleString();
};

const CompetitorAnalysis = ({
  businessName,
  businessCategory,
  businessLocation,
  radius = 5000,
}: CompetitorAnalysisProps) => {
  const [data, setData] = useState<CompetitorAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    fetchCompetitorAnalysis({
      business_name: businessName,
      category: businessCategory,
      location: businessLocation,
      radius,
    })
      .then((response) => {
        if (!isMounted) return;
        setData(response);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err.message || "Failed to load competitor analysis");
      })
      .finally(() => {
        if (!isMounted) return;
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [businessName, businessCategory, businessLocation, radius]);

  const mainBusiness = data?.main_business;
  const mainRating = Number(mainBusiness?.rating ?? 0);
  const mainReviews = Number(mainBusiness?.total_reviews ?? 0);

  const quadrantData = useMemo(() => {
    if (!data) return [];

    const competitors = data.competitors.map((competitor, index) => ({
      name: competitor.name,
      rating: Number(competitor.rating ?? 0),
      reviews: Number(competitor.total_reviews ?? 0),
      size: getPointSize(competitor.total_reviews ?? 0),
      color: competitorColors[index % competitorColors.length],
      isUser: false,
    }));

    const base = {
      name: data.main_business?.name || businessName,
      rating: mainRating,
      reviews: mainReviews,
      size: getPointSize(mainReviews),
      color: "hsl(var(--accent))",
      isUser: true,
    };

    return [base, ...competitors];
  }, [data, businessName, mainRating, mainReviews]);

  const aspectComparisonData = useMemo(() => {
    if (!data?.aspect_showdown?.aspects?.length) return [];
    return data.aspect_showdown.aspects.map((aspect: AspectShowdownEntry) => ({
      aspect: aspect.aspect,
      yourBusiness: aspect.your_score ?? null,
      competitorAvg: aspect.competitor_avg ?? null,
    }));
  }, [data]);

  const competitorTableData = useMemo(() => {
    if (!data) return [];

    return data.competitors.map((competitor, index) => {
      const rating = Number(competitor.rating ?? 0);
      const categoryLabel = categorizeCompetitor(rating, mainRating);

      return {
        key: competitor.place_id || `competitor-${index}`,
        name: competitor.name,
        rating,
        reviews: Number(competitor.total_reviews ?? 0),
        address: competitor.address || "Not provided",
        isOpen: competitor.is_open,
        category: categoryLabel,
        badgeClass: getCategoryColor(categoryLabel),
      };
    });
  }, [data, mainRating]);

  const renderLoading = (message: string) => (
    <div className="flex h-60 items-center justify-center text-sm text-muted-foreground">
      {message}
    </div>
  );

  const renderError = (message: string) => (
    <div className="flex h-60 items-center justify-center text-sm text-destructive">
      {message}
    </div>
  );

  return (
    <>
      {/* Competitor Quadrant */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle>Competitive Positioning Map</CardTitle>
          <CardDescription>Your position in the local market based on quality vs. popularity</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && renderLoading("Loading competitor positioning...")}
          {!loading && error && renderError(error)}
          {!loading && !error && quadrantData.length === 0 && (
            <div className="flex h-60 items-center justify-center text-sm text-muted-foreground">
              No competitor data available yet. Run an analysis to populate this view.
            </div>
          )}
          {!loading && !error && quadrantData.length > 0 && (
            <>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    type="number"
                    dataKey="reviews"
                    name="Total Reviews"
                    stroke="hsl(var(--muted-foreground))"
                    label={{ value: "Popularity (Total Reviews)", position: "insideBottom", offset: -5 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="rating"
                    name="Rating"
                    domain={[3, 5]}
                    stroke="hsl(var(--muted-foreground))"
                    label={{ value: "Quality (Avg. Rating)", angle: -90, position: "insideLeft" }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "var(--radius)",
                    }}
                  />
                  <Scatter data={quadrantData} dataKey="size">
                    {quadrantData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color}
                        stroke={entry.isUser ? "hsl(var(--foreground))" : "none"}
                        strokeWidth={entry.isUser ? 3 : 0}
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
              <div className="mt-4 flex flex-wrap justify-center gap-4 text-xs">
                {quadrantData.map((competitor, index) => (
                  <div key={`legend-${index}`} className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: competitor.color }} />
                    <span className={competitor.isUser ? "font-bold" : ""}>{competitor.name}</span>
                  </div>
                ))}
              </div>
              {data?.competitive_analysis && (
                <div className="mt-6 grid gap-3 text-sm text-muted-foreground sm:grid-cols-2">
                  <div>
                    Avg competitor rating: <span className="text-foreground">{data.competitive_analysis.average_competitor_rating.toFixed(2)}</span>
                  </div>
                  <div>
                    Avg competitor reviews: <span className="text-foreground">{formatNumber(data.competitive_analysis.average_competitor_reviews)}</span>
                  </div>
                  <div>
                    Rating position: <span className="text-foreground">{data.competitive_analysis.your_rating_vs_average}</span>
                  </div>
                  <div>
                    Review volume: <span className="text-foreground">{data.competitive_analysis.your_reviews_vs_average}</span>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Aspect Showdown */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle>Aspect Showdown</CardTitle>
          <CardDescription>Head-to-head comparison with competitor average</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && renderLoading("Calculating aspect scores...")}
          {!loading && error && renderError("Unable to load aspect comparison")}
          {!loading && !error && aspectComparisonData.length === 0 && (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              No overlapping aspect data yet. Run insights to generate scores.
            </div>
          )}
          {!loading && !error && aspectComparisonData.length > 0 && (
            <>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={aspectComparisonData}>
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
                  <Legend />
                  <Bar dataKey="yourBusiness" fill="hsl(var(--accent))" name="Your Business" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="competitorAvg" fill="hsl(var(--primary))" name="Competitor Avg" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
              {data?.aspect_showdown?.methodology && (
                <p className="mt-4 text-xs text-muted-foreground">
                  {data.aspect_showdown.methodology}
                </p>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Detailed Comparison Table */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle>Detailed Competitor Breakdown</CardTitle>
          <CardDescription>Side-by-side comparison of key metrics</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && renderLoading("Loading competitor leaderboard...")}
          {!loading && error && renderError("Unable to load competitor leaderboard")}
          {!loading && !error && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Business Name</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Total Reviews</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Address</TableHead>
                  <TableHead>Category</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow className="bg-accent/10">
                  <TableCell className="font-bold">{mainBusiness?.name || businessName} (You)</TableCell>
                  <TableCell>{mainRating ? `${mainRating.toFixed(1)} ⭐` : "-"}</TableCell>
                  <TableCell>{formatNumber(mainReviews)}</TableCell>
                  <TableCell>-</TableCell>
                  <TableCell>{mainBusiness?.address || "Not available"}</TableCell>
                  <TableCell>
                    <Badge className="bg-accent text-accent-foreground">
                      {data?.competitive_analysis?.market_position || "Your Business"}
                    </Badge>
                  </TableCell>
                </TableRow>
                {competitorTableData.map((competitor) => (
                  <TableRow key={competitor.key}>
                    <TableCell>{competitor.name}</TableCell>
                    <TableCell>{competitor.rating ? `${competitor.rating.toFixed(1)} ⭐` : "-"}</TableCell>
                    <TableCell>{formatNumber(competitor.reviews)}</TableCell>
                    <TableCell>
                      {competitor.isOpen === true
                        ? "Open now"
                        : competitor.isOpen === false
                        ? "Closed"
                        : "Unknown"}
                    </TableCell>
                    <TableCell className="max-w-xs truncate" title={competitor.address}>
                      {competitor.address}
                    </TableCell>
                    <TableCell>
                      <Badge className={competitor.badgeClass}>{competitor.category}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </>
  );
};

export default CompetitorAnalysis;
