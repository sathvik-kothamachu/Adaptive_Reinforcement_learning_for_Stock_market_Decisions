import { useEffect, useState } from "react";

/**
 * Reads CSS variable values (HSL triples like "190 95% 55%") so Chart.js
 * can be styled from the same design tokens as the rest of the app.
 * Re-reads on theme change.
 */
export function useChartTheme() {
  const [tokens, setTokens] = useState(() => readTokens());

  useEffect(() => {
    const obs = new MutationObserver(() => setTokens(readTokens()));
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => obs.disconnect();
  }, []);

  return tokens;
}

function hsl(varName: string, alpha = 1) {
  if (typeof window === "undefined") return "";
  const v = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
  return alpha === 1 ? `hsl(${v})` : `hsl(${v} / ${alpha})`;
}

function readTokens() {
  return {
    grid: hsl("--border", 0.3),
    axis: hsl("--muted-foreground", 0.5),
    bull: hsl("--signal-buy"),
    bear: hsl("--signal-sell"),
    sideways: hsl("--signal-hold"),
    primary: hsl("--primary"),
    primaryGlow: hsl("--primary"),
    primaryFill: hsl("--primary", 0.18),
    surface: hsl("--card", 0.8),
    foreground: hsl("--foreground"),
    muted: hsl("--muted-foreground"),
    border: hsl("--border"),
  };
}
