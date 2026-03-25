"use client"

import { useState } from "react"
import {
  BarChart3,
  Users,
  Globe,
  Lightbulb,
  Grid3X3,
  MessageSquareText,
  Radio,
  FileBarChart,
  Target,
  ChevronLeft,
  ChevronRight,
  Zap,
  X,
  Settings,
  TrendingUp,
  ShoppingBag,
  Globe2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { businessInfo } from "@/lib/mock-data"

const navGroups = [
  {
    label: "Analytics",
    items: [
      { id: "overall",     label: "Overall Analysis",    icon: BarChart3,        description: "Sentiment & key metrics" },
      { id: "competitors", label: "Competitors",          icon: Users,            description: "Competitive benchmarking" },
      { id: "market",      label: "Market Intelligence",  icon: Globe,            description: "News & forecasts" },
    ],
  },
  {
    label: "Strategy",
    items: [
      { id: "swot",   label: "SWOT Analysis",   icon: TrendingUp,  description: "Strengths, Weaknesses, Opportunities, Threats" },
      { id: "pestel", label: "PESTEL",           icon: Globe2,      description: "Macro-environmental analysis" },
      { id: "fourps", label: "4 P's Framework",  icon: ShoppingBag, description: "Product, Price, Place, Promotion" },
      { id: "bcg",    label: "BCG Matrix",       icon: Grid3X3,     description: "Menu portfolio analysis" },
      { id: "ansoff", label: "Ansoff Matrix",    icon: Target,      description: "Growth strategy planning" },
    ],
  },
  {
    label: "Engagement",
    items: [
      { id: "orm",    label: "ORM Integration",  icon: MessageSquareText, description: "Review management" },
      { id: "social", label: "Social Listening",  icon: Radio,             description: "Platform mentions" },
    ],
  },
  {
    label: "Insights",
    items: [
      { id: "reporting",       label: "Advanced Reports", icon: FileBarChart, description: "Trends & exports" },
      { id: "recommendations", label: "Action Plan",      icon: Lightbulb,    description: "Prioritised actions" },
    ],
  },
]

interface DashboardSidebarProps {
  activeTab: string
  onTabChange: (id: string) => void
  mobileOpen?: boolean
  onMobileClose?: () => void
}

function SidebarContent({
  activeTab,
  onTabChange,
  collapsed,
  setCollapsed,
  onMobileClose,
}: {
  activeTab: string
  onTabChange: (id: string) => void
  collapsed: boolean
  setCollapsed: (v: boolean) => void
  onMobileClose?: () => void
}) {
  const handleSelect = (id: string) => {
    onTabChange(id)
    onMobileClose?.()
  }

  return (
    <div className="flex h-full flex-col bg-sidebar text-sidebar-foreground">
      {/* ── Brand header ── */}
      <div
        className={cn(
          "flex shrink-0 items-center border-b border-sidebar-border transition-all duration-300",
          collapsed ? "h-[60px] justify-center px-0" : "h-[60px] gap-3 px-4"
        )}
      >
        {/* Lightning bolt logo — amber on dark, matches PulseIQ */}
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-[0_0_12px_2px_oklch(0.74_0.17_62/0.35)]">
          <Zap className="h-4 w-4 fill-sidebar-primary-foreground" strokeWidth={0} />
        </div>

        {!collapsed && (
          <>
            <span className="flex-1 font-serif text-base font-bold tracking-tight text-sidebar-foreground select-none">
              PulseIQ
            </span>

            {/* Mobile close */}
            {onMobileClose && (
              <button
                onClick={onMobileClose}
                className="ml-auto flex h-7 w-7 items-center justify-center rounded-md text-sidebar-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground lg:hidden"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </>
        )}
      </div>

      {/* ── Business identity card ── */}
      {!collapsed && (
        <div className="shrink-0 border-b border-sidebar-border px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sidebar-accent text-sm font-semibold text-sidebar-foreground">
              {businessInfo.name.charAt(0)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold leading-tight text-sidebar-foreground">
                {businessInfo.name}
              </p>
              <p className="truncate text-[11px] leading-tight text-sidebar-muted-foreground mt-0.5">
                {businessInfo.category}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Navigation groups ── */}
      <nav className="flex-1 overflow-y-auto py-2 scrollbar-thin">
        <ul className="flex flex-col" role="list">
          {navGroups.map((group) => (
            <li key={group.label} className="mb-1">
              {!collapsed && (
                <p className="mb-1 px-4 pt-3 text-[10px] font-semibold uppercase tracking-widest text-sidebar-muted-foreground/50">
                  {group.label}
                </p>
              )}
              {collapsed && <div className="my-1.5 mx-3 h-px bg-sidebar-border/50" />}

              <ul className="flex flex-col gap-0.5 px-2" role="list">
                {group.items.map((item) => {
                  const Icon = item.icon
                  const isActive = activeTab === item.id
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => handleSelect(item.id)}
                        title={collapsed ? item.label : undefined}
                        aria-current={isActive ? "page" : undefined}
                        className={cn(
                          "group relative flex w-full items-center rounded-lg text-[13px] font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring",
                          collapsed
                            ? "h-9 w-full justify-center px-0"
                            : "gap-3 px-3 py-2",
                          isActive
                            ? "bg-sidebar-primary/90 text-sidebar-primary-foreground shadow-sm"
                            : "text-sidebar-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                        )}
                      >
                        {/* Active left bar */}
                        {isActive && !collapsed && (
                          <span className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-r bg-sidebar-primary-foreground/50" />
                        )}

                        <Icon
                          className={cn(
                            "shrink-0 h-4 w-4 transition-transform duration-150",
                            !isActive && "group-hover:scale-110"
                          )}
                        />

                        {!collapsed && (
                          <span className="truncate leading-tight">{item.label}</span>
                        )}
                      </button>
                    </li>
                  )
                })}
              </ul>
            </li>
          ))}
        </ul>
      </nav>

      {/* ── Footer ── */}
      <div className="shrink-0 border-t border-sidebar-border">
        {/* Settings row */}
        {!collapsed && (
          <div className="px-2 py-1.5">
            <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-[13px] font-medium text-sidebar-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </button>
          </div>
        )}

        {/* Collapse toggle + version */}
        <div className={cn("flex items-center border-t border-sidebar-border px-4 py-3", collapsed && "justify-center px-2")}>
          {!collapsed && (
            <span className="flex-1 text-[10px] text-sidebar-muted-foreground/50 font-medium">
              PulseIQ v1.0 MVP
            </span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="flex h-7 w-7 items-center justify-center rounded-md text-sidebar-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export function DashboardSidebar({
  activeTab,
  onTabChange,
  mobileOpen,
  onMobileClose,
}: DashboardSidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={cn(
          "relative hidden shrink-0 border-r border-sidebar-border bg-sidebar transition-[width] duration-300 ease-in-out lg:flex lg:flex-col",
          collapsed ? "w-[60px]" : "w-[220px]"
        )}
      >
        <SidebarContent
          activeTab={activeTab}
          onTabChange={onTabChange}
          collapsed={collapsed}
          setCollapsed={setCollapsed}
        />
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
            onClick={onMobileClose}
            aria-hidden="true"
          />
          <aside className="fixed inset-y-0 left-0 z-50 flex w-[220px] flex-col border-r border-sidebar-border bg-sidebar shadow-xl lg:hidden">
            <SidebarContent
              activeTab={activeTab}
              onTabChange={onTabChange}
              collapsed={false}
              setCollapsed={() => {}}
              onMobileClose={onMobileClose}
            />
          </aside>
        </>
      )}
    </>
  )
}
