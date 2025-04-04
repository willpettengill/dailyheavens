"use client"

import { Cell, LabelList, Pie, PieChart } from "recharts"

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