"use client"

import { useEffect, useState } from "react"

import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardSidebar } from "@/components/dashboard/dashboard-sidebar"
import { DashboardProvider } from "@/hooks/use-dashboard-data"
import {
  DashboardData,
  getBusinessInsights,
  getCompetitorInsights,
  getMarketIntelligence,
  mapCompetitorToDashboardData,
  mapInsightsToDashboardData,
  mapMarketIntelligenceToDashboardFields,
} from "@/services/dashboard.service"

// Framework Components
import { OverallAnalysis } from "@/components/frameworks/overall-analysis"
import { CompetitorAnalysis } from "@/components/frameworks/competitor-analysis"
import { MarketIntelligence } from "@/components/frameworks/market-intelligence"
import { BCGMatrix } from "@/components/frameworks/bcg-matrix"
import { AnsoffMatrix } from "@/components/frameworks/ansoff-matrix"
import { SwotAnalysis } from "@/components/frameworks/swot-analysis"
import { PestelFramework } from "@/components/frameworks/pestel-framework"
import { FourPsFramework } from "@/components/frameworks/four-ps-framework"
import { ORMIntegration } from "@/components/frameworks/orm-integration"
import { SocialListening } from "@/components/frameworks/social-listening"
import { AdvancedReporting } from "@/components/frameworks/advanced-reporting"
import { Recommendations } from "@/components/frameworks/recommendations"

const contentMap: Record<string, React.ReactNode> = {
  overall:         <OverallAnalysis />,
  competitors:     <CompetitorAnalysis />,
  market:          <MarketIntelligence />,
  swot:            <SwotAnalysis />,
  pestel:          <PestelFramework />,
  fourps:          <FourPsFramework />,
  bcg:             <BCGMatrix />,
  ansoff:          <AnsoffMatrix />,
  orm:             <ORMIntegration />,
  social:          <SocialListening />,
  reporting:       <AdvancedReporting />,
  recommendations: <Recommendations />,
}

export default function DashboardPage() {
  const [activeTab, setActiveTab]       = useState("overall")
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)

  // Input fields for dynamic queries
  const [businessName, setBusinessName] = useState("")
  const [area, setArea] = useState("")
  const [city, setCity] = useState("")
  const [twitterQuery, setTwitterQuery] = useState("")
  const [monthsBack, setMonthsBack] = useState("2")
  const [hasSearched, setHasSearched] = useState(false)
  const [isMarketLoading, setIsMarketLoading] = useState(false)

  const loadInsights = async (name: string, areaVal: string, cityVal: string, twitterVal: string, months: string) => {
    setIsRefreshing(true)

    try {
      const normalizedTwitterQuery = twitterVal.trim() || `${name} ${areaVal}`
      const [insights, competitorInsights] = await Promise.all([
        getBusinessInsights({
        business_name: name,
        area: areaVal,
        city: cityVal,
        twitter_query: normalizedTwitterQuery,
        months_back: parseInt(months) || 2,
      }),
        getCompetitorInsights({
          business_name: name,
          area: areaVal,
          city: cityVal,
        }),
      ])

      const mappedDashboard = mapInsightsToDashboardData(insights)
      mappedDashboard.competitorData = mapCompetitorToDashboardData(competitorInsights)
      setDashboardData(mappedDashboard)
      setHasSearched(true)

      // Fire market-intelligence call non-blocking — updates forecast + news when ready
      setIsMarketLoading(true)
      void getMarketIntelligence({
        business_name: name,
        city: cityVal,
        category: mappedDashboard.businessInfo.category,
        current_rating: mappedDashboard.businessInfo.rating,
      })
        .then((miResp) => {
          const miFields = mapMarketIntelligenceToDashboardFields(miResp)
          setDashboardData((prev) =>
            prev ? { ...prev, ...miFields } : prev,
          )
        })
        .catch((err) => console.error("Market intelligence fetch failed:", err))
        .finally(() => setIsMarketLoading(false))
    } catch (error) {
      console.error("Failed to load dashboard insights:", error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (businessName.trim() && area.trim() && city.trim()) {
      void loadInsights(businessName, area, city, twitterQuery, monthsBack)
    }
  }

  const handleRefresh = () => {
    if (businessName && area && city) {
      void loadInsights(businessName, area, city, twitterQuery, monthsBack)
    }
  }

  // Show search form if no data loaded yet
  if (!hasSearched || !dashboardData) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="w-full max-w-md space-y-6 rounded-lg border border-border bg-card p-8 shadow-lg">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Business Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-1">Enter your business details to analyze</p>
          </div>

          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Business Name</label>
              <input
                type="text"
                placeholder="e.g., Leopold Cafe"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Area</label>
              <input
                type="text"
                placeholder="e.g., Churchgate"
                value={area}
                onChange={(e) => setArea(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">City</label>
              <input
                type="text"
                placeholder="e.g., Mumbai"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Twitter Query (Optional)</label>
              <input
                type="text"
                placeholder="e.g., Pizza By The Bay Mumbai"
                value={twitterQuery}
                onChange={(e) => setTwitterQuery(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Months Back</label>
              <input
                type="number"
                min="1"
                value={monthsBack}
                onChange={(e) => setMonthsBack(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <button
              type="submit"
              disabled={isRefreshing || !businessName.trim() || !area.trim() || !city.trim()}
              className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isRefreshing ? "Loading..." : "Analyze"}
            </button>
          </form>
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-muted-foreground">
        Loading dashboard...
      </div>
    )
  }

  return (
    <DashboardProvider data={dashboardData} isMarketLoading={isMarketLoading}>
      <div className="flex h-screen overflow-hidden bg-background">
      <DashboardSidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        mobileOpen={mobileSidebarOpen}
        onMobileClose={() => setMobileSidebarOpen(false)}
      />

      {/* Right column: sticky header + scrollable content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader activeTab={activeTab} onRefresh={handleRefresh} isLoading={isRefreshing} />

        <main className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="px-6 py-6">
            {contentMap[activeTab]}
          </div>
        </main>
      </div>
      </div>
    </DashboardProvider>
  )
}
