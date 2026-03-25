"use client"

import { motion } from "framer-motion"
import { useDashboardData } from "@/hooks/use-dashboard-data"

type PestelItem = {
  factor: string
  impact: "Positive" | "Negative" | "Neutral"
  severity: "High" | "Medium" | "Low"
  description: string
  implication: string
}

const stagger = { animate: { transition: { staggerChildren: 0.05 } } }
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } }

const sectionKeys = ["political", "economic", "social", "technological", "environmental", "legal"]

function ImpactBadge({ impact }: { impact: PestelItem["impact"] }) {
  const cls = impact === "Positive" ? "badge-high" : impact === "Negative" ? "badge-low" : "badge-medium"
  return <span className={cls}>{impact}</span>
}

function SeverityDot({ severity }: { severity: PestelItem["severity"] }) {
  const color = severity === "High" ? "hsl(var(--danger))" : severity === "Medium" ? "hsl(var(--accent))" : "hsl(var(--success))"
  return (
    <span className="flex items-center gap-1 text-xs" style={{ color: "hsl(var(--text-muted))" }}>
      <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
      {severity} severity
    </span>
  )
}

export function PestelFramework() {
  const { pestelData } = useDashboardData()
  return (
    <div className="space-y-5">
      {/* Header card */}
      <div className="pulse-card p-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "hsl(var(--text-muted))" }}>
            Framework
          </p>
          <h2 className="font-serif text-xl font-bold" style={{ color: "hsl(var(--text-primary))" }}>
            PESTEL Analysis
          </h2>
          <p className="text-sm mt-1" style={{ color: "hsl(var(--text-muted))" }}>
            Macro-environmental factors affecting The Golden Fork
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-wider mb-1" style={{ color: "hsl(var(--text-muted))" }}>Factors</p>
          <p className="font-serif text-2xl font-bold" style={{ color: "hsl(var(--accent))" }}>
            {sectionKeys.reduce((acc, k) => acc + pestelData[k].items.length, 0)}
          </p>
        </div>
      </div>

      {/* Factor sections */}
      <motion.div variants={stagger} initial="initial" animate="animate" className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sectionKeys.map((key) => {
          const section = pestelData[key]
          return (
            <motion.div key={key} variants={fadeUp} className="pulse-card p-5">
              {/* Section header */}
              <div className="flex items-center gap-2 mb-3 pb-3" style={{ borderBottom: "1px solid hsl(var(--border-subtle))" }}>
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: section.color }} />
                <h3 className="font-serif text-base font-semibold" style={{ color: "hsl(var(--text-primary))" }}>
                  {section.label}
                </h3>
                <span className="ml-auto text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: `${section.color}20`, color: section.color }}>
                  {section.items.length} factors
                </span>
              </div>

              {/* Items */}
              <div className="space-y-3">
                {section.items.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl space-y-2"
                    style={{ backgroundColor: "hsl(var(--bg-elevated))", border: "1px solid hsl(var(--border-subtle))" }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-semibold leading-tight" style={{ color: "hsl(var(--text-primary))" }}>
                        {item.factor}
                      </p>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        <ImpactBadge impact={item.impact} />
                      </div>
                    </div>
                    <SeverityDot severity={item.severity} />
                    <p className="text-xs leading-relaxed" style={{ color: "hsl(var(--text-muted))" }}>
                      {item.description}
                    </p>
                    <div
                      className="text-xs p-2 rounded-lg"
                      style={{ backgroundColor: `${section.color}10`, borderLeft: `2px solid ${section.color}`, color: "hsl(var(--text-primary))" }}
                    >
                      <span className="font-semibold" style={{ color: section.color }}>Implication: </span>
                      {item.implication}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )
        })}
      </motion.div>
    </div>
  )
}
