import { useMemo } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import type { NiftyPoint } from "@/lib/schema";
import { useChartTheme } from "./useChartTheme";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export function NiftyLineChart({ data }: { data: NiftyPoint[] }) {
  const t = useChartTheme();

  const chartData = useMemo(() => {
    const colorFor = (r: NiftyPoint["regime"]) =>
      r === "Bullish" ? t.bull : r === "Bearish" ? t.bear : t.sideways;
    return {
      labels: data.map((p) => p.date),
      datasets: [
        {
          label: "Nifty 50",
          data: data.map((p) => p.value),
          borderColor: t.primary,
          backgroundColor: t.primaryFill,
          fill: true,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: data.map((p) => colorFor(p.regime)),
          pointBorderColor: data.map((p) => colorFor(p.regime)),
          borderWidth: 2,
        },
      ],
    };
  }, [data, t]);

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
          callbacks: {
            label: (ctx: { dataIndex: number; parsed: { y: number } }) => {
              const p = data[ctx.dataIndex];
              return `${p.value.toFixed(0)} · ${p.regime}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: t.muted, maxTicksLimit: 8, font: { size: 10 } },
        },
        y: {
          grid: { color: t.grid },
          ticks: { color: t.muted, font: { size: 10 } },
        },
      },
      interaction: { mode: "index" as const, intersect: false },
    }),
    [t, data]
  );

  return (
    <div role="img" aria-label="Nifty 50 index value over time, points coloured by market regime" className="h-56 w-full">
      <Line data={chartData} options={options as never} />
    </div>
  );
}
