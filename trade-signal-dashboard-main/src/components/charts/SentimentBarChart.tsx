import { useMemo } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { useChartTheme } from "./useChartTheme";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface Props {
  dates: string[];
  scores: number[];
}

export function SentimentBarChart({ dates, scores }: Props) {
  const t = useChartTheme();

  const data = useMemo(
    () => ({
      labels: dates,
      datasets: [
        {
          label: "Sentiment",
          data: scores,
          backgroundColor: scores.map((s) =>
            s > 0.05 ? t.bull : s < -0.05 ? t.bear : t.sideways
          ),
          borderRadius: 4,
          borderSkipped: false,
        },
      ],
    }),
    [dates, scores, t]
  );

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: t.surface,
          titleColor: t.foreground,
          bodyColor: t.foreground,
          borderColor: t.border,
          borderWidth: 1,
          padding: 10,
          displayColors: false,
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: t.muted, font: { size: 10 } },
        },
        y: {
          grid: { color: t.grid },
          ticks: { color: t.muted, font: { size: 10 } },
        },
      },
    }),
    [t]
  );

  return (
    <div
      role="img"
      aria-label="Daily news sentiment scores for the last 14 days"
      className="h-48 w-full"
    >
      <Bar data={data} options={options as never} />
    </div>
  );
}
