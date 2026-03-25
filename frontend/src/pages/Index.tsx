import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { BarChart3, TrendingUp, Users, Zap } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    businessName: "",
    category: "",
    area: "",
    location: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Map formData to match Dashboard's expected structure
    navigate("/dashboard", { 
      state: { 
        businessData: {
          name: formData.businessName,
          category: formData.category,
          area: formData.area,
          location: formData.location
        }
      } 
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/10">
      {/* Hero Section */}
      <div className="container mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            GrowKaro
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            AI-powered business intelligence for hyper-local SMBs. Transform data into actionable insights.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <Card className="shadow-soft border-t-4 border-t-primary">
            <CardContent className="pt-6">
              <BarChart3 className="h-8 w-8 text-primary mb-3" />
              <h3 className="font-semibold mb-2">ABSA Analysis</h3>
              <p className="text-sm text-muted-foreground">Aspect-based sentiment analysis for deep customer insights</p>
            </CardContent>
          </Card>

          <Card className="shadow-soft border-t-4 border-t-secondary">
            <CardContent className="pt-6">
              <Users className="h-8 w-8 text-secondary mb-3" />
              <h3 className="font-semibold mb-2">Competitor Intel</h3>
              <p className="text-sm text-muted-foreground">Real-time competitive positioning and market analysis</p>
            </CardContent>
          </Card>

          <Card className="shadow-soft border-t-4 border-t-accent">
            <CardContent className="pt-6">
              <TrendingUp className="h-8 w-8 text-accent mb-3" />
              <h3 className="font-semibold mb-2">Predictive Forecasting</h3>
              <p className="text-sm text-muted-foreground">Prophet-based rating predictions for strategic planning</p>
            </CardContent>
          </Card>

          <Card className="shadow-soft border-t-4 border-t-success">
            <CardContent className="pt-6">
              <Zap className="h-8 w-8 text-success mb-3" />
              <h3 className="font-semibold mb-2">AI Recommendations</h3>
              <p className="text-sm text-muted-foreground">Actionable strategies powered by large language models</p>
            </CardContent>
          </Card>
        </div>

        {/* Input Form */}
        <Card className="max-w-2xl mx-auto shadow-strong">
          <CardHeader>
            <CardTitle>Get Started with Your Business Analysis</CardTitle>
            <CardDescription>Enter your business details to access comprehensive intelligence dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="businessName">Business Name</Label>
                <Input
                  id="businessName"
                  name="businessName"
                  placeholder="e.g., Cafe Mumbai"
                  value={formData.businessName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  name="category"
                  placeholder="e.g., Restaurant, Cafe, Retail"
                  value={formData.category}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="area">Area</Label>
                  <Input id="area" name="area" placeholder="e.g., Bandra" value={formData.area} onChange={handleChange} required />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">City</Label>
                  <Input
                    id="location"
                    name="location"
                    placeholder="e.g., Mumbai"
                    value={formData.location}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" size="lg">
                Launch Intelligence Dashboard
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Index;
