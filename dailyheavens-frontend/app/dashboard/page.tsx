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
  SignDistributionBackendData,
  BoilerplateStackedBarChart
} from "@/components/element-modality-charts"
import { Interpretation } from "../../lib/types"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

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

// Helper to render markdown content with proper styling
const renderMarkdown = (markdownText: string | undefined | null): React.ReactNode => {
  if (!markdownText) return null;
  
  // Basic check if it looks like HTML already
  const isHtml = markdownText.trim().startsWith('<') && markdownText.trim().endsWith('>');
  let processedHtml = isHtml ? markdownText : marked.parse(markdownText) as string;

  // Apply basic prose styling for readability within CardContent
  // Note: Using prose class handles most markdown elements well
  // You might not need explicit replacements if prose covers it.
  // Example explicit replacements (if needed beyond prose):
  // processedHtml = processedHtml
  //   .replace(/<h1/g, '<h1 class="text-2xl font-semibold mb-4"')
  //   .replace(/<h2/g, '<h2 class="text-xl font-semibold mb-3"')
  //   .replace(/<p>/g, '<p class="mb-4">')
  //   .replace(/<ul>/g, '<ul class="list-disc pl-6 mb-4 space-y-1">')
  //   .replace(/<ol>/g, '<ol class="list-decimal pl-6 mb-4 space-y-1">');
    
  return (
    <div 
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
                    {["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
                      .filter(planet => planet !== 'sun' && planet !== 'moon')
                      .map((planet) => {
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
                  interpretation.display_order.map((sectionKey, index) => {
                    const section = interpretation.structured_sections?.[sectionKey];
                    console.log(`Rendering section ${index}: ${sectionKey}`, section);

                    if (!section && sectionKey !== "element_balance" && sectionKey !== "sign_distribution") {
                      console.warn(`Section data not found for key: ${sectionKey}`);
                      return null; // Don't render if section data is missing, except for handled cases
                    }

                    // Skip rendering these keys directly as they are handled within other sections
                    if (sectionKey === "sign_distribution" || sectionKey === "modality_balance") {
                      return null;
                    }
                    
                    // --- Specific Section Rendering --- //

                    if (sectionKey === "overview") {
                      // Don't render anything for overview, title is handled above
                      return null; 
                    }
                    
                    // NEW: Chart Shape Rendering
                    if (sectionKey === "chart_shape") {
                      if (!section?.content) return null; // Don't render if no content
                      return (
                        <React.Fragment key={sectionKey}>
                          <Card>
                            <CardHeader>
                              <CardTitle>{section?.title}</CardTitle>
                            </CardHeader>
                            <CardContent className="prose dark:prose-invert max-w-none">
                              {renderMarkdown(section.content)}
                            </CardContent>
                          </Card>
                          <Separator className="my-6" />
                        </React.Fragment>
                      );
                    }

                    // Core Signs Rendering (3-column layout)
                    if (sectionKey === "core_signs") {
                      const coreSignsData = section?.data;
                      
                      return (
                        <React.Fragment key={sectionKey}>
                          <Card>
                            <CardHeader>
                              <CardTitle>Know Thyself</CardTitle>
                            </CardHeader>
                            <CardContent>
                              {coreSignsData ? (
                                <div className="space-y-6">
                                  {coreSignsData.sun && (
                                    <div className="space-y-2">
                                      <div className="text-sm prose-sm prose text-muted-foreground dark:prose-invert max-w-none">
                                          {renderMarkdown(coreSignsData.sun.interpretation)}
                                      </div>
                                    </div>
                                  )}
                                  {coreSignsData.moon && (
                                    <div className="space-y-2">
                                       <div className="text-sm prose-sm prose text-muted-foreground dark:prose-invert max-w-none">
                                          {renderMarkdown(coreSignsData.moon.interpretation)}
                                      </div>
                                    </div>
                                  )}
                                  {coreSignsData.ascendant && (
                                    <div className="space-y-2">
                                       <div className="text-sm prose-sm prose text-muted-foreground dark:prose-invert max-w-none">
                                          {renderMarkdown(coreSignsData.ascendant.interpretation)}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ) : (
                                <p>Core signs data not available.</p>
                              )}
                            </CardContent>
                          </Card>
                          {/* Keep separator after Core Signs */}
                          <Separator className="my-6" /> 
                        </React.Fragment>
                      );
                    }
                    
                    // UPDATED: Sun Sign Details Rendering (Table)
                    if (sectionKey === "sun_sign_details") {
                      const sunSignData = section?.data;
                      
                      if (!sunSignData || typeof sunSignData !== 'object' || Object.keys(sunSignData).length === 0) {
                        return null; 
                      }

                      const detailsToShow: (keyof typeof sunSignData)[] = [
                        'ruling_planet', 
                        'lucky_day',
                        'lucky_numbers', 
                        'birthstone', 
                        'best_trait'
                      ];
                      
                      const formatLabel = (key: string): string => {
                        return key.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                      };
                      
                      const formatValue = (value: any): string => {
                        return Array.isArray(value) ? value.join(', ') : String(value);
                      }

                      return (
                         <React.Fragment key={sectionKey}>
                           <Card> {/* Keep the Card wrapper */} 
                                <CardHeader>
                                  <CardTitle>{section?.title || 'Cosmic Details'}</CardTitle> 
                                  <CardDescription>Key facts and associations for your Sun sign.</CardDescription>
                                </CardHeader>
                                <CardContent>
                                  {/* Replace Badge div with Table */}
                                  <Table>
                                    {/* Optional: Add TableCaption if desired */}
                                    {/* <TableCaption>Details for your Sun sign.</TableCaption> */}
                                    <TableHeader>
                                      <TableRow>
                                        <TableHead className="w-[150px]">Detail</TableHead>
                                        <TableHead>Value</TableHead>
                                      </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                      {detailsToShow.map(key => (
                                        // Render row only if the key exists in the data
                                        sunSignData[key] ? (
                                          <TableRow key={key as string}> {/* Cast key to string for React key */} 
                                            <TableCell className="font-medium">{formatLabel(key as string)}</TableCell> {/* Cast key */} 
                                            <TableCell>{formatValue(sunSignData[key])}</TableCell>
                                          </TableRow>
                                        ) : null
                                      ))}
                                    </TableBody>
                                  </Table>
                                </CardContent>
                              </Card>
                              <Separator className="my-6" />
                         </React.Fragment>
                      );
                    }
                    
                    // Stelliums & Sign Distribution Chart Rendering
                    if (sectionKey === "stelliums") {
                      const stelliumData = section?.data as Array<{
                        location: string;
                        count: number;
                        planets?: string[];
                        interpretation_hint?: string;
                      }> | undefined;
                      
                          return (
                            <React.Fragment key={sectionKey}>
                          <Card>
                            <CardHeader>
                              {/* <CardTitle>{section?.title || 'Stelliums & Sign Distribution'}</CardTitle> <-- Removed Title */}
                            </CardHeader>
                            <CardContent className="space-y-4">
                              {/* Display Stellium Data from section.data */}
                              {stelliumData && Array.isArray(stelliumData) && stelliumData.length > 0 && (
                                <div className="space-y-3">
                                  <p className="text-sm text-muted-foreground pb-2">Areas of concentrated energy (stelliums) and the overall balance of zodiac signs in your chart.</p> {/* Moved description here */} 
                                  {stelliumData.map((stellium, index) => (
                                    <div key={index}>
                                      <h4 className="font-semibold">{stellium.location} Stellium ({stellium.count} planets)</h4>
                                      <p className="text-sm text-muted-foreground">Involving: {stellium.planets?.join(', ') || 'N/A'}</p>
                                      <p className="text-sm">{stellium.interpretation_hint || 'Strong focus in this area.'}</p>
                                    </div>
                                  ))}
                                </div>
                              )}
                              {/* Pass backend data directly to SignDistributionChart*/}
                              {interpretation.structured_sections?.['sign_distribution']?.data && (
                                // Log data being passed to SignDistributionChart
                                (() => {
                                  const signDistData = interpretation.structured_sections['sign_distribution'].data as SignDistributionBackendData;
                                  console.log("Dashboard: Passing data to SignDistributionChart:", JSON.stringify(signDistData));
                                  return <SignDistributionChart signDistribution={signDistData} />;
                                })()
                              )}
                            </CardContent>
                          </Card>
                                <Separator className="my-6" />
                        </React.Fragment>
                      );
                    }

                    // NEW: Chart Highlights Rendering (Combined Patterns & Combinations)
                    if (sectionKey === "chart_highlights") {
                      // More robust check: ensure content exists and is a non-empty string
                      if (!section?.content || typeof section.content !== 'string' || section.content.trim() === '') {
                         console.log("Dashboard: Skipping Chart Highlights render (no content)."); // Added log
                         return null;
                       } 
                      
                      // Extract data if needed for more complex rendering
                      const combinedData = section?.data || { combinations: [], patterns: [] };
                      const combinationsData = combinedData.combinations;
                      const patternsData = combinedData.patterns;
                      
                      console.log("Dashboard: Rendering Chart Highlights."); // Added log
                      return (
                        <React.Fragment key={sectionKey}>
                          <Card>
                            <CardHeader>
                              <CardTitle>{section?.title || 'Chart Highlights'}</CardTitle>
                              <CardDescription>Key patterns and planetary connections shaping your chart's dynamics.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              {/* Render the combined markdown content from the backend */}
                              <div className="prose dark:prose-invert max-w-none">
                                {renderMarkdown(section.content)} 
                              </div>
                            </CardContent>
                          </Card>
                          <Separator className="my-6" />
                        </React.Fragment>
                      );
                    }

                    // Element & Modality Balance Chart Rendering
                    if (sectionKey === "element_balance") {
                      const elementData = section?.data as ElementBalanceData | undefined;
                      const modalityData = interpretation.structured_sections?.['modality_balance']?.data as ModalityBalanceData | undefined;
                      
                      return (
                        <React.Fragment key={sectionKey}>
                          <Card>
                            <CardHeader>
                              <CardTitle>{section?.title || 'Elemental & Modality Balance'}</CardTitle>
                               <CardDescription>The distribution of Fire, Earth, Air, Water (Elements) and Cardinal, Fixed, Mutable (Modalities) energies in your chart.</CardDescription>
                            </CardHeader>
                            <CardContent>
                              <div className="grid grid-cols-1 gap-4 mb-4 md:grid-cols-2">
                                  {elementData && Object.keys(elementData.percentages).length > 0 ? (
                                    // Log data being passed to ElementBalanceChart
                                    (() => {
                                      console.log("Dashboard: Passing data to ElementBalanceChart:", JSON.stringify(elementData));
                                      return <ElementBalanceChart elementBalance={elementData} />;
                                    })()
                                   ) : (
                                     <p className="py-10 text-sm text-center text-muted-foreground">Element data not available.</p>
                                   )}
                                   {modalityData && Object.keys(modalityData.percentages).length > 0 ? (
                                    // Log data being passed to ModalityBalanceChart
                                    (() => {
                                      console.log("Dashboard: Passing data to ModalityBalanceChart:", JSON.stringify(modalityData));
                                      return <ModalityBalanceChart modalityBalance={modalityData} />;
                                    })()
                                   ) : (
                                     <p className="py-10 text-sm text-center text-muted-foreground">Modality data not available.</p>
                                   )}
                              </div>
                              <div className="prose dark:prose-invert max-w-none">
                                {/* Render combined content if available */} 
                                {renderMarkdown(section?.content)}
                                {renderMarkdown(interpretation.structured_sections?.['modality_balance']?.content)}
                                {/* Optionally display dominant/lacking from data */} 
                                {(elementData?.dominant || modalityData?.dominant) && (
                                  <div className="mt-4 text-sm">
                                    {elementData?.dominant && <p><strong>Dominant Element:</strong> {elementData.dominant}</p>}
                                    {modalityData?.dominant && <p><strong>Dominant Modality:</strong> {modalityData.dominant}</p>}
                                  </div>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                          <Separator className="my-6" />
                        </React.Fragment>
                      );
                    }

                    // Modality Balance Chart Rendering
                    if (sectionKey === "modality_balance") {
                      // This data is rendered within the 'element_balance' section
                      return null;
                    }
                    
                    // Combined Understanding your Houses Section (replaces separate House Emphasis and Angles sections)
                    if (sectionKey === "house_emphasis" || sectionKey === "angles") {
                      // Only render once - when house_emphasis is encountered
                      if (sectionKey === "angles") return null;
                      
                      // Get the angles section data for combined rendering
                      const anglesSection = interpretation.structured_sections?.["angles"];
                      
                      return (
                        <React.Fragment key="understanding_houses">
                          <Card>
                            <CardHeader>
                              <CardTitle>Understanding your Houses</CardTitle>
                              <CardDescription>The 12 houses represent different areas of life experience and how planetary energies manifest in specific domains.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                              {/* Display Important Angles Section */}
                              <div className="mb-4">
                                <h4 className="font-semibold mb-3">Important Angles:</h4>
                                <div className="prose dark:prose-invert max-w-none text-sm">
                                  {renderMarkdown(anglesSection?.content)}
                                </div>
                                <div className="mt-2 px-3 py-2 rounded-md bg-muted/50">
                                  <p className="text-xs text-muted-foreground">The angles (Ascendant, Descendant, Midheaven, and IC) are the four most sensitive points in your chart, functioning as power channels through which planetary energy flows most directly into your life experience.</p>
                                </div>
                              </div>

                              {/* Display House Emphasis Data */} 
                              {section?.data && Array.isArray(section.data) && section.data.length > 0 && (
                                <div>
                                  <h4 className="font-semibold mb-3">Emphasized Houses:</h4>
                                  <ul className="pl-5 text-sm list-disc space-y-3">
                                    {section.data.map((emphasis: any, index: number) => (
                                      <li key={index} className="leading-relaxed">
                                        <strong>House {emphasis.house}:</strong> {emphasis.interpretation || 'No specific focus interpretation.'}
                                        {emphasis.planets && emphasis.planets.length > 0 && (
                                          <div className="mt-1 ml-2">
                                            <span className="font-medium">Planets:</span> {emphasis.planets.map((planet: string, i: number) => (
                                              <span key={i} className="ml-1">
                                                {planet}{i < emphasis.planets.length - 1 ? ', ' : ''}
                                              </span>
                                            ))}
                                            <div className="mt-1">
                                              {emphasis.planets.map((planet: string, i: number) => {
                                                const planetLower = planet.toLowerCase();
                                                let governs = "";
                                                
                                                // Map common planets to what they govern
                                                if (planetLower === "sun") governs = "identity, vitality, purpose";
                                                else if (planetLower === "moon") governs = "emotions, instincts, unconscious";
                                                else if (planetLower === "mercury") governs = "communication, thought, learning";
                                                else if (planetLower === "venus") governs = "love, beauty, values";
                                                else if (planetLower === "mars") governs = "action, desire, courage";
                                                else if (planetLower === "jupiter") governs = "expansion, abundance, wisdom";
                                                else if (planetLower === "saturn") governs = "structure, responsibility, mastery";
                                                else if (planetLower === "uranus") governs = "innovation, rebellion, freedom";
                                                else if (planetLower === "neptune") governs = "spirituality, dreams, dissolution";
                                                else if (planetLower === "pluto") governs = "transformation, power, rebirth";
                                                
                                                return governs ? (
                                                  <div key={i} className="text-xs text-muted-foreground">
                                                    <span className="font-medium">{planet}</span> governs {governs}
                          </div>
                                                ) : null;
                                              })}
                                            </div>
                                          </div>
                                        )}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              
                              {/* House Classification Analysis */}
                              <div className="mt-4">
                                <h4 className="font-semibold mb-3">House Classifications:</h4>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                  <div className="p-3 rounded-md border border-border">
                                    <h5 className="text-sm font-medium mb-1">Angular Houses (1, 4, 7, 10)</h5>
                                    <p className="text-xs text-muted-foreground">Action-oriented areas that initiate major life themes in identity, home, relationships, and career.</p>
                                  </div>
                                  <div className="p-3 rounded-md border border-border">
                                    <h5 className="text-sm font-medium mb-1">Succedent Houses (2, 5, 8, 11)</h5>
                                    <p className="text-xs text-muted-foreground">Resource-building areas that stabilize and develop values, creativity, transformation, and social connections.</p>
                                  </div>
                                  <div className="p-3 rounded-md border border-border">
                                    <h5 className="text-sm font-medium mb-1">Cadent Houses (3, 6, 9, 12)</h5>
                                    <p className="text-xs text-muted-foreground">Adaptable areas that process, refine, and prepare for transition through communication, service, philosophy, and spirituality.</p>
                                  </div>
                                </div>
                          </div>
                          
                              {/* Hemisphere Analysis */}
                              <div className="mt-4">
                                <h4 className="font-semibold mb-3">Hemisphere Distribution:</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div className="p-3 rounded-md border border-border">
                                    <h5 className="text-sm font-medium mb-1">Eastern (Houses 10-3) vs. Western (Houses 4-9)</h5>
                                    <p className="text-xs text-muted-foreground">Eastern emphasis suggests self-directed energy and personal initiative. Western emphasis indicates relationship-oriented and responsive approach.</p>
                                  </div>
                                  <div className="p-3 rounded-md border border-border">
                                    <h5 className="text-sm font-medium mb-1">Northern (Houses 1-6) vs. Southern (Houses 7-12)</h5>
                                    <p className="text-xs text-muted-foreground">Northern emphasis suggests subjective, personal, and private focus. Southern emphasis indicates objective, social, and public engagement.</p>
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                          <Separator className="my-6" />
                        </React.Fragment>
                      );
                    }

                    // Retrograde Planets Rendering
                    if (sectionKey === "retrograde_planets") {
                    return (
                        <React.Fragment key={sectionKey}>
                          <Card>
                            <CardHeader>
                              <CardTitle>{section?.title || 'Planetary Movement'}</CardTitle>
                              <CardDescription>Retrograde planets suggest energies that are turned inward, internalized, or operate unconventionally. They often indicate areas needing review, reflection, or a unique approach.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <div className="prose dark:prose-invert max-w-none">
                                {/* Filter out the "You have 3 retrograde planets:" text */}
                                {section?.content && 
                                  renderMarkdown(section.content.replace(/You have \d+ retrograde planets?:/g, ''))}
                              </div>
                               {/* Display Retrograde Data */} 
                              {section?.data && Array.isArray(section.data) && section.data.length > 0 && (
                                <div className="mt-4">
                                  <h4 className="font-semibold">Retrograde Planets:</h4>
                                  <p className="text-sm">{section.data.join(', ')}</p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        <Separator className="my-6" />
                        </React.Fragment>
                      );
                    }

                    // --- Default Section Rendering --- //

                    // Generic rendering for any other sections
                    // Should only be reached if a section key is in display_order but not handled above
                    if (!section?.content && !section?.data) {
                        console.warn(`Rendering default for ${sectionKey}, but it has no content or data.`);
                        return null; // Skip truly empty sections
                    }
                    return (
                        <React.Fragment key={sectionKey}>
                            <Card>
                                <CardHeader>
                                    <CardTitle>{section?.title || sectionKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</CardTitle>
                                </CardHeader>
                                <CardContent className="prose dark:prose-invert max-w-none">
                                    {renderMarkdown(section?.content)}
                                    {/* Add generic data display if needed */} 
                                    {section?.data && (
                                        <pre className="p-2 mt-4 overflow-auto text-xs rounded bg-muted">{JSON.stringify(section.data, null, 2)}</pre>
                                    )}
                                </CardContent>
                            </Card>
                            <Separator className="my-6" />
                        </React.Fragment>
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