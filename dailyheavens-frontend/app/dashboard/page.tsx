"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Nav } from "@/components/layout/nav"
import { PlanetCard } from "@/components/planet-card"
import { HouseCard } from "@/components/house-card"
import { marked } from "marked"
import React from "react"
import { 
  ElementBalanceChart, 
  ModalityBalanceChart, 
  SignDistributionChart,
  ElementBalanceData, 
  ModalityBalanceData,
  SignDistributionData,
  BoilerplateStackedBarChart
} from "@/components/element-modality-charts"

interface ChartData {
  user: {
    email: string;
  };
  birth_chart: {
    planets: Record<string, {
      sign: string;
      house: string;
      degree: number;
      description?: string;
      retrograde?: boolean;
    }>;
    houses: Record<string, {
      sign: string;
      description?: string;
    }>;
    angles: Record<string, {
      sign: string;
      degrees: number;
    }>;
  };
  interpretation: {
    overall?: string;
    element_balance?: {
      percentages?: Record<string, number>;
      dominant?: string;
      lacking?: string[] | number;
    };
    modality_balance?: {
      percentages?: Record<string, number>;
      dominant?: string;
      lacking?: string[] | number;
    };
    patterns?: Array<{
      name: string;
      description: string;
    }>;
  };
}

// Helper to parse markdown and return HTML
const parseMarkdown = (content: string): string => {
  if (!content) return '';
  
  // If the content is already HTML (starts with < and ends with >), return it as is
  if (content.trim().startsWith('<') && content.trim().endsWith('>')) {
    return content;
  }
  
  // Otherwise, parse it as markdown
  return marked.parse(content) as string;
};

// Add this helper function for consistent planet data access
const getPlanetData = (planets: Record<string, {
  sign: string;
  house: string;
  degree: number;
  description?: string;
  retrograde?: boolean;
}>, planetName: string) => {
  // Try capitalized first (Mercury, Venus, etc.)
  const capitalized = planetName.charAt(0).toUpperCase() + planetName.slice(1).toLowerCase();
  
  // Then try all lowercase (mercury, venus, etc.)
  const lowercase = planetName.toLowerCase();
  
  // Return the first one that exists
  return planets[capitalized] || planets[lowercase];
};

// Add this utility function after other helper functions
const generateSignDistribution = (
  planets: Record<string, {
    sign?: string;
    house?: string;
    degree?: number;
    description?: string;
    retrograde?: boolean;
  }>, 
  houses: Record<string, {
    sign?: string;
    description?: string;
  }>
): SignDistributionData => {
  const planetCounts: Record<string, number> = {};
  const houseCounts: Record<string, number> = {};
  
  // Count planets in each sign
  Object.values(planets).forEach(planet => {
    if (planet && planet.sign) {
      const sign = planet.sign.toLowerCase();
      planetCounts[sign] = (planetCounts[sign] || 0) + 1;
    }
  });
  
  // Count houses in each sign
  Object.values(houses).forEach(house => {
    if (house && house.sign) {
      const sign = house.sign.toLowerCase();
      houseCounts[sign] = (houseCounts[sign] || 0) + 1;
    }
  });
  
  return {
    planets: planetCounts,
    houses: houseCounts
  };
};

export default function Dashboard() {
  const router = useRouter();
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("birth-chart");

  useEffect(() => {
    // Clear potentially outdated data from localStorage on mount
    // to ensure fresh data is fetched if needed.
    // localStorage.removeItem('birthChartData'); // <<< REMOVED THIS LINE
    // console.log("Cleared birthChartData from localStorage.");

    const loadData = async () => {
      const storedData = localStorage.getItem('birthChartData');
      if (storedData) {
        const parsedData = JSON.parse(storedData);
        console.log("Loaded data from localStorage:", parsedData);
        console.log("Interpretation data:", parsedData.interpretation);
        setChartData(parsedData);
        setIsLoading(false);
      } else {
        // If no data is found, load the test user data
        console.log("No data in localStorage, fetching default user data."); // Added log
        fetchDefaultUserData();
      }
    };
    loadData();
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
      console.log("Complete API response:", data);
      console.log("Interpretation data structure:", data?.interpretation);
      
      // Extract overall interpretation from the API response structure
      const overall = data?.interpretation?.overall;
      
      // Update the main chartData state which includes the interpretation
      if (overall) {
        console.log("Found overall interpretation, updating chartData state.");
        // Construct the new state carefully
        const newState = {
          ...data, // Spread base data (user, birth_chart etc.)
          interpretation: { 
            // Safely spread existing interpretation fields if data.interpretation exists
            ...(data.interpretation || {}),
            overall: overall // Explicitly set overall
          }
        };
        setChartData(newState);
        localStorage.setItem("birthChartData", JSON.stringify(newState)); // Store the updated state
      } else {
        console.log("No overall interpretation found in API response, setting chartData without it.");
        // Ensure interpretation object exists even if overall is missing
        const newState = {
          ...data,
          interpretation: {
            ...(data.interpretation || {}),
            overall: null // Explicitly set overall to null
          }
        };
        setChartData(newState);
        localStorage.setItem("birthChartData", JSON.stringify(newState)); // Store the updated state
      }
      
      // Store userEmail separately if needed (or handle within chartData)
      localStorage.setItem("userEmail", data.user?.email || "wwpettengill@gmail.com");
    } catch (error) {
      console.error("Error fetching test user data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto border-b-2 rounded-full animate-spin border-primary"></div>
          <p className="mt-4 text-lg">Loading your cosmic data...</p>
        </div>
      </div>
    );
  }

  if (!chartData) {
    return (
      <div className="container px-4 py-8 mx-auto">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>No Birth Chart Data Found</CardTitle>
            <CardDescription>We couldn&apos;t find your birth chart information.</CardDescription>
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
  const { user, birth_chart, interpretation } = chartData || {};
  console.log("Extracted interpretation:", interpretation);
  console.log("Interpretation overall property:", interpretation?.overall);
  const planets = birth_chart?.planets || {};
  const houses = birth_chart?.houses || {};
  const angles = birth_chart?.angles || {};
  const patterns = interpretation?.patterns || [];
  const elementBalance = interpretation?.element_balance;
  const modalityBalance = interpretation?.modality_balance;

  // Add debugging
  console.log("=== Retrograde Debug ===");
  console.log("Mercury data:", planets["Mercury"] || planets["mercury"]);
  console.log("Venus data:", planets["Venus"] || planets["venus"]);
  console.log("Saturn data:", planets["Saturn"] || planets["saturn"]);
  
  // Helper to check if planet is retrograde
  const isRetrograde = (planet: string) => {
    // Handle both capitalized and lowercase planet names
    const planetData = getPlanetData(planets, planet);
    console.log(`Checking retrograde for ${planet}:`, planetData?.retrograde);
    return planetData?.retrograde || false;
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

  // Log the interpretation state just before rendering
  console.log("Rendering Dashboard - interpretation state:", interpretation);

  return (
    <>
      <Nav 
        email={user.email} 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
      />
      <div className="container px-4 py-8 mx-auto">
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
                  <h3 className="mb-4 text-lg font-semibold">Core Signs</h3>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    <PlanetCard
                      key="sun"
                      planet="sun"
                      sign={getPlanetData(planets, "sun")?.sign}
                      house={getPlanetData(planets, "sun")?.house}
                      degree={getPlanetData(planets, "sun")?.degree}
                      description={getPlanetData(planets, "sun")?.description}
                      retrograde={isRetrograde("sun")}
                    />
                    <PlanetCard
                      key="moon"
                      planet="moon"
                      sign={getPlanetData(planets, "moon")?.sign}
                      house={getPlanetData(planets, "moon")?.house}
                      degree={getPlanetData(planets, "moon")?.degree}
                      description={getPlanetData(planets, "moon")?.description}
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
                  <h3 className="mb-4 text-lg font-semibold">Planets</h3>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    {["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"].map((planet) => {
                      const planetData = getPlanetData(planets, planet);
                      return (
                        <PlanetCard
                          key={planet}
                          planet={planet}
                          sign={planetData?.sign}
                          house={planetData?.house?.toString()}
                          degree={planetData?.degree || 0}
                          description={planetData?.description}
                          retrograde={isRetrograde(planet)}
                        />
                      );
                    })}
                  </div>
                </section>

                <Separator />

                <section>
                  <h3 className="mb-4 text-lg font-semibold">Houses</h3>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
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
                  <h3 className="mb-4 text-lg font-semibold">Other Placements</h3>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    {["north_node", "south_node", "chiron"].map((placement) => {
                      const placementData = getPlanetData(planets, placement);
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
                          degree={placementData.degree || 0}
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
            <CardContent>
              <div className="space-y-6">
                {/* Overall Interpretation Section */}
                {interpretation?.overall && (
                  <section className="text-card-foreground">
                    <div className="space-y-4">
                      {interpretation.overall.startsWith('<') ? (
                        <div 
                          className="text-card-foreground"
                          dangerouslySetInnerHTML={{ 
                            __html: interpretation.overall
                              .replace(/<h1/g, '<h1 class="text-2xl font-semibold mb-4 text-card-foreground"')
                              .replace(/<h2/g, '<h2 class="text-xl font-semibold mb-3 text-card-foreground"')
                              .replace(/<h3/g, '<h3 class="text-lg font-semibold mb-2 text-card-foreground"')
                              .replace(/<p>/g, '<p class="text-card-foreground mb-4">')
                              .replace(/<ul>/g, '<ul class="list-disc pl-6 mb-4 space-y-2">')
                              .replace(/<li>/g, '<li class="text-card-foreground">')
                          }} 
                        />
                      ) : (
                        <div 
                          className="text-card-foreground"
                          dangerouslySetInnerHTML={{ 
                            __html: parseMarkdown(interpretation.overall)
                              .replace(/<h1/g, '<h1 class="text-2xl font-semibold mb-4 text-card-foreground"')
                              .replace(/<h2/g, '<h2 class="text-xl font-semibold mb-3 text-card-foreground"')
                              .replace(/<h3/g, '<h3 class="text-lg font-semibold mb-2 text-card-foreground"')
                              .replace(/<p>/g, '<p class="text-card-foreground mb-4">')
                              .replace(/<ul>/g, '<ul class="list-disc pl-6 mb-4 space-y-2">')
                              .replace(/<li>/g, '<li class="text-card-foreground">')
                          }} 
                        />
                      )}
                    </div>
                  </section>
                )}

                {(elementBalance || modalityBalance) && (
                  <>
                    <Separator />
                    <section>
                      <h3 className="mb-4 text-lg font-semibold">Element & Modality Balance</h3>
                      <div className="grid gap-4 md:grid-cols-2">
                        {elementBalance && elementBalance.percentages && (
                          <div className="space-y-4">
                            <ElementBalanceChart elementBalance={elementBalance as ElementBalanceData} />
                            <Card>
                              <CardHeader className="pb-2">
                                <CardTitle className="text-base">Element Details</CardTitle>
                              </CardHeader>
                              <CardContent>
                                <div className="space-y-4">
                                  {/* Display percentages */}
                                  {elementBalance.percentages && (
                                    <div>
                                      <h4 className="mb-2 text-sm font-medium text-card-foreground">Distribution</h4>
                                      <ul className="space-y-1 text-sm">
                                        {Object.entries(elementBalance.percentages).map(([element, percentage]) => (
                                          <li key={element} className="flex items-center justify-between">
                                            <span className="capitalize text-card-foreground">{element}</span>
                                            <span className="text-card-foreground">{percentage}%</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {/* Display dominant element */}
                                  {elementBalance.dominant && (
                                    <div>
                                      <h4 className="mb-2 text-sm font-medium text-card-foreground">Dominant</h4>
                                      <p className="text-sm capitalize text-card-foreground">{elementBalance.dominant}</p>
                                    </div>
                                  )}
                                  
                                  {/* Display lacking elements */}
                                  {elementBalance.lacking && Array.isArray(elementBalance.lacking) && elementBalance.lacking.length > 0 && (
                                    <div>
                                      <h4 className="mb-2 text-sm font-medium text-card-foreground">Lacking</h4>
                                      <p className="text-sm text-card-foreground">
                                        {elementBalance.lacking.map(e => 
                                          typeof e === 'string' ? e.charAt(0).toUpperCase() + e.slice(1) : '').join(', ')}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        )}
                        
                        {modalityBalance && modalityBalance.percentages && (
                          <div className="space-y-4">
                            <ModalityBalanceChart modalityBalance={modalityBalance as ModalityBalanceData} />
                            <Card>
                              <CardHeader className="pb-2">
                                <CardTitle className="text-base">Modality Details</CardTitle>
                              </CardHeader>
                              <CardContent>
                                <div className="space-y-4">
                                  {/* Display percentages */}
                                  {modalityBalance.percentages && (
                                    <div>
                                      <h4 className="mb-2 text-sm font-medium text-card-foreground">Distribution</h4>
                                      <ul className="space-y-1 text-sm">
                                        {Object.entries(modalityBalance.percentages).map(([modality, percentage]) => (
                                          <li key={modality} className="flex items-center justify-between">
                                            <span className="capitalize text-card-foreground">{modality}</span>
                                            <span className="text-card-foreground">{percentage}%</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {/* Display dominant modality */}
                                  {modalityBalance.dominant && (
                                    <div>
                                      <h4 className="mb-2 text-sm font-medium text-card-foreground">Dominant</h4>
                                      <p className="text-sm capitalize text-card-foreground">{modalityBalance.dominant}</p>
                                    </div>
                                  )}
                                  
                                  {/* Display lacking modalities */}
                                  {modalityBalance.lacking && Array.isArray(modalityBalance.lacking) && modalityBalance.lacking.length > 0 && (
                                    <div>
                                      <h4 className="mb-2 text-sm font-medium text-card-foreground">Lacking</h4>
                                      <p className="text-sm text-card-foreground">
                                        {modalityBalance.lacking.map(m => 
                                          typeof m === 'string' ? m.charAt(0).toUpperCase() + m.slice(1) : '').join(', ')}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        )}
                      </div>
                    </section>
                  </>
                )}

                {patterns.length > 0 && (
                  <>
                    <Separator />
                    <section>
                      <h3 className="mb-4 text-lg font-semibold">Chart Patterns</h3>
                      <ul className="pl-6 space-y-2 list-disc text-card-foreground">
                        {patterns.map((pattern, index) => (
                          <li key={index} className="text-card-foreground">
                            <strong className="text-card-foreground">{pattern.name}:</strong> {pattern.description}
                          </li>
                        ))}
                      </ul>
                    </section>
                  </>
                )}
                
                {/* Sign Distribution Chart */}
                <>
                  <Separator />
                  <section>
                    <h3 className="mb-4 text-lg font-semibold">Sign Distribution</h3>
                    <SignDistributionChart 
                      signDistribution={generateSignDistribution(planets, houses)} 
                    />
                  </section>
                </>

                {/* Boilerplate Chart for Comparison */}
                <>
                  <Separator />
                  <section>
                    <h3 className="mb-4 text-lg font-semibold">Boilerplate Comparison Chart</h3>
                    <BoilerplateStackedBarChart />
                  </section>
                </>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}