"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { TrendingUp, TrendingDown, Zap, AlertTriangle, ExternalLink } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useDashboardData } from "@/hooks/use-dashboard-data"

type SwotItem = {
  text: string
  confidence: "High" | "Medium" | "Low"
  platform: string
  sourceText: string
  sourceUrl: string
}

const stagger = { animate: { transition: { staggerChildren: 0.06 } } }
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } }

const quadrants = [
  { key: "strengths" as const,     label: "Strengths",     icon: TrendingUp,    borderColor: "hsl(var(--success))", bgColor: "hsl(142 69% 58% / 0.05)" },
  { key: "weaknesses" as const,    label: "Weaknesses",    icon: TrendingDown,  borderColor: "hsl(var(--danger))",  bgColor: "hsl(0 91% 71% / 0.05)" },
  { key: "opportunities" as const, label: "Opportunities", icon: Zap,           borderColor: "hsl(var(--accent))",  bgColor: "hsl(38 82% 58% / 0.05)" },
  { key: "threats" as const,       label: "Threats",       icon: AlertTriangle, borderColor: "hsl(var(--info))",    bgColor: "hsl(213 93% 68% / 0.05)" },
]

function ConfidenceBadge({ level }: { level: "High" | "Medium" | "Low" }) {
  const cls = level === "High" ? "badge-high" : level === "Medium" ? "badge-medium" : "badge-low"
  return <span className={cls}>{level}</span>
}

export function SwotAnalysis() {
  const { swotData } = useDashboardData()
  const [selectedSource, setSelectedSource] = useState<SwotItem | null>(null)

  const allItems = [...swotData.strengths, ...swotData.weaknesses, ...swotData.opportunities, ...swotData.threats]
  const highCount = allItems.filter((i) => i.confidence === "High").length

  return (
    <div className="space-y-5">
      {/* Confidence bar */}
      <div className="pulse-card p-4 flex items-center gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "hsl(var(--text-muted))" }}>
            SWOT Confidence
          </p>
          <p className="font-serif text-2xl font-bold" style={{ color: "hsl(var(--accent))" }}>84%</p>
        </div>
        <div className="flex-1">
          <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: "hsl(var(--bg-elevated))" }}>
            <div className="h-full rounded-full transition-all duration-700" style={{ width: "84%", backgroundColor: "hsl(var(--accent))" }} />
          </div>
          <p className="text-xs mt-1" style={{ color: "hsl(var(--text-muted))" }}>
            {highCount} of {allItems.length} insights rated High confidence · Derived from 847 reviews
          </p>
        </div>
      </div>

      {/* 2×2 Grid */}
      <motion.div variants={stagger} initial="initial" animate="animate" className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {quadrants.map(({ key, label, icon: Icon, borderColor, bgColor }) => (
          <motion.div
            key={key}
            variants={fadeUp}
            className="pulse-card p-5 flex flex-col"
            style={{ borderLeft: `3px solid ${borderColor}`, backgroundColor: bgColor }}
          >
            {/* Quadrant header */}
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${borderColor}20` }}>
                <Icon className="w-4 h-4" style={{ color: borderColor }} />
              </div>
              <h2 className="font-serif text-lg font-semibold" style={{ color: "hsl(var(--text-primary))" }}>
                {label}
              </h2>
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full"
                style={{ backgroundColor: `${borderColor}15`, color: borderColor }}>
                {swotData[key].length}
              </span>
            </div>

            {/* Items */}
            <div className="space-y-3 flex-1">
              {swotData[key].map((item, idx) => (
                <div
                  key={idx}
                  className="flex flex-col gap-1.5 p-3 rounded-xl"
                  style={{ backgroundColor: "hsl(var(--bg-card))", border: "1px solid hsl(var(--border-subtle))" }}
                >
                  <p className="text-sm leading-relaxed" style={{ color: "hsl(var(--text-primary))" }}>{item.text}</p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <ConfidenceBadge level={item.confidence} />
                    <button
                      onClick={() => setSelectedSource(item)}
                      className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium transition-all duration-150 hover:opacity-80"
                      style={{
                        backgroundColor: "hsl(var(--bg-elevated))",
                        border: "1px solid hsl(var(--border-subtle))",
                        color: "hsl(var(--text-muted))",
                      }}
                    >
                      <ExternalLink className="w-2.5 h-2.5" />
                      {item.platform}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Source Dialog */}
      <Dialog open={!!selectedSource} onOpenChange={() => setSelectedSource(null)}>
        <DialogContent
          style={{
            backgroundColor: "hsl(var(--bg-elevated))",
            border: "1px solid hsl(var(--border-subtle))",
            color: "hsl(var(--text-primary))",
          }}
        >
          <DialogHeader>
            <DialogTitle className="font-serif" style={{ color: "hsl(var(--text-primary))" }}>
              Source Citation
            </DialogTitle>
          </DialogHeader>
          {selectedSource && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-1 rounded-full font-medium"
                  style={{ backgroundColor: "hsl(var(--accent) / 0.15)", color: "hsl(var(--accent))" }}>
                  {selectedSource.platform}
                </span>
                <ConfidenceBadge level={selectedSource.confidence} />
              </div>
              <div className="p-4 rounded-xl" style={{ backgroundColor: "hsl(var(--bg-card))", border: "1px solid hsl(var(--border-subtle))" }}>
                <p className="text-sm leading-relaxed italic" style={{ color: "hsl(var(--text-primary))" }}>
                  &ldquo;{selectedSource.sourceText}&rdquo;
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "hsl(var(--text-muted))" }}>
                  Insight derived from this source:
                </p>
                <p className="text-sm" style={{ color: "hsl(var(--text-primary))" }}>{selectedSource.text}</p>
              </div>
              <a
                href={selectedSource.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-amber inline-flex items-center gap-2 px-4 py-2 text-sm w-full justify-center"
              >
                <ExternalLink className="w-4 h-4" />
                View Original Source
              </a>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
