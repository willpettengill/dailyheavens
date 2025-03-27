"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

// Default test user data
const defaultUser = {
  email: "wwpettengill@gmail.com",
  birthDate: "1988-06-20",
  birthTime: "04:15",
  zipCode: "01776"
}

export default function Home() {
  const router = useRouter()
  const [formData, setFormData] = useState(defaultUser)
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target
    setFormData((prev) => ({ ...prev, [id]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Format the request according to the birth chart API
      const response = await fetch("/api/birth-chart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          birth_date: formData.birthDate,
          birth_time: formData.birthTime,
          birth_place_zip: formData.zipCode,
          email: formData.email
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to generate birth chart")
      }

      const data = await response.json()
      
      // Store data in localStorage to access in dashboard
      localStorage.setItem("birthChartData", JSON.stringify(data))
      localStorage.setItem("userEmail", formData.email)
      
      // Redirect to dashboard
      router.push("/dashboard")
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setIsLoading(false)
    }
  }

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
            <form onSubmit={handleSubmit}>
              <CardContent>
                <div className="grid gap-6">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input 
                      id="email" 
                      type="email" 
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="birthDate">Birth Date</Label>
                    <Input 
                      id="birthDate" 
                      type="date" 
                      value={formData.birthDate}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="birthTime">Birth Time</Label>
                    <Input 
                      id="birthTime" 
                      type="time" 
                      value={formData.birthTime}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="zipCode">Birth Place Zip Code</Label>
                    <Input 
                      id="zipCode" 
                      type="text" 
                      placeholder="Enter zip code"
                      maxLength={5}
                      pattern="[0-9]*"
                      value={formData.zipCode}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full" type="submit" disabled={isLoading}>
                  {isLoading ? "Calculating..." : "Calculate Birth Chart"}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  )
}
