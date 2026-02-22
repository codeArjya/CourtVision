"use client";

import { LineChart, Line } from "recharts";

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
}

export default function Sparkline({
  data,
  width = 64,
  height = 28,
}: SparklineProps) {
  if (!data || data.length === 0) return null;
  const chartData = data.map((v, i) => ({ v, i }));
  const isUp = data[data.length - 1] > data[0];
  const color = isUp ? "#27AE60" : "#E74C3C";

  return (
    <LineChart width={width} height={height} data={chartData}>
      <Line
        dataKey="v"
        dot={(props: any) => {
          // Only show dot on last point
          if (props.index === data.length - 1) {
            return (
              <circle
                key="last"
                cx={props.cx}
                cy={props.cy}
                r={3}
                fill={color}
              />
            );
          }
          return <g key={props.index} />;
        }}
        strokeWidth={2}
        stroke={color}
        isAnimationActive={false}
      />
    </LineChart>
  );
}
