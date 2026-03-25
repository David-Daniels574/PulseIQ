"use client"

import { useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Star, MessageSquare, Clock, TrendingUp, AlertCircle, Send, Sparkles } from "lucide-react"
import { useDashboardData } from "@/hooks/use-dashboard-data"
import { generateResponseTemplate, publishReviewReply } from "@/services/dashboard.service"
import { format } from "date-fns"

export function ORMIntegration() {
  const { ormData, businessInfo } = useDashboardData()
  const [selectedReview, setSelectedReview] = useState<typeof ormData.reviews[0] | null>(null)
  const [responseText, setResponseText] = useState("")
  const [sentimentFilter, setSentimentFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [reviews, setReviews] = useState(ormData.reviews)
  const [isGeneratingTemplate, setIsGeneratingTemplate] = useState(false)
  const [isPublishing, setIsPublishing] = useState(false)
  const [dialogError, setDialogError] = useState<string | null>(null)

  useEffect(() => {
    setReviews(ormData.reviews)
  }, [ormData.reviews])

  const filteredReviews = useMemo(() => reviews.filter(review => {
    const matchesSentiment = sentimentFilter === "all" || review.sentiment === sentimentFilter
    const matchesStatus = statusFilter === "all" || review.status === statusFilter
    return matchesSentiment && matchesStatus
  }), [reviews, sentimentFilter, statusFilter])

  const handleRespond = async (review: typeof ormData.reviews[0]) => {
    setSelectedReview(review)
    setDialogError(null)
    setIsGeneratingTemplate(true)

    try {
      const resp = await generateResponseTemplate({
        aspect: review.aspect,
        sentiment: review.sentiment,
        business_name: businessInfo.name || "the business",
      })
      setResponseText(resp.response_template)
    } catch (error) {
      const fallbackTemplate = review.sentiment === "Negative"
        ? `Thank you for taking the time to share your feedback about ${review.aspect.toLowerCase()}. We sincerely apologize for not meeting your expectations. We take your comments seriously and are actively working to improve. We would love the opportunity to make things right - please feel free to reach out directly so we can address your concerns personally.`
        : `Thank you so much for your wonderful feedback! We're thrilled to hear that you enjoyed your experience with us, especially regarding ${review.aspect.toLowerCase()}. Your kind words mean a lot to our team. We look forward to welcoming you back soon!`
      setResponseText(fallbackTemplate)
      setDialogError(error instanceof Error ? error.message : "Failed to generate AI response template.")
    } finally {
      setIsGeneratingTemplate(false)
    }
  }

  const closeDialog = () => {
    setSelectedReview(null)
    setResponseText("")
    setDialogError(null)
  }

  const handlePublish = async () => {
    if (!selectedReview || !responseText.trim()) return

    setIsPublishing(true)
    setDialogError(null)
    try {
      const publishResp = await publishReviewReply({
        review_id: selectedReview.id,
        source: selectedReview.source,
        response_text: responseText,
        business_name: businessInfo.name,
        place_id: businessInfo.place_id,
        original_review_text: selectedReview.text,
      })

      if (publishResp.requires_redirect && publishResp.redirect_url) {
        const opened = window.open(publishResp.redirect_url, "_blank", "noopener,noreferrer")
        if (!opened) {
          setDialogError("Popup blocked. Please allow popups and try again.")
          return
        }
      }

      setReviews((prev) => prev.map((r) => (
        r.id === selectedReview.id ? { ...r, status: "Responded" } : r
      )))
      closeDialog()
    } catch (error) {
      setDialogError(error instanceof Error ? error.message : "Failed to publish response.")
    } finally {
      setIsPublishing(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "Positive": return "bg-chart-2/20 text-chart-2"
      case "Negative": return "bg-chart-3/20 text-chart-3"
      default: return "bg-chart-4/20 text-chart-4"
    }
  }

  const getStatusColor = (status: string) => {
    return status === "Responded" 
      ? "bg-chart-2/20 text-chart-2" 
      : "bg-chart-4/20 text-chart-4"
  }

  return (
    <div className="space-y-6">
      {/* ORM Analytics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/50">
          <CardContent className="flex items-center gap-4 p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-chart-2/20">
              <MessageSquare className="h-6 w-6 text-chart-2" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Response Rate</p>
              <p className="text-2xl font-bold text-foreground">{ormData.analytics.responseRate}%</p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="flex items-center gap-4 p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20">
              <Clock className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Avg Response Time</p>
              <p className="text-2xl font-bold text-foreground">{ormData.analytics.avgResponseTime}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="flex items-center gap-4 p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-chart-3/20">
              <AlertCircle className="h-6 w-6 text-chart-3" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending Negative</p>
              <p className="text-2xl font-bold text-foreground">{ormData.analytics.pendingNegative}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/50">
          <CardContent className="flex items-center gap-4 p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-chart-4/20">
              <TrendingUp className="h-6 w-6 text-chart-4" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Sentiment Trend</p>
              <Badge className="mt-1 bg-chart-2/20 text-chart-2 capitalize">
                {ormData.analytics.sentimentTrend}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Review Inbox */}
      <Card className="border-border/50">
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle>Review Inbox</CardTitle>
              <CardDescription>Manage and respond to customer reviews</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
                <SelectTrigger className="w-[130px]">
                  <SelectValue placeholder="Sentiment" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sentiment</SelectItem>
                  <SelectItem value="Positive">Positive</SelectItem>
                  <SelectItem value="Negative">Negative</SelectItem>
                  <SelectItem value="Neutral">Neutral</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[130px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="Responded">Responded</SelectItem>
                  <SelectItem value="Pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="w-[80px]">Rating</TableHead>
                  <TableHead>Review</TableHead>
                  <TableHead className="hidden sm:table-cell">Aspect</TableHead>
                  <TableHead>Sentiment</TableHead>
                  <TableHead className="hidden md:table-cell">Source</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[100px]">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReviews.map((review) => (
                  <TableRow key={review.id}>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Star className={`h-4 w-4 ${review.rating >= 4 ? 'fill-chart-4 text-chart-4' : review.rating >= 3 ? 'fill-chart-4/50 text-chart-4' : 'fill-chart-3 text-chart-3'}`} />
                        <span className="font-medium">{review.rating}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <p className="line-clamp-2 max-w-[300px] text-sm">{review.text}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {format(new Date(review.date), "MMM d, yyyy")}
                      </p>
                    </TableCell>
                    <TableCell className="hidden sm:table-cell">
                      <Badge variant="outline">{review.aspect}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getSentimentColor(review.sentiment)}>
                        {review.sentiment}
                      </Badge>
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                      {review.source}
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(review.status)}>
                        {review.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button 
                        size="sm" 
                        variant={review.status === "Pending" ? "default" : "outline"}
                        onClick={() => handleRespond(review)}
                      >
                        {review.status === "Pending" ? "Respond" : "View"}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Response Composer Dialog */}
      <Dialog open={!!selectedReview} onOpenChange={() => closeDialog()}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Compose Response</DialogTitle>
            <DialogDescription>
              AI-generated response template - edit as needed before publishing
            </DialogDescription>
          </DialogHeader>
          
          {selectedReview && (
            <div className="space-y-4">
              <div className="rounded-lg bg-secondary/50 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-chart-4 text-chart-4" />
                    <span className="font-medium">{selectedReview.rating}</span>
                  </div>
                  <Badge className={getSentimentColor(selectedReview.sentiment)}>
                    {selectedReview.sentiment}
                  </Badge>
                  <Badge variant="outline">{selectedReview.aspect}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{selectedReview.text}</p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium">AI-Generated Response</span>
                </div>
                <Textarea
                  value={responseText}
                  onChange={(e) => setResponseText(e.target.value)}
                  rows={6}
                  className="resize-none"
                  disabled={isGeneratingTemplate || isPublishing}
                />
              </div>

              {dialogError && (
                <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
                  {dialogError}
                </div>
              )}
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isPublishing}>
              Cancel
            </Button>
            <Button
              className="gap-2"
              onClick={handlePublish}
              disabled={isGeneratingTemplate || isPublishing || !responseText.trim()}
            >
              <Send className="h-4 w-4" />
              {isPublishing ? "Publishing..." : "Publish Response"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
