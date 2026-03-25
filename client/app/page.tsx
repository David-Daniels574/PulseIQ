"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { 
  BarChart3, 
  Target, 
  Smartphone, 
  FileText, 
  Search,
  ArrowRight,
  Sparkles,
  TrendingUp,
  Users,
  Star
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"

const features = [
  {
    icon: BarChart3,
    title: "Real-time Sentiment Analysis",
    description: "AI-powered analysis of customer reviews across all major platforms with aspect-based insights."
  },
  {
    icon: Target,
    title: "8 Strategic Frameworks",
    description: "BCG Matrix, Ansoff Matrix, Competitor Analysis, and more business intelligence tools."
  },
  {
    icon: Smartphone,
    title: "Social Listening",
    description: "Monitor mentions across Instagram, Twitter, Reddit, and other social platforms."
  },
  {
    icon: FileText,
    title: "Boardroom-Ready Reports",
    description: "Export comprehensive PDF reports with visualizations and actionable recommendations."
  }
]

const stats = [
  { value: "10K+", label: "Businesses Analyzed" },
  { value: "50M+", label: "Reviews Processed" },
  { value: "98%", label: "Accuracy Rate" },
  { value: "24/7", label: "Real-time Monitoring" }
]

const categories = [
  { value: "restaurant", label: "Restaurant" },
  { value: "cafe", label: "Cafe" },
  { value: "hotel", label: "Hotel" },
  { value: "bar", label: "Bar & Lounge" },
  { value: "bakery", label: "Bakery" },
  { value: "food_truck", label: "Food Truck" }
]

export default function HomePage() {
  const router = useRouter()
  const [businessName, setBusinessName] = useState("")
  const [category, setCategory] = useState("")
  const [location, setLocation] = useState("")

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    router.push("/dashboard")
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
          <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8 lg:py-32">
            <div className="mx-auto max-w-3xl text-center">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-secondary/50 px-4 py-1.5 text-sm text-muted-foreground">
                <Sparkles className="h-4 w-4 text-primary" />
                AI-Powered Business Intelligence
              </div>
              
              <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
                360° Restaurant Oracle
              </h1>
              <p className="mt-2 text-xl font-medium text-primary sm:text-2xl">
                Convert Data into Strategy
              </p>
              <p className="mt-6 text-lg leading-relaxed text-muted-foreground">
                Transform customer reviews into strategic insights with AI-powered sentiment analysis, 
                competitor intelligence, and actionable recommendations for your business.
              </p>
            </div>

            {/* Search Form */}
            <Card className="mx-auto mt-12 max-w-4xl border-border/50 bg-card/80 shadow-xl backdrop-blur">
              <CardContent className="p-6 sm:p-8">
                <form onSubmit={handleSearch} className="space-y-6">
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="space-y-2 lg:col-span-2">
                      <label className="text-sm font-medium text-foreground">
                        Business Name
                      </label>
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                          placeholder="e.g., The Golden Fork"
                          value={businessName}
                          onChange={(e) => setBusinessName(e.target.value)}
                          className="pl-10"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">
                        Category
                      </label>
                      <Select value={category} onValueChange={setCategory}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map((cat) => (
                            <SelectItem key={cat.value} value={cat.value}>
                              {cat.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">
                        Location
                      </label>
                      <Input
                        placeholder="e.g., New York, NY"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <Button type="submit" size="lg" className="w-full gap-2 text-base">
                    Launch Intelligence Dashboard
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Stats Section */}
        <section className="border-y border-border bg-secondary/30">
          <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <p className="text-3xl font-bold text-primary sm:text-4xl">{stat.value}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 sm:py-28">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Comprehensive Business Intelligence
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Everything you need to understand your customers, outperform competitors, 
                and grow your business strategically.
              </p>
            </div>
            
            <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature, index) => (
                <Card 
                  key={index} 
                  className="group border-border/50 bg-card/50 transition-all duration-300 hover:border-primary/30 hover:shadow-lg"
                >
                  <CardContent className="p-6">
                    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                      <feature.icon className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="mb-2 text-lg font-semibold text-foreground">
                      {feature.title}
                    </h3>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="border-t border-border bg-secondary/20 py-20 sm:py-28">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                How It Works
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Get actionable insights in three simple steps
              </p>
            </div>
            
            <div className="mt-16 grid gap-8 md:grid-cols-3">
              {[
                {
                  step: "01",
                  icon: Search,
                  title: "Search Your Business",
                  description: "Enter your business name, category, and location to start the analysis."
                },
                {
                  step: "02",
                  icon: TrendingUp,
                  title: "AI Analyzes Data",
                  description: "Our AI processes reviews from multiple platforms and extracts insights."
                },
                {
                  step: "03",
                  icon: Target,
                  title: "Get Recommendations",
                  description: "Receive strategic recommendations based on sentiment and competitive analysis."
                }
              ].map((item, index) => (
                <div key={index} className="relative text-center">
                  <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-2xl font-bold text-primary-foreground">
                    {item.step}
                  </div>
                  <h3 className="mb-3 text-xl font-semibold text-foreground">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                  
                  {index < 2 && (
                    <ArrowRight className="absolute right-0 top-8 hidden h-6 w-6 -translate-x-1/2 text-muted-foreground/30 md:block" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 sm:py-28">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary to-primary/80 px-8 py-16 text-center sm:px-16">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />
              <div className="relative">
                <h2 className="text-3xl font-bold text-primary-foreground sm:text-4xl">
                  Ready to Transform Your Business?
                </h2>
                <p className="mx-auto mt-4 max-w-2xl text-lg text-primary-foreground/80">
                  Join thousands of businesses using 360° Restaurant Oracle to make data-driven decisions.
                </p>
                <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
                  <Button 
                    size="lg" 
                    variant="secondary"
                    className="gap-2 text-base"
                    onClick={() => router.push("/dashboard")}
                  >
                    View Demo Dashboard
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
