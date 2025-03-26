import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <header className="flex justify-between items-center mb-10">
          <h1 className="text-4xl font-bold">Daily Heavens</h1>
          <Button variant="outline" asChild>
            <a href="/dashboard">View Dashboard</a>
          </Button>
        </header>

        <div className="max-w-3xl mx-auto">
          <Card className="shadow-md">
            <CardHeader>
              <CardTitle>Birth Chart Calculator</CardTitle>
              <CardDescription>Enter your birth details to generate your chart</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6">
                <div className="grid gap-2">
                  <Label htmlFor="date">Birth Date</Label>
                  <Input id="date" type="date" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="time">Birth Time</Label>
                  <Input id="time" type="time" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="zipcode">Birth Place Zip Code</Label>
                  <Input 
                    id="zipcode" 
                    type="text" 
                    placeholder="Enter zip code"
                    maxLength={5}
                    pattern="[0-9]*"
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full">Calculate Birth Chart</Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
