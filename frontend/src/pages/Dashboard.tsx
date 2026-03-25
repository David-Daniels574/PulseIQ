import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { BarChart3, TrendingUp, Users, Lightbulb } from "lucide-react";
import OverallAnalysis from "@/components/dashboard/OverallAnalysis";
import CompetitorAnalysis from "@/components/dashboard/CompetitorAnalysis";
import MarketIntelligence from "@/components/dashboard/MarketIntelligence";
import Recommendations from "@/components/dashboard/Recommendations";
import { fetchBusinessInsights, BusinessInsightsResponse } from "@/lib/api";

interface DashboardProps {
  businessData: {
    name: string;
    category: string;
    area: string;
    location: string;
  };
}

const Dashboard = ({ businessData }: DashboardProps) => {
  const [activeTab, setActiveTab] = useState("overall");
  const [cachedInsights, setCachedInsights] = useState<BusinessInsightsResponse | null>(null);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  useEffect(() => {
    const loadInsights = async () => {
      if (!businessData.name) {
        setInsightsLoading(false);
        setInsightsError("Business name is required");
        return;
      }

      try {
        setInsightsLoading(true);
        setInsightsError(null);
        
        const response = await fetchBusinessInsights({
          business_name: businessData.name,
          category: businessData.category,
          location: businessData.location,
        });
        
        setCachedInsights(response);
      } catch (err) {
        console.error('Error loading insights:', err);
        setInsightsError(err instanceof Error ? err.message : "Failed to load insights");
      } finally {
        setInsightsLoading(false);
      }
    };

    loadInsights();
  }, [businessData.name, businessData.category, businessData.location]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card shadow-soft">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">{businessData.name}</h1>
              <p className="text-sm text-muted-foreground">
                {businessData.category} • {businessData.area}, {businessData.location}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span className="text-sm text-muted-foreground">Live Data</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid bg-card shadow-soft">
            <TabsTrigger value="overall" className="gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Overall Analysis</span>
              <span className="sm:hidden">Overall</span>
            </TabsTrigger>
            <TabsTrigger value="competitors" className="gap-2">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Competitors</span>
              <span className="sm:hidden">Rivals</span>
            </TabsTrigger>
            <TabsTrigger value="market" className="gap-2">
              <TrendingUp className="h-4 w-4" />
              <span className="hidden sm:inline">Market Intel</span>
              <span className="sm:hidden">Market</span>
            </TabsTrigger>
            <TabsTrigger value="recommendations" className="gap-2">
              <Lightbulb className="h-4 w-4" />
              <span className="hidden sm:inline">Recommendations</span>
              <span className="sm:hidden">Tips</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overall" className="space-y-6">
            <OverallAnalysis 
              businessName={businessData.name}
              businessCategory={businessData.category}
              businessLocation={businessData.location}
              cachedData={cachedInsights}
              loading={insightsLoading}
              error={insightsError}
            />
          </TabsContent>

          <TabsContent value="competitors" className="space-y-6">
            <CompetitorAnalysis
              businessName={businessData.name}
              businessCategory={businessData.category}
              businessLocation={businessData.location}
            />
          </TabsContent>

          <TabsContent value="market" className="space-y-6">
            <MarketIntelligence 
              businessName={businessData.name}
              businessLocation={businessData.location}
              businessCategory={businessData.category}
              currentRating={cachedInsights?.business_info?.rating || 4.3}
              sentimentScore={
                cachedInsights?.analysis?.overall_sentiment 
                  ? cachedInsights.analysis.overall_sentiment.positive_percentage / 100 
                  : 0.75
              }
            />
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-6">
            <Recommendations businessName={businessData.name} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;
