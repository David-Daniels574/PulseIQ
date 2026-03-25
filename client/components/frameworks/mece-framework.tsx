"use client"

import { motion } from "framer-motion"
import { useDashboardData } from "@/hooks/use-dashboard-data"

const stagger = { animate: { transition: { staggerChildren: 0.05 } } }
const fadeUp = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 } }

export function MeceFramework() {
  const { meceData } = useDashboardData()

  return (
    <div className="space-y-5">
      <div className="pulse-card p-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "hsl(var(--text-muted))" }}>
            Framework
          </p>
          <h2 className="font-serif text-xl font-bold" style={{ color: "hsl(var(--text-primary))" }}>
            MECE Complaint Framework
          </h2>
          <p className="text-sm mt-1" style={{ color: "hsl(var(--text-muted))" }}>
            Pre-clustered complaint buckets refined for mutual exclusivity and exhaustive coverage.
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-wider" style={{ color: "hsl(var(--text-muted))" }}>Avg Score</p>
          <p className="font-serif text-2xl font-bold" style={{ color: "hsl(var(--accent))" }}>
            {meceData.avg_score_pct}%
          </p>
          <p className="text-xs mt-1" style={{ color: "hsl(var(--text-muted))" }}>
            Product focus: {meceData.product_focus}
          </p>
        </div>
      </div>

      {meceData.is_exhaustive_note && (
        <div className="pulse-card p-4 text-sm" style={{ color: "hsl(var(--text-primary))" }}>
          <span className="font-semibold">Coverage note: </span>
          {meceData.is_exhaustive_note}
        </div>
      )}

      <motion.div variants={stagger} initial="initial" animate="animate" className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {meceData.complaint_categories.map((item, idx) => (
          <motion.div key={`${item.category}-${idx}`} variants={fadeUp} className="pulse-card p-5">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-serif text-lg font-semibold" style={{ color: "hsl(var(--text-primary))" }}>
                {item.category}
              </h3>
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: "hsl(var(--accent) / 0.16)", color: "hsl(var(--accent))" }}>
                {item.count} mentions
              </span>
            </div>

            <p className="text-sm mt-2" style={{ color: "hsl(var(--text-muted))" }}>
              {item.description}
            </p>

            <div className="mt-3 text-xs" style={{ color: "hsl(var(--text-muted))" }}>
              Confidence: <span style={{ color: "hsl(var(--text-primary))" }}>{item.confidence}%</span>
            </div>

            {item.examples.length > 0 && (
              <div className="mt-3 space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "hsl(var(--text-muted))" }}>
                  Example Complaints
                </p>
                {item.examples.slice(0, 3).map((example, exIdx) => (
                  <div
                    key={exIdx}
                    className="rounded-lg p-2 text-sm"
                    style={{ backgroundColor: "hsl(var(--bg-elevated))", border: "1px solid hsl(var(--border-subtle))", color: "hsl(var(--text-primary))" }}
                  >
                    {example}
                  </div>
                ))}
              </div>
            )}

            {item.sources.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {item.sources.map((source) => (
                  <span
                    key={source}
                    className="text-[11px] px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: "hsl(var(--bg-elevated))", color: "hsl(var(--text-muted))", border: "1px solid hsl(var(--border-subtle))" }}
                  >
                    {source}
                  </span>
                ))}
              </div>
            )}
          </motion.div>
        ))}
      </motion.div>

      {meceData.complaint_categories.length === 0 && (
        <div className="pulse-card p-8 text-center text-sm" style={{ color: "hsl(var(--text-muted))" }}>
          No MECE categories available yet. Run business insights first, then load MECE.
        </div>
      )}
    </div>
  )
}
