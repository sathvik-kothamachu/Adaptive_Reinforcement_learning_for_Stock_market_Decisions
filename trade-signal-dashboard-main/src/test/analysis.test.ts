import { describe, it, expect } from "vitest";
import { AnalysisSchema } from "@/lib/schema";
import { buildMockAnalysis } from "@/lib/mock";
import { scoreStatus, signalTokens, formatSigned } from "@/lib/format";

describe("schema + mock", () => {
  it("mock payloads validate against the schema for every ticker", () => {
    const tickers = ["RELIANCE.NS", "TCS.NS", "KOTAKBANK.NS", "HDFCBANK.NS"];
    for (const t of tickers) {
      const parsed = AnalysisSchema.safeParse(buildMockAnalysis(t));
      expect(parsed.success).toBe(true);
    }
  });

  it("mock action_value is between -1 and 1", () => {
    const m = buildMockAnalysis("INFY.NS");
    expect(m.action_value).toBeGreaterThanOrEqual(-1);
    expect(m.action_value).toBeLessThanOrEqual(1);
  });

  it("regime percentages sum to ~100", () => {
    const m = buildMockAnalysis("ITC.NS");
    const sum = m.market_regime.bull_pct + m.market_regime.sideways_pct + m.market_regime.bear_pct;
    expect(Math.abs(sum - 100)).toBeLessThan(0.5);
  });
});

describe("format helpers", () => {
  it("scoreStatus maps thresholds correctly", () => {
    expect(scoreStatus(80)).toBe("Strong");
    expect(scoreStatus(60)).toBe("Good");
    expect(scoreStatus(40)).toBe("OK");
    expect(scoreStatus(20)).toBe("Weak");
  });

  it("formatSigned prefixes positive values with +", () => {
    expect(formatSigned(0.73)).toBe("+0.73");
    expect(formatSigned(-0.42)).toBe("-0.42");
  });

  it("signalTokens returns distinct gradients per signal", () => {
    expect(signalTokens("BUY").gradient).toContain("buy");
    expect(signalTokens("SELL").gradient).toContain("sell");
    expect(signalTokens("HOLD").gradient).toContain("hold");
  });
});
