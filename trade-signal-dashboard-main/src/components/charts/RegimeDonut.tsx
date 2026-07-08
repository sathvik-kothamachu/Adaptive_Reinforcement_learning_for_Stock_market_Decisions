import { useMemo } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { useChartTheme } from "./useChartTheme";

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  bull: number;
  sideways: number;
  bear: number;
}

export function RegimeDonut({ bull, sideways, bear }: Props) {
  const t = useChartTheme();

  const data = useMemo(
    () => ({
      labels: ["Bullish", "Sideways", "Bearish"],
      datasets: [
        {
          data: [bull, sideways, bear],
          backgroundColor: [t.bull, t.sideways, t.bear],
          borderColor: t.surface,
          borderWidth: 3,
          hoverOffset: 6,
        },
      ],
    }),
    [bull, sideways, bear, t]
  );

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
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
            label: (ctx: { label: string; parsed: number }) =>
              `${ctx.label}: ${ctx.parsed.toFixed(1)}%`,
          },
        },
      },
    }),
    [t]
  );

  return (
    <div
      role="img"
      aria-label={`Market regime distribution: ${bull.toFixed(1)}% bullish, ${sideways.toFixed(1)}% sideways, ${bear.toFixed(1)}% bearish`}
      className="relative h-40 w-40"
    >
      <Doughnut data={data} options={options as never} />
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <div className="font-mono text-2xl font-bold text-foreground">{bull.toFixed(0)}%</div>
        <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Bullish</div>
      </div>
    </div>
  );
}
