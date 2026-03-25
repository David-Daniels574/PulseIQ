"use client"

import { useState, useEffect } from "react"
import { Bell, CalendarDays, CheckCircle2, ChevronDown, User } from "lucide-react"
import { useDashboardData } from "@/hooks/use-dashboard-data"

const PAGE_TITLES: Record<string, { title: string }> = {
  overall:         { title: "Overview" },
  competitors:     { title: "Competitor Analysis" },
  market:          { title: "Market Intelligence" },
  swot:            { title: "SWOT Analysis" },
  pestel:          { title: "PESTEL Analysis" },
  fourps:          { title: "4 P's Framework" },
  bcg:             { title: "BCG Matrix" },
  ansoff:          { title: "Ansoff Matrix" },
  orm:             { title: "ORM Console" },
  social:          { title: "Trend Tracker" },
  reporting:       { title: "Advanced Reports" },
  recommendations: { title: "Action Plan" },
}

interface DashboardHeaderProps {
  activeTab?: string
  onRefresh?: () => void
  isLoading?: boolean
}

export function DashboardHeader({ activeTab = "overall" }: DashboardHeaderProps) {
  const [mounted, setMounted] = useState(false)
  const { businessInfo } = useDashboardData()

  useEffect(() => {
    setMounted(true)
  }, [])

  const page = PAGE_TITLES[activeTab] ?? PAGE_TITLES["overall"]

  return (
    <header className="flex h-[60px] shrink-0 items-center justify-between border-b px-5 gap-3"
      style={{ backgroundColor: "hsl(var(--bg-sidebar))", borderColor: "hsl(var(--border-subtle))" }}
    >
      {/* Left: page title + subtitle */}
      <div className="min-w-0">
        <h1 className="font-serif text-[18px] font-bold leading-tight tracking-tight truncate"
          style={{ color: "hsl(var(--text-primary))" }}>
          {page.title}
        </h1>
        <p className="text-[11px] leading-tight truncate" style={{ color: "hsl(var(--text-muted))" }}>
          {businessInfo.name}
        </p>
      </div>

      {/* Center: Welcome badge */}
      <div className="hidden sm:flex shrink-0 items-center gap-1.5 rounded-full border border-border bg-secondary px-3.5 py-1.5 text-[13px] font-medium text-foreground">
        <CheckCircle2 className="h-4 w-4 text-chart-2 fill-chart-2/20" strokeWidth={2} />
        Welcome back!
      </div>

      {/* Right: date range + bell + user */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Date range */}
        <div className="hidden md:flex items-center gap-1.5 rounded-lg border border-border bg-secondary px-3 py-1.5 text-[12px] text-muted-foreground">
          <CalendarDays className="h-3.5 w-3.5" />
          <span>Jun 1, 2024 — Nov 30, 2024</span>
        </div>

        {/* Bell */}
        <button className="relative flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors">
          <Bell className="h-4 w-4" />
          {mounted && (
            <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-primary" />
          )}
        </button>

        {/* User avatar */}
        <button className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-2.5 py-1.5 text-[12px] font-medium text-foreground hover:bg-secondary/80 transition-colors">
          <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-[11px] font-bold text-primary-foreground">
            C
          </div>
          <span className="hidden sm:inline">Chef Admin</span>
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
        </button>
      </div>
    </header>
  )
}
