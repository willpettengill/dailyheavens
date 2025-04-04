"use client"

import { Cell, LabelList, Pie, PieChart, Bar, BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Rectangle } from "recharts"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

// Element Balance Chart
export interface ElementBalanceData {
  percentages: Record<string, number>;
  dominant?: string;
  lacking?: string[] | number;
}

export function ElementBalanceChart({ elementBalance }: { elementBalance: ElementBalanceData }) {
  // Filter out elements with 0 percentage
  const chartData = Object.entries(elementBalance.percentages)
    .filter(([, percentage]) => percentage > 0) // Only include elements with value > 0
    .map(([element, percentage]) => ({
      name: element,
      value: percentage // Use actual percentage value for pie chart segments
    }));

  const chartConfig = {
    value: {
      label: "Percentage",
    },
    fire: {
      label: "Fire",
      color: "var(--color-chart-1)"
    },
    earth: {
      label: "Earth",
      color: "var(--color-chart-2)"
    },
    air: {
      label: "Air",
      color: "var(--color-chart-3)"
    },
    water: {
      label: "Water",
      color: "var(--color-chart-4)"
    }
  } satisfies ChartConfig;

  // Create an array of colors based on the order of data items
  const COLORS = [
    chartConfig.fire.color,
    chartConfig.earth.color, 
    chartConfig.air.color, 
    chartConfig.water.color
  ];

  // Function to get element color with type safety
  const getElementColor = (elementName: string): string => {
    if (elementName === 'fire') return chartConfig.fire.color;
    if (elementName === 'earth') return chartConfig.earth.color;
    if (elementName === 'air') return chartConfig.air.color;
    if (elementName === 'water') return chartConfig.water.color;
    return COLORS[0]; // Default color
  };

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-0">
        <CardTitle className="text-base">Element Balance</CardTitle>
        <div className="mt-2 space-y-1 text-sm">
          {elementBalance.dominant && (
            <div>
              <span className="font-medium">Dominant: </span>
              <span className="capitalize text-muted-foreground">
                {elementBalance.dominant}
              </span>
            </div>
          )}
          {elementBalance.lacking && Array.isArray(elementBalance.lacking) && elementBalance.lacking.length > 0 && (
            <div>
              <span className="font-medium">Lacking: </span>
              <span className="text-muted-foreground">
                {elementBalance.lacking.map(e => 
                  typeof e === 'string' ? e.charAt(0).toUpperCase() + e.slice(1) : '').join(', ')}
              </span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 pt-4 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[200px] [&_.recharts-text]:fill-background"
        >
          <PieChart>
            <ChartTooltip
              content={<ChartTooltipContent nameKey="name" hideLabel />}
            />
            <Pie 
              data={chartData} 
              dataKey="value" 
              nameKey="name"
              cx="50%" 
              cy="50%" 
              outerRadius={70}
              fill="#8884d8" // This is overridden by the Cell components
            >
              {
                chartData.map((entry, index) => {
                  // Get the correct color based on the element name
                  const elementName = entry.name.toLowerCase();
                  const color = getElementColor(elementName);
                  
                  return <Cell key={`cell-${index}`} fill={color} />;
                })
              }
              <LabelList
                dataKey="name"
                className="fill-background"
                stroke="none"
                fontSize={12}
                formatter={(value: string) => value.charAt(0).toUpperCase() + value.slice(1)}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardContent className="pt-3 pb-3 text-xs text-muted-foreground">
        <div className="space-y-1">
          <div><span className="font-medium">Fire:</span> Energy, passion, impulsivity, creativity</div>
          <div><span className="font-medium">Earth:</span> Stability, practicality, reliability, groundedness</div>
          <div><span className="font-medium">Air:</span> Intellect, communication, social connection, ideas</div>
          <div><span className="font-medium">Water:</span> Emotion, intuition, sensitivity, empathy</div>
        </div>
      </CardContent>
    </Card>
  );
}

// Modality Balance Chart
export interface ModalityBalanceData {
  percentages: Record<string, number>;
  dominant?: string;
  lacking?: string[] | number;
}

export function ModalityBalanceChart({ modalityBalance }: { modalityBalance: ModalityBalanceData }) {
  // Filter out modalities with 0 percentage
  const chartData = Object.entries(modalityBalance.percentages)
    .filter(([, percentage]) => percentage > 0) // Only include modalities with value > 0
    .map(([modality, percentage]) => ({
      name: modality,
      value: percentage // Use actual percentage value for pie chart segments
    }));

  const chartConfig = {
    value: {
      label: "Percentage",
    },
    cardinal: {
      label: "Cardinal",
      color: "var(--color-chart-1)"
    },
    fixed: {
      label: "Fixed",
      color: "var(--color-chart-3)"
    },
    mutable: {
      label: "Mutable",
      color: "var(--color-chart-5)"
    }
  } satisfies ChartConfig;

  // Create an array of colors based on the order of data items
  const COLORS = [
    chartConfig.cardinal.color, 
    chartConfig.fixed.color,
    chartConfig.mutable.color
  ];

  // Function to get modality color with type safety
  const getModalityColor = (modalityName: string): string => {
    if (modalityName === 'cardinal') return chartConfig.cardinal.color;
    if (modalityName === 'fixed') return chartConfig.fixed.color;
    if (modalityName === 'mutable') return chartConfig.mutable.color;
    return COLORS[0]; // Default color
  };

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-0">
        <CardTitle className="text-base">Modality Balance</CardTitle>
        <div className="mt-2 space-y-1 text-sm">
          {modalityBalance.dominant && (
            <div>
              <span className="font-medium">Dominant: </span>
              <span className="capitalize text-muted-foreground">
                {modalityBalance.dominant}
              </span>
            </div>
          )}
          {modalityBalance.lacking && Array.isArray(modalityBalance.lacking) && modalityBalance.lacking.length > 0 && (
            <div>
              <span className="font-medium">Lacking: </span>
              <span className="text-muted-foreground">
                {modalityBalance.lacking.map(m => 
                  typeof m === 'string' ? m.charAt(0).toUpperCase() + m.slice(1) : '').join(', ')}
              </span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 pt-4 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[200px] [&_.recharts-text]:fill-background"
        >
          <PieChart>
            <ChartTooltip
              content={<ChartTooltipContent nameKey="name" hideLabel />}
            />
            <Pie 
              data={chartData} 
              dataKey="value" 
              nameKey="name"
              cx="50%" 
              cy="50%" 
              outerRadius={70}
              fill="#8884d8" // This is overridden by the Cell components
            >
              {
                chartData.map((entry, index) => {
                  // Get the correct color based on the modality name
                  const modalityName = entry.name.toLowerCase();
                  const color = getModalityColor(modalityName);
                  
                  return <Cell key={`cell-${index}`} fill={color} />;
                })
              }
              <LabelList
                dataKey="name"
                className="fill-background"
                stroke="none"
                fontSize={12}
                formatter={(value: string) => value.charAt(0).toUpperCase() + value.slice(1)}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardContent className="pt-3 pb-3 text-xs text-muted-foreground">
        <div className="space-y-1">
          <div><span className="font-medium">Cardinal:</span> Initiating, leadership, active, ambitious</div>
          <div><span className="font-medium">Fixed:</span> Stable, persistent, determined, reliable</div>
          <div><span className="font-medium">Mutable:</span> Adaptable, flexible, versatile, changeable</div>
        </div>
      </CardContent>
    </Card>
  );
}

// Sign Distribution Chart
export interface SignDistributionData {
  planets: Record<string, string[]>;
  houses: Record<string, string[]>;
}

export function SignDistributionChart({ signDistribution }: { signDistribution: SignDistributionData }) {
  // Zodiac signs in traditional order
  const zodiacSigns = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 
    'Leo', 'Virgo', 'Libra', 'Scorpio', 
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
  ];

  // Transform data for the stacked bar chart
  const chartData = zodiacSigns.map((sign) => {
    const planetCount = signDistribution.planets[sign]?.length || 0;
    const houseCount = signDistribution.houses[sign]?.length || 0;
    
    return {
      name: sign,
      planets: planetCount,
      houses: houseCount
    };
  });

  const chartConfig = {
    planets: {
      label: "Planets",
      color: "var(--color-chart-1)"
    },
    houses: {
      label: "Houses",
      color: "var(--color-chart-3)"
    }
  } satisfies ChartConfig;

  // Get dominant sign (most planets and houses combined)
  const dominantSign = [...chartData]
    .sort((a, b) => (b.planets + b.houses) - (a.planets + a.houses))[0]?.name;

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-0">
        <CardTitle className="text-base">Sign Distribution</CardTitle>
        {dominantSign && (
          <div className="mt-2 space-y-1 text-sm">
            <div>
              <span className="font-medium">Dominant Sign: </span>
              <span className="capitalize text-muted-foreground">{dominantSign}</span>
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent className="flex-1 pt-4 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto min-h-[300px] w-full"
        >
          <BarChart 
            data={chartData}
            margin={{ top: 10, right: 10, left: 0, bottom: 55 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis 
              dataKey="name" 
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 10 }}
              angle={-45}
              textAnchor="end"
              interval={0}
            />
            <YAxis 
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 10 }}
              domain={[0, 'dataMax + 1']}
            />
            <Tooltip content={<ChartTooltipContent />} />
            <Legend />
            <Bar 
              dataKey="planets" 
              name="Planets" 
              stackId="a" 
              fill={chartConfig.planets.color} 
              radius={[4, 4, 0, 0]}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              shape={(props: any) => <Rectangle {...props} fill={chartConfig.planets.color} />}
            />
            <Bar 
              dataKey="houses" 
              name="Houses" 
              stackId="a" 
              fill={chartConfig.houses.color}
              radius={[4, 4, 0, 0]}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              shape={(props: any) => <Rectangle {...props} fill={chartConfig.houses.color} />}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardContent className="pt-3 pb-3 text-xs text-muted-foreground">
        <div className="space-y-1">
          <div>
            <span className="font-medium">What This Shows:</span> Distribution of planets and houses across zodiac signs, revealing where your chart&apos;s energy is concentrated.
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 