"use client"

import { motion } from "framer-motion"
import { Package, DollarSign, MapPin, Megaphone, CheckCircle2, XCircle } from "lucide-react"
import { fourPsData } from "@/lib/mock-data"

const stagger = { animate: { transition: { staggerChildren: 0.07 } } }
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } }

const pConfig = [
  {
    key: "product" as const,
    label: "Product",
    icon: Package,
    borderColor: "hsl(var(--accent))",
    bgTint: "hsl(38 82% 58% / 0.06)",
  },
  {
    key: "price" as const,
    label: "Price",
    icon: DollarSign,
    borderColor: "hsl(var(--success))",
    bgTint: "hsl(142 69% 58% / 0.06)",
  },
  {
    key: "place" as const,
    label: "Place",
    icon: MapPin,
    borderColor: "hsl(var(--info))",
    bgTint: "hsl(213 93% 68% / 0.06)",
  },
  {
    key: "promotion" as const,
    label: "Promotion",
    icon: Megaphone,
    borderColor: "hsl(var(--danger))",
    bgTint: "hsl(0 91% 71% / 0.06)",
  },
]

function ScoreRing({ score, color }: { score: number; color: string }) {
  const r = 28
  const circ = 2 * Math.PI * r
  const fill = (score / 100) * circ
  return (
    <div className="relative flex items-center justify-center w-16 h-16">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 72 72">
        <circle cx="36" cy="36" r={r} strokeWidth="5" stroke="hsl(var(--border-subtle))" fill="none" />
        <circle
          cx="36"
          cy="36"
          r={r}
          strokeWidth="5"
          stroke={color}
          fill="none"
          strokeDasharray={circ}
          strokeDashoffset={circ - fill}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
      </svg>
      <span className="absolute font-serif text-sm font-bold" style={{ color }}>
        {score}
      </span>
    </div>
  )
}

export function FourPsFramework() {
  const avgScore = Math.round(
    Object.values(fourPsData).reduce((s, d) => s + d.score, 0) / 4
  )

  return (
    <div className="space-y-5">
      {/* Summary header */}
      <div className="pulse-card p-4 flex items-center gap-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "hsl(var(--text-muted))" }}>
            Framework
          </p>
          <h2 className="font-serif text-xl font-bold" style={{ color: "hsl(var(--text-primary))" }}>
            4 P's Framework
          </h2>
          <p className="text-sm mt-1" style={{ color: "hsl(var(--text-muted))" }}>
            Marketing mix analysis for The Golden Fork
          </p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-xs uppercase tracking-wider mb-1" style={{ color: "hsl(var(--text-muted))" }}>Avg Score</p>
          <p className="font-serif text-2xl font-bold" style={{ color: "hsl(var(--accent))" }}>{avgScore}%</p>
        </div>
      </div>

      {/* P cards */}
      <motion.div variants={stagger} initial="initial" animate="animate" className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {pConfig.map(({ key, label, icon: Icon, borderColor, bgTint }) => {
          const data = fourPsData[key]
          return (
            <motion.div
              key={key}
              variants={fadeUp}
              className="pulse-card p-5 flex flex-col gap-4"
              style={{ borderTop: `3px solid ${borderColor}`, backgroundColor: bgTint }}
            >
              {/* Card header */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${borderColor}20` }}>
                  <Icon className="w-5 h-5" style={{ color: borderColor }} />
                </div>
                <div className="flex-1">
                  <h3 className="font-serif text-base font-bold" style={{ color: "hsl(var(--text-primary))" }}>
                    {label}
                  </h3>
                  <p className="text-xs" style={{ color: "hsl(var(--text-muted))" }}>{data.summary}</p>
                </div>
                <ScoreRing score={data.score} color={borderColor} />
              </div>

              {/* Highlights */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "hsl(var(--text-muted))" }}>
                  Strengths
                </p>
                <div className="space-y-1.5">
                  {data.highlights.map((h, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: "hsl(var(--success))" }} />
                      <p className="text-xs leading-relaxed" style={{ color: "hsl(var(--text-primary))" }}>{h}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gaps */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "hsl(var(--text-muted))" }}>
                  Gaps
                </p>
                <div className="space-y-1.5">
                  {data.gaps.map((g, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <XCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: "hsl(var(--danger))" }} />
                      <p className="text-xs leading-relaxed" style={{ color: "hsl(var(--text-muted))" }}>{g}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )
        })}
      </motion.div>
    </div>
  )
}
