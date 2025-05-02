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
        {/* Comment out the element details to simplify chart display
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
        */}
      </CardHeader>
      <CardContent className="flex-1 pt-4 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[200px]"
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
              labelLine={false}
              label={({ cx, cy, midAngle, innerRadius, outerRadius, name }) => {
                const RADIAN = Math.PI / 180;
                const radius = innerRadius + (outerRadius - innerRadius) * 1.15; 
                const x = cx + radius * Math.cos(-midAngle * RADIAN);
                const y = cy + radius * Math.sin(-midAngle * RADIAN);

                return (
                  <text 
                    x={x}
                    y={y}
                    fill="currentColor"
                    textAnchor={x > cx ? 'start' : 'end'} 
                    dominantBaseline="central"
                    className="text-xs fill-foreground"
                  >
                    {name.charAt(0).toUpperCase() + name.slice(1)}
                  </text>
                );
              }}
              outerRadius={70}
              fill="#8884d8"
            >
              {
                chartData.map((entry, index) => {
                  const elementName = entry.name.toLowerCase();
                  const color = getElementColor(elementName);
                  
                  return <Cell key={`cell-${index}`} fill={color} />;
                })
              }
            </Pie>
          </PieChart>
        </ChartContainer>
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
        {/* Comment out the modality details to simplify chart display
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
        */}
      </CardHeader>
      <CardContent className="flex-1 pt-4 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[200px]"
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
              labelLine={false}
              label={({ cx, cy, midAngle, innerRadius, outerRadius, name }) => {
                const RADIAN = Math.PI / 180;
                const radius = innerRadius + (outerRadius - innerRadius) * 1.15;
                const x = cx + radius * Math.cos(-midAngle * RADIAN);
                const y = cy + radius * Math.sin(-midAngle * RADIAN);

                return (
                  <text 
                    x={x}
                    y={y}
                    fill="currentColor"
                    textAnchor={x > cx ? 'start' : 'end'} 
                    dominantBaseline="central"
                    className="text-xs fill-foreground"
                  >
                    {name.charAt(0).toUpperCase() + name.slice(1)}
                  </text>
                );
              }}
              outerRadius={70}
              fill="#8884d8"
            >
              {
                chartData.map((entry, index) => {
                  const modalityName = entry.name.toLowerCase();
                  const color = getModalityColor(modalityName);
                  
                  return <Cell key={`cell-${index}`} fill={color} />;
                })
              }
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

// Sign Distribution Chart
export interface SignDistributionBackendData {
  // Structure matches what the backend generates
  [sign: string]: { planets: number; houses: number };
}

export function SignDistributionChart({ signDistribution }: { signDistribution: SignDistributionBackendData }) {
  const zodiacSigns = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
  ];

  // Transform the backend data into the format Recharts expects
  const processedChartData = zodiacSigns.map(sign => {
    const signData = signDistribution[sign] || { planets: 0, houses: 0 };
    return {
      sign: sign, // Keep full name for potential sorting/filtering
      signAbbr: sign.substring(0, 3), // Keep abbreviation for axis
      planets: signData.planets,
      houses: signData.houses,
      total: signData.planets + signData.houses // Add total for sorting
    };
  });

  // Sort the data by total count descending
  const chartData = processedChartData.sort((a, b) => b.total - a.total);

  const chartConfig = {
    planets: {
      label: "Planets",
      color: "var(--color-chart-1)",
    },
    houses: {
      label: "Houses",
      color: "var(--color-chart-3)",
    },
  } satisfies ChartConfig;

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
          className="h-[250px] w-full"
        >
          <BarChart data={chartData} margin={{ top: 20, right: 20, left: -10, bottom: 5 }}>
            <CartesianGrid vertical={false} />
            <XAxis 
              dataKey="sign" 
              tickLine={false} 
              tickMargin={10} 
              axisLine={false}
              tickFormatter={(value) => chartConfig[value as keyof typeof chartConfig]?.label || value}
            />
            <YAxis />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="planets"
              stackId="a"
              name="Planets"
              fill="var(--color-planets)"
              radius={[0, 0, 4, 4]}
            />
            <Bar
              dataKey="houses"
              stackId="a"
              name="Houses"
              fill="var(--color-houses)"
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
          Trending up by 5.2% this month <TrendingUp className="w-4 h-4" />
        </div>
        <div className="leading-none text-muted-foreground">
          Showing total visitors for the last 6 months
        </div>
      </CardFooter>
    </Card>
  );
} 