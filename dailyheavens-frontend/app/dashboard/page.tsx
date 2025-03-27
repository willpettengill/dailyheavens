"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

// Component for planet card in birth chart view
const PlanetCard = ({ planet, sign, house, degree }: { planet: string; sign: string; house: string; degree: number }) => {
  // Map planet names to their symbols
  const planetSymbols: Record<string, string> = {
    sun: "☉",
    moon: "☽",
    mercury: "☿",
    venus: "♀",
    mars: "♂",
    jupiter: "♃",
    saturn: "♄",
    uranus: "♅",
    neptune: "♆",
    pluto: "♇"
  };

  // Map signs to their symbols and colors
  const signData: Record<string, { symbol: string; color: string }> = {
    aries: { symbol: "♈", color: "bg-red-500" },
    taurus: { symbol: "♉", color: "bg-green-700" },
    gemini: { symbol: "♊", color: "bg-yellow-500" },
    cancer: { symbol: "♋", color: "bg-blue-300" },
    leo: { symbol: "♌", color: "bg-orange-500" },
    virgo: { symbol: "♍", color: "bg-green-500" },
    libra: { symbol: "♎", color: "bg-pink-300" },
    scorpio: { symbol: "♏", color: "bg-red-900" },
    sagittarius: { symbol: "♐", color: "bg-purple-500" },
    capricorn: { symbol: "♑", color: "bg-gray-700" },
    aquarius: { symbol: "♒", color: "bg-blue-500" },
    pisces: { symbol: "♓", color: "bg-sky-300" }
  };

  const capitalizedPlanet = planet.charAt(0).toUpperCase() + planet.slice(1);
  const capitalizedSign = sign.charAt(0).toUpperCase() + sign.slice(1);
  const signInfo = signData[sign.toLowerCase()] || { symbol: "?", color: "bg-gray-500" };

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center text-xl gap-2">
            <span className="text-3xl">{planetSymbols[planet.toLowerCase()] || planet}</span>
            {capitalizedPlanet}
          </CardTitle>
          <Badge variant="outline" className={`${signInfo.color} text-white`}>
            {signInfo.symbol}
          </Badge>
        </div>
        <CardDescription>{capitalizedSign} • House {house}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <span>Degree: {degree.toFixed(1)}°</span>
        </div>
      </CardContent>
    </Card>
  );
};

// Component for interpretation item in personality profile view
const InterpretationItem = ({ title, description }: { title: string; description: string }) => {
  return (
    <AccordionItem value={title}>
      <AccordionTrigger className="text-lg font-medium">{title}</AccordionTrigger>
      <AccordionContent>
        <p className="text-base leading-relaxed">{description}</p>
      </AccordionContent>
    </AccordionItem>
  );
};

export default function Dashboard() {
  const router = useRouter();
  const [chartData, setChartData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("birth-chart");

  useEffect(() => {
    // Check for data in localStorage
    const storedData = localStorage.getItem("birthChartData");
    const userEmail = localStorage.getItem("userEmail");
    
    if (storedData) {
      setChartData(JSON.parse(storedData));
      setIsLoading(false);
    } else {
      // If no data is found, load the test user data
      fetchDefaultUserData();
    }
  }, []);

  const fetchDefaultUserData = async () => {
    try {
      // Use the default test user data
      const response = await fetch("/api/birth-chart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          birth_date: "1988-06-20",
          birth_time: "04:15",
          birth_place_zip: "01776",
          email: "wwpettengill@gmail.com"
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch test user data");
      }

      const data = await response.json();
      setChartData(data);
      
      // Store in localStorage
      localStorage.setItem("birthChartData", JSON.stringify(data));
      localStorage.setItem("userEmail", "wwpettengill@gmail.com");
    } catch (error) {
      console.error("Error fetching test user data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-lg">Loading your cosmic data...</p>
        </div>
      </div>
    );
  }

  if (!chartData) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>No Birth Chart Data Found</CardTitle>
            <CardDescription>We couldn't find your birth chart information.</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Please return to the home page to calculate your birth chart.</p>
          </CardContent>
          <CardFooter>
            <Button onClick={() => router.push("/")} className="w-full">
              Return to Home
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // Extract data
  const { user, birth_chart, interpretation } = chartData;
  const planets = birth_chart.planets;
  const houses = birth_chart.houses;
  const interpretations = interpretation.planets;

  return (
    <div className="container mx-auto py-8 px-4">
      <header className="mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold">Your Cosmic Profile</h1>
            <p className="text-muted-foreground">
              Based on your birth details: {user.birth_date} at {user.birth_time}, {user.birth_place_zip}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Avatar>
              <AvatarFallback>{user.email.substring(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">{user.email}</p>
            </div>
          </div>
        </div>
        <Separator />
      </header>

      <Tabs
        defaultValue="birth-chart"
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-6"
      >
        <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
          <TabsTrigger value="birth-chart">Birth Chart</TabsTrigger>
          <TabsTrigger value="personality-profile">Personality Profile</TabsTrigger>
        </TabsList>

        <TabsContent value="birth-chart" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Birth Chart Placements</CardTitle>
              <CardDescription>
                These planetary positions reveal your cosmic blueprint at the moment of your birth.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(planets).map(([planet, data]: [string, any]) => (
                  <PlanetCard
                    key={planet}
                    planet={planet}
                    sign={data.sign}
                    house={data.house}
                    degree={data.degree}
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Houses</CardTitle>
              <CardDescription>
                The houses represent different areas of your life where planetary energies express themselves.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {Object.entries(houses).map(([houseNum, data]: [string, any]) => (
                  <Card key={houseNum} className="overflow-hidden">
                    <CardHeader className="p-3">
                      <CardTitle className="text-lg">House {houseNum}</CardTitle>
                    </CardHeader>
                    <CardContent className="p-3 pt-0">
                      <p className="font-medium">{data.sign}</p>
                      <p className="text-muted-foreground text-sm">{data.degree.toFixed(1)}°</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="personality-profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Personality Profile</CardTitle>
              <CardDescription>
                In-depth interpretation of your birth chart revealing your unique traits and potentials.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <h3 className="text-xl font-semibold mb-2">Summary</h3>
                <p className="text-base leading-relaxed">{interpretation.summary}</p>
              </div>

              <Accordion type="single" collapsible className="w-full">
                <h3 className="text-xl font-semibold mb-2">Planetary Influences</h3>
                <ScrollArea className="h-[400px] rounded-md border p-4">
                  {interpretations.map((item: any, index: number) => (
                    <InterpretationItem
                      key={index}
                      title={`${item.planet} in ${item.sign} (House ${item.house})`}
                      description={item.interpretation}
                    />
                  ))}
                </ScrollArea>
              </Accordion>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Aspect Patterns</CardTitle>
              <CardDescription>
                The relationships between planets reveal dynamics in your personality and life.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {interpretation.aspects.map((aspect: any, index: number) => (
                  <InterpretationItem
                    key={index}
                    title={aspect.aspect}
                    description={aspect.interpretation}
                  />
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="mt-8 text-center">
        <Button variant="outline" onClick={() => router.push("/")}>
          Calculate New Chart
        </Button>
      </div>
    </div>
  );
} 