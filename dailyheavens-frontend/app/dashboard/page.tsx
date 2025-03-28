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
import { Nav } from "@/components/layout/nav"
import { PlanetCard } from "@/components/planet-card"
import { HouseCard } from "@/components/house-card"
import { planetIcons, signIcons } from "@/components/ui/planet-icons"

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
  const angles = birth_chart.angles;
  const interpretations = interpretation.planets;
  const aspects = interpretation.aspects || [];
  const patterns = interpretation.patterns || [];
  const elementBalance = interpretation.element_balance;
  const modalityBalance = interpretation.modality_balance;

  // Helper to check if planet is retrograde
  const isRetrograde = (planet: string) => {
    return planets[planet]?.movement?.toLowerCase() === "retrograde";
  };
  
  // Make sure we use angle data for ascendant
  const getAscendantData = () => {
    // If angles.ascendant exists and has a sign, use that
    if (angles?.ascendant?.sign && angles.ascendant.sign !== "Unknown") {
      return {
        sign: angles.ascendant.sign,
        house: "1", // Ascendant is always at the start of house 1
        degree: angles.ascendant.degrees
      };
    }
    // Otherwise fall back to planets.ascendant if it exists
    return planets.ascendant || { sign: "Unknown", house: "1", degree: 0 };
  };
  
  const ascendantData = getAscendantData();

  return (
    <>
      <Nav 
        email={user.email} 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
      />
      <div className="container mx-auto py-8 px-4">
        {activeTab === "birth-chart" ? (
          <Card>
            <CardHeader>
              <CardTitle>Your Birth Chart Placements</CardTitle>
              <CardDescription>
                These planetary positions reveal your cosmic blueprint at the moment of your birth.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <section>
                  <h3 className="text-lg font-semibold mb-4">Core Signs</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <PlanetCard
                      key="sun"
                      planet="sun"
                      sign={planets.sun?.sign}
                      house={planets.sun?.house}
                      degree={planets.sun?.degree}
                      description={planets.sun?.description}
                      retrograde={isRetrograde("sun")}
                    />
                    <PlanetCard
                      key="moon"
                      planet="moon"
                      sign={planets.moon?.sign}
                      house={planets.moon?.house}
                      degree={planets.moon?.degree}
                      description={planets.moon?.description}
                      retrograde={isRetrograde("moon")}
                    />
                    <PlanetCard
                      key="ascendant"
                      planet="ascendant"
                      sign={ascendantData.sign}
                      house={ascendantData.house}
                      degree={ascendantData.degree}
                      description="Your rising sign - how others see you"
                      retrograde={false}
                    />
                  </div>
                </section>

                <Separator />

                <section>
                  <h3 className="text-lg font-semibold mb-4">Planets</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"].map((planet) => (
                      <PlanetCard
                        key={planet}
                        planet={planet}
                        sign={planets[planet]?.sign}
                        house={planets[planet]?.house}
                        degree={planets[planet]?.degree}
                        description={planets[planet]?.description}
                        retrograde={isRetrograde(planet)}
                      />
                    ))}
                  </div>
                </section>

                <Separator />

                <section>
                  <h3 className="text-lg font-semibold mb-4">Houses</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((house) => (
                      <HouseCard
                        key={house}
                        house={house.toString()}
                        sign={houses[house]?.sign}
                        description={houses[house]?.description}
                      />
                    ))}
                  </div>
                </section>

                <Separator />

                <section>
                  <h3 className="text-lg font-semibold mb-4">Other Placements</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {["north_node", "south_node", "chiron"].map((placement) => {
                      const placementData = planets[placement];
                      // Only show the card if we have some valid data for this placement
                      if (!placementData || !placementData.sign) {
                        return null;
                      }
                      
                      return (
                        <PlanetCard
                          key={placement}
                          planet={placement}
                          sign={placementData.sign}
                          house={placementData.house?.toString()}
                          degree={placementData.degrees || 0}
                          description={placementData.description}
                          retrograde={isRetrograde(placement)}
                        />
                      );
                    })}
                  </div>
                </section>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Your Chart Interpretation</CardTitle>
              <CardDescription>
                An in-depth analysis of your birth chart revealing your unique traits and potentials.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="prose prose-invert max-w-none">
                <div className="mb-6">
                  <h3 className="text-xl font-semibold mb-2">Overview</h3>
                  <p className="text-base leading-relaxed">{interpretation.summary ? "Your birth chart reveals your cosmic blueprint at birth." : "Your birth chart shows your unique cosmic blueprint at the moment of your birth."}</p>
                </div>

                <ScrollArea className="h-[600px] rounded-md">
                  {/* Sign Descriptions Section - New */}
                  {interpretation.summary && (
                    <div className="mb-8">
                      <h4 className="text-lg font-semibold mb-2">Your Core Signs</h4>
                      <div className="space-y-4">
                        {interpretation.summary.includes("Sun in") && (
                          <div className="p-4 border border-slate-800 rounded-md bg-slate-900">
                            <h5 className="text-md font-medium mb-2 flex items-center">
                              <span className="mr-2">{planetIcons.sun}</span>
                              Sun Sign
                            </h5>
                            <p className="text-base leading-relaxed">
                              {interpretation.summary.split(". ").find((s: string) => s.trim().startsWith("Sun in"))?.trim()}
                              {interpretation.summary.split(". ").find((s: string) => s.trim().startsWith("Sun in"))?.trim()?.endsWith(".") ? "" : "."}
                            </p>
                          </div>
                        )}
                        
                        {interpretation.summary.includes("Moon in") && (
                          <div className="p-4 border border-slate-800 rounded-md bg-slate-900">
                            <h5 className="text-md font-medium mb-2 flex items-center">
                              <span className="mr-2">{planetIcons.moon}</span>
                              Moon Sign
                            </h5>
                            <p className="text-base leading-relaxed">
                              {interpretation.summary.split(". ").find((s: string) => s.trim().startsWith("Moon in"))?.trim()}
                              {interpretation.summary.split(". ").find((s: string) => s.trim().startsWith("Moon in"))?.trim()?.endsWith(".") ? "" : "."}
                            </p>
                          </div>
                        )}
                        
                        {interpretation.summary.includes("Rising Sign") && (
                          <div className="p-4 border border-slate-800 rounded-md bg-slate-900">
                            <h5 className="text-md font-medium mb-2 flex items-center">
                              <span className="mr-2">{planetIcons.ascendant}</span>
                              Rising Sign
                            </h5>
                            <p className="text-base leading-relaxed">
                              {interpretation.summary.split(". ").find((s: string) => s.trim().startsWith("Rising Sign"))?.trim()}
                              {interpretation.summary.split(". ").find((s: string) => s.trim().startsWith("Rising Sign"))?.trim()?.endsWith(".") ? "" : "."}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="mb-8">
                    <h4 className="text-lg font-semibold mb-2">Element & Modality Balance</h4>
                    {elementBalance && (
                      <div className="mb-4">
                        <h5 className="text-md font-medium">Elements</h5>
                        <p className="text-base leading-relaxed mb-2">{elementBalance.interpretation}</p>
                        <div className="flex flex-wrap gap-2 mb-4">
                          {Object.entries(elementBalance.percentages || {}).map(([element, percentage]) => (
                            <Badge key={element} variant="outline" className="py-1">
                              {element.charAt(0).toUpperCase() + element.slice(1)}: {Math.round(percentage as number)}%
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {modalityBalance && (
                      <div>
                        <h5 className="text-md font-medium">Modalities</h5>
                        <p className="text-base leading-relaxed mb-2">{modalityBalance.interpretation}</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(modalityBalance.percentages || {}).map(([modality, percentage]) => (
                            <Badge key={modality} variant="outline" className="py-1">
                              {modality.charAt(0).toUpperCase() + modality.slice(1)}: {Math.round(percentage as number)}%
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {patterns && patterns.length > 0 && (
                    <div className="mb-8">
                      <h4 className="text-lg font-semibold mb-2">Chart Patterns</h4>
                      {patterns.map((pattern: any, index: number) => (
                        <div key={index} className="mb-4">
                          <h5 className="text-md font-medium">
                            {pattern.type.charAt(0).toUpperCase() + pattern.type.slice(1)}
                            {pattern.sign && ` in ${pattern.sign}`}
                            {pattern.planets && ` (${pattern.planets.join(", ")})`}
                          </h5>
                          <p className="text-base leading-relaxed">{pattern.interpretation}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mb-8">
                    <h4 className="text-lg font-semibold mb-2">Planets</h4>
                    {interpretations.map((item: any, index: number) => (
                      <div key={index} className="mb-6">
                        <h5 className="text-md font-medium">
                          {item.planet} in {item.sign} (House {item.house})
                          {item.retrograde && <Badge className="ml-2 bg-orange-600" variant="secondary">Retrograde</Badge>}
                        </h5>
                        <p className="text-base leading-relaxed">{item.interpretation}</p>
                      </div>
                    ))}
                  </div>

                  {aspects && aspects.length > 0 && (
                    <div className="mb-8">
                      <h4 className="text-lg font-semibold mb-2">Aspects</h4>
                      <Accordion type="multiple" className="w-full">
                        {aspects.filter((aspect: any) => aspect.type !== -1 && aspect.interpretation).map((aspect: any, index: number) => (
                          <InterpretationItem 
                            key={index} 
                            title={`${aspect.planet1} ${aspect.type === 60 ? 'sextile' : 
                                   aspect.type === 90 ? 'square' : 
                                   aspect.type === 120 ? 'trine' : 
                                   aspect.type === 180 ? 'opposition' : 
                                   aspect.type === 0 ? 'conjunction' : ''} ${aspect.planet2}`}
                            description={aspect.interpretation}
                          />
                        ))}
                      </Accordion>
                    </div>
                  )}
                </ScrollArea>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
} 