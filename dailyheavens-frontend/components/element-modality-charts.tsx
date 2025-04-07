"use client"

import { Cell, LabelList, Pie, PieChart, Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { TrendingUp } from "lucide-react"

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
          <div><span className="font-medium">Earth:</span> Stability, practicality, groundedness</div>
          <div><span className="font-medium">Air:</span> Intellect, communication, social connection</div>
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
          <div><span className="font-medium">Cardinal:</span> Initiative, leadership, ambition</div>
          <div><span className="font-medium">Fixed:</span> Stability, persistence, determination</div>
          <div><span className="font-medium">Mutable:</span> Adaptability, flexibility, versatility</div>
        </div>
      </CardContent>
    </Card>
  );
}

// Sign Distribution Chart 
export interface SignDistributionData {
  planets: Record<string, number>;
  houses: Record<string, number>;
}

export function SignDistributionChart({ signDistribution }: { signDistribution: SignDistributionData }) {
  const planets = signDistribution.planets || {};
  const houses = signDistribution.houses || {};

  // Get all unique signs from both planets and houses
  const allSigns = [...new Set([...Object.keys(planets), ...Object.keys(houses)])];

  // Transform data for stacked bar chart, iterating through all unique signs
  const chartData = allSigns
    .map(sign => ({
      sign: sign,
      planets: planets[sign] || 0, // Default to 0 if sign not in planets
      houses: houses[sign] || 0,  // Default to 0 if sign not in houses
      // Calculate total for sorting
      total: (planets[sign] || 0) + (houses[sign] || 0)
    }))
    // Filter out signs with zero total count (optional, but keeps chart clean)
    .filter(data => data.total > 0)
    // Sort by total count descending
    .sort((a, b) => b.total - a.total);
    
  // Updated chartConfig to remove hsl() wrapper as per ShadCN v4 docs with @theme inline
  const chartConfig = {
    planets: {
      label: "Planets",
      color: "var(--chart-1)"
    },
    houses: {
      label: "Houses",
      color: "var(--chart-2)"
    }
  } satisfies ChartConfig;

  // Format sign name to title case with full names
  const formatSignName = (sign: string): string => {
    const zodiacSigns: Record<string, string> = {
      'aries': 'Aries',
      'taurus': 'Taurus',
      'gemini': 'Gemini',
      'cancer': 'Cancer',
      'leo': 'Leo',
      'virgo': 'Virgo',
      'libra': 'Libra',
      'scorpio': 'Scorpio',
      'sagittarius': 'Sagittarius',
      'capricorn': 'Capricorn',
      'aquarius': 'Aquarius',
      'pisces': 'Pisces'
    };
    return zodiacSigns[sign.toLowerCase()] || sign;
  };

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Sign Distribution</CardTitle>
      </CardHeader>
      <CardContent className="pt-2">
        <ChartContainer
          config={chartConfig}
          className="min-h-[300px] w-full [&_.recharts-text]:fill-card-foreground"
        >
          <BarChart 
            accessibilityLayer 
            data={chartData}
            margin={{ top: 10, right: 30, left: 15, bottom: 80 }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="sign"
              tickLine={false}
              tickMargin={20}
              axisLine={false}
              angle={-45}
              textAnchor="end"
              tick={{ fontSize: 12 }}
              tickFormatter={formatSignName}
            />
            <YAxis 
              tickLine={false}
              axisLine={false}
              tickMargin={10}
              label={{ 
                value: 'Count', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle' },
                className: "fill-card-foreground text-xs"
              }}
            />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <ChartLegend content={<ChartLegendContent />} />
            {/* Updated fill properties to use --color-KEY pattern */}
            <Bar
              dataKey="planets"
              stackId="a"
              name="Planets"
              fill="var(--color-planets)" // Corrected fill
              radius={[0, 0, 4, 4]}
            />
            <Bar
              dataKey="houses"
              stackId="a"
              name="Houses"
              fill="var(--color-houses)" // Corrected fill
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardContent className="pt-1 pb-3 text-xs text-muted-foreground">
        <div className="text-center">
          Distribution of planets and houses across zodiac signs
        </div>
      </CardContent>
    </Card>
  );
}

// Boilerplate Stacked Bar Chart for Comparison
const boilerplateChartData = [
  { month: "January", desktop: 186, mobile: 80 },
  { month: "February", desktop: 305, mobile: 200 },
  { month: "March", desktop: 237, mobile: 120 },
  { month: "April", desktop: 73, mobile: 190 },
  { month: "May", desktop: 209, mobile: 130 },
  { month: "June", desktop: 214, mobile: 140 },
];

const boilerplateChartConfig = {
  desktop: {
    label: "Desktop",
    // Use var() directly because of @theme inline
    color: "var(--chart-1)",
  },
  mobile: {
    label: "Mobile",
    // Use var() directly because of @theme inline
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export function BoilerplateStackedBarChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Boilerplate - Stacked + Legend</CardTitle>
        <CardDescription>January - June 2024 (Test)</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={boilerplateChartConfig}>
          <BarChart accessibilityLayer data={boilerplateChartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <YAxis />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="desktop"
              stackId="a"
              fill="var(--color-desktop)"
              radius={[0, 0, 4, 4]}
            />
            <Bar
              dataKey="mobile"
              stackId="a"
              fill="var(--color-mobile)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 font-medium leading-none">
          Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
        </div>
        <div className="leading-none text-muted-foreground">
          Showing total visitors for the last 6 months
        </div>
      </CardFooter>
    </Card>
  );
} 