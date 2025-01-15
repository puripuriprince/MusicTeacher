import React from "react";

import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
} from "chart.js";
import { Radar } from "react-chartjs-2";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler);

interface SpiderChartProps {
  data: { labels: string[]; datasets: { data: number[]; label: string }[] };
  options?: any;
}

export const SpiderChart: React.FC<SpiderChartProps> = ({ data, options }) => {
  return <Radar data={data} options={options} />;
};
