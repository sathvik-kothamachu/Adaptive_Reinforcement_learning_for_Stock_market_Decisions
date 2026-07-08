import type { IndicatorStatus, Signal } from "./schema";

export const formatNumber = (n: number, digits = 2) =>
  n.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits });

export const formatPercent = (n: number, digits = 1) => `${n.toFixed(digits)}%`;

export const formatSigned = (n: number, digits = 2) => `${n >= 0 ? "+" : ""}${n.toFixed(digits)}`;

export const statusColorClass = (s: IndicatorStatus) => {
  switch (s) {
    case "Strong":
      return "text-status-strong";
    case "Good":
      return "text-status-good";
    case "OK":
      return "text-status-ok";
    case "Weak":
      return "text-status-weak";
  }
};

export const statusBgClass = (s: IndicatorStatus) => {
  switch (s) {
    case "Strong":
      return "bg-status-strong";
    case "Good":
      return "bg-status-good";
    case "OK":
      return "bg-status-ok";
    case "Weak":
      return "bg-status-weak";
  }
};

export const signalTokens = (s: Signal) => {
  switch (s) {
    case "BUY":
      return {
        gradient: "bg-gradient-buy",
        text: "text-signal-buy",
        glow: "animate-pulse-buy",
        ring: "ring-signal-buy/40",
      };
    case "SELL":
      return {
        gradient: "bg-gradient-sell",
        text: "text-signal-sell",
        glow: "animate-pulse-sell",
        ring: "ring-signal-sell/40",
      };
    case "HOLD":
      return {
        gradient: "bg-gradient-hold",
        text: "text-signal-hold",
        glow: "animate-pulse-hold",
        ring: "ring-signal-hold/40",
      };
  }
};

export const scoreStatus = (score: number): IndicatorStatus => {
  if (score >= 75) return "Strong";
  if (score >= 55) return "Good";
  if (score >= 35) return "OK";
  return "Weak";
};

export const timeAgo = (date: Date) => {
  const s = Math.floor((Date.now() - date.getTime()) / 1000);
  if (s < 5) return "just now";
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
};
