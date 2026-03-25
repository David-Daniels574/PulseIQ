"use client"
import React, { createContext, useContext } from "react"
import { DashboardData } from "@/services/dashboard.service"

type DashboardContextValue = DashboardData & {
  isMarketLoading: boolean
}

const DashboardContext = createContext<DashboardContextValue | null>(null)

export function DashboardProvider({
  children,
  data,
  isMarketLoading = false,
}: {
  children: React.ReactNode
  data: DashboardData
  isMarketLoading?: boolean
}) {
  return (
    <DashboardContext.Provider value={{ ...data, isMarketLoading }}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboardData() {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error("useDashboardData must be used within DashboardProvider")
  }
  return context
}
