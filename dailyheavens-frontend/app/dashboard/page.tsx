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
    // New fields for structured content
    structured_sections?: Record<string, {
      title: string;
      content: string;
      data?: any;
    }>;
    display_order?: string[];
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

// Helper to render markdown content with proper styling
const renderMarkdownSection = (content: string) => {
  if (!content) return null;
  
  // Process the markdown
  let processedHtml = content.startsWith('<') 
    ? content 
    : parseMarkdown(content);
    
  // Add styling classes
  processedHtml = processedHtml
    .replace(/<h1/g, '<h1 class="text-2xl font-semibold mb-4 text-card-foreground"')
    .replace(/<h2/g, '<h2 class="text-xl font-semibold mb-3 text-card-foreground"')
    .replace(/<h3/g, '<h3 class="text-lg font-semibold mb-2 text-card-foreground"')
    .replace(/<p>/g, '<p class="text-card-foreground mb-4">')
    .replace(/<ul>/g, '<ul class="list-disc pl-6 mb-4 space-y-2">')
    .replace(/<li>/g, '<li class="text-card-foreground">');
    
  return (
    <div 
      className="text-card-foreground"
      dangerouslySetInnerHTML={{ __html: processedHtml }} 
    />
  );
};

export default function Dashboard() {
  const router = useRouter();
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("birth-chart");

  useEffect(() => {
    const loadData = () => {
      setIsLoading(true);
      try {
        const storedDataString = localStorage.getItem('birthChartData');
        const storedEmail = localStorage.getItem('userEmail');
        
        let parsedData: ChartData | null = null;
        if (storedDataString) {
          try {
            parsedData = JSON.parse(storedDataString);
            console.log("Loaded data from localStorage:", parsedData);
          } catch (e) {
            console.error("Failed to parse birthChartData from localStorage:", e);
            localStorage.removeItem('birthChartData');
          }
        }
        
        if (parsedData) {
          setChartData(parsedData);
          setUserEmail(storedEmail);
          setIsLoading(false);
        } else {
          console.log("No valid data in localStorage, redirecting to home.");
          router.push("/");
        }
      } catch (error) {
        console.error("Error loading data from localStorage:", error);
        localStorage.removeItem('birthChartData');
        localStorage.removeItem('userEmail');
        setIsLoading(false);
        router.push("/");
      }
    };
    loadData();
  }, []);

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

  const { birth_chart, interpretation } = chartData || {};
  const planets = birth_chart?.planets || {};
  const houses = birth_chart?.houses || {};
  const angles = birth_chart?.angles || {};
  const patterns = interpretation?.patterns || [];
  const elementBalance = interpretation?.element_balance;
  const modalityBalance = interpretation?.modality_balance;
  const displayEmail = userEmail ?? "No email found";

  const isRetrograde = (planet: string) => {
    const planetData = getPlanetData(planets, planet);
    return planetData?.retrograde ?? false;
  };

  const getAscendantData = () => {
    if (angles?.ascendant?.sign && angles.ascendant.sign !== "Unknown") {
      return {
        sign: angles.ascendant.sign,
        house: "1",
        degree: angles.ascendant.degrees
      };
    }
    return planets?.ascendant ?? { sign: "Unknown", house: "1", degree: 0 };
  };
  
  const ascendantData = getAscendantData();

  return (
    <>
      <Nav 
        email={displayEmail} 
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
                      sign={getPlanetData(planets, "sun")?.sign ?? 'N/A'}
                      house={getPlanetData(planets, "sun")?.house?.toString() ?? 'N/A'}
                      degree={getPlanetData(planets, "sun")?.degree ?? 0}
                      description={getPlanetData(planets, "sun")?.description}
                      retrograde={isRetrograde("sun")}
                    />
                    <PlanetCard
                      key="moon"
                      planet="moon"
                      sign={getPlanetData(planets, "moon")?.sign ?? 'N/A'}
                      house={getPlanetData(planets, "moon")?.house?.toString() ?? 'N/A'}
                      degree={getPlanetData(planets, "moon")?.degree ?? 0}
                      description={getPlanetData(planets, "moon")?.description}
                      retrograde={isRetrograde("moon")}
                    />
                    <PlanetCard
                      key="ascendant"
                      planet="ascendant"
                      sign={ascendantData?.sign ?? 'N/A'}
                      house={ascendantData?.house?.toString() ?? '1'}
                      degree={ascendantData?.degree ?? 0}
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
                      if (!planetData) return null;
                      return (
                        <PlanetCard
                          key={planet}
                          planet={planet}
                          sign={planetData?.sign ?? 'N/A'}
                          house={planetData?.house?.toString() ?? 'N/A'}
                          degree={planetData?.degree ?? 0}
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
                        sign={houses?.[house]?.sign ?? 'N/A'}
                        description={houses?.[house]?.description}
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
                      if (!placementData || !placementData.sign) {
                        return null;
                      }
                      return (
                        <PlanetCard
                          key={placement}
                          planet={placement}
                          sign={placementData?.sign ?? 'N/A'}
                          house={placementData?.house?.toString() ?? 'N/A'}
                          degree={placementData?.degree ?? 0}
                          description={placementData?.description}
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
                {interpretation?.structured_sections && interpretation?.display_order ? (
                  interpretation.display_order.map((sectionKey) => {
                    const section = interpretation.structured_sections?.[sectionKey];
                    if (!section) {
                      console.warn(`Dashboard: Section data not found for key: ${sectionKey}`);
                      return null;
                    }

                    // Log section processing
                    console.log(`Dashboard: Processing section '${sectionKey}'. Title: '${section.title}'. Has content: ${!!section.content}, Has data: ${!!section.data}`);
                    if (section.content) {
                      console.log(`  Content for '${sectionKey}' (start):`, section.content.substring(0, 100) + "...");
                    }
                    
                    if (sectionKey === 'element_balance') {
                      const modalitySection = interpretation.structured_sections?.['modality_balance'];
                      const elementContent = section?.content;
                      const modalityContent = modalitySection?.content;
                      const elementData = section?.data as ElementBalanceData | undefined;
                      const modalityData = modalitySection?.data as ModalityBalanceData | undefined;
                      
                      return (
                        <section key="element-modality-balance">
                          <h2 className="mb-4 text-xl font-semibold">Element and Modality Balance</h2>
                          <div className="grid gap-6 mb-6 md:grid-cols-2">
                            {elementData && (
                              <ElementBalanceChart elementBalance={elementData} />
                            )}
                            {modalityData && (
                              <ModalityBalanceChart modalityBalance={modalityData} />
                            )}
                          </div>
                          {elementContent && renderMarkdownSection(elementContent)}
                          {modalityContent && renderMarkdownSection(modalityContent)}
                          <Separator className="my-6" />
                        </section>
                      );
                    }
                    
                    else if (sectionKey === 'modality_balance') {
                      return null;
                    }
                    
                    else if (sectionKey === 'house_emphasis') {
                      return (
                        <section key={sectionKey}>
                          <h2 className="mb-4 text-xl font-semibold">{section.title}</h2>
                          {renderMarkdownSection(section.content)}
                          <Separator className="my-6" />
                        </section>
                      );
                    }
                    
                    else if (sectionKey === 'sign_distribution') {
                      return null;
                    }
                    
                    else if (sectionKey === 'stelliums') {
                      return (
                        <section key={sectionKey}>
                          <h2 className="mb-4 text-xl font-semibold">{section.title}</h2>
                          
                          <div className="mb-6">
                            <SignDistributionChart 
                              signDistribution={generateSignDistribution(planets, houses)} 
                            />
                          </div>
                          
                          {renderMarkdownSection(section.content)}
                          <Separator className="my-6" />
                        </section>
                      );
                    }

                    return (
                      <section key={sectionKey}>
                        <h2 className="mb-4 text-xl font-semibold">{section.title}</h2>
                        {renderMarkdownSection(section.content)}
                        <Separator className="my-6" />
                      </section>
                    );
                  })
                ) : (
                  <>
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
                            {elementBalance?.percentages && (
                              <div className="space-y-4">
                                <ElementBalanceChart elementBalance={elementBalance as ElementBalanceData} />
                                <Card>
                                  <CardHeader className="pb-2">
                                    <CardTitle className="text-base">Element Details</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="space-y-4">
                                      {Object.entries(elementBalance.percentages).map(([element, percentage]) => (
                                        <li key={element} className="flex items-center justify-between">
                                          <span className="capitalize text-card-foreground">{element}</span>
                                          <span className="text-card-foreground">{percentage}%</span>
                                        </li>
                                      ))}
                                    </div>
                                  </CardContent>
                                </Card>
                              </div>
                            )}
                            
                            {modalityBalance?.percentages && (
                              <div className="space-y-4">
                                <ModalityBalanceChart modalityBalance={modalityBalance as ModalityBalanceData} />
                                <Card>
                                  <CardHeader className="pb-2">
                                    <CardTitle className="text-base">Modality Details</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="space-y-4">
                                      {Object.entries(modalityBalance.percentages).map(([modality, percentage]) => (
                                        <li key={modality} className="flex items-center justify-between">
                                          <span className="capitalize text-card-foreground">{modality}</span>
                                          <span className="text-card-foreground">{percentage}%</span>
                                        </li>
                                      ))}
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
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}