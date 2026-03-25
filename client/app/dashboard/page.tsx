"use client"

import { useState } from "react"

import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardSidebar } from "@/components/dashboard/dashboard-sidebar"

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

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1500)
  }

  return (
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
  )
}
