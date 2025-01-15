import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface LineChartProps {
  data: { x: Date; y: number }[];
}

export default function LineChart({ data }: LineChartProps) {
  const chartData = {
    labels: data.map((item) => item.x.toLocaleDateString()), // Format date as string
    datasets: [
      {
        label: "Score",
        data: data.map((item) => item.y),
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.5)",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
    scales: {
      x: {
        ticks: {
          color: "white", // Set x-axis tick color to white
        },
        grid: {
          color: "rgba(255, 255, 255, 0.2)", // Set x-axis grid color to semi-transparent white
        },
      },
      y: {
        ticks: {
          color: "white", // Set y-axis tick color to white
        },
        grid: {
          color: "rgba(255, 255, 255, 0.2)", // Set y-axis grid color to semi-transparent white
        },
      },
    },
  };

  return (
    <div className="h-96">
      <Line data={chartData} options={options} />
    </div>
  );
}
