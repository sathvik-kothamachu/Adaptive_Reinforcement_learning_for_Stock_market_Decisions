import { AnalysisSchema, type Analysis } from "./schema";
import { buildMockAnalysis } from "./mock";

const API_BASE = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Fetches analysis for a given ticker from the Python backend API.
 * Falls back to mock data when VITE_API_BASE_URL is not set.
 */
export async function fetchAnalysis(ticker: string): Promise<Analysis> {
  if (!API_BASE) {
    // Simulate a small network delay for realism
    await new Promise((r) => setTimeout(r, 350));
    return AnalysisSchema.parse(buildMockAnalysis(ticker));
  }

  const url = `${API_BASE}/api/analyze?ticker=${encodeURIComponent(ticker)}`;
  let res: Response;
  try {
    res = await fetch(url, { 
      headers: { Accept: "application/json" },
      method: "GET",
    });
  } catch (e) {
    throw new ApiError(`Network error contacting analysis API: ${(e as Error).message}`);
  }
  if (!res.ok) {
    const errorData = await res.text();
    throw new ApiError(
      `Analysis API returned ${res.status}: ${errorData || res.statusText}`,
      res.status
    );
  }
  const json = await res.json();
  const parsed = AnalysisSchema.safeParse(json);
  if (!parsed.success) {
    console.error("Validation error:", parsed.error);
    throw new ApiError(`Invalid response shape: ${parsed.error.message}`);
  }
  return parsed.data;
}

/**
 * Fetches market regime data
 */
export async function fetchMarketRegime() {
  if (!API_BASE) {
    return { bull_pct: 45, sideways_pct: 30, bear_pct: 25, nifty_data: [] };
  }

  const url = `${API_BASE}/api/market-regime`;
  try {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new ApiError(`Market regime API returned ${res.status}`, res.status);
    return await res.json();
  } catch (e) {
    throw new ApiError(`Error fetching market regime: ${(e as Error).message}`);
  }
}

/**
 * Fetches all stocks analysis in parallel
 */
export async function fetchAllStocksAnalysis(): Promise<Record<string, Analysis>> {
  if (!API_BASE) {
    return {};
  }

  const url = `${API_BASE}/api/all-stocks`;
  try {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new ApiError(`All stocks API returned ${res.status}`, res.status);
    return await res.json();
  } catch (e) {
    throw new ApiError(`Error fetching all stocks: ${(e as Error).message}`);
  }
}

/**
 * Get list of available stocks
 */
export async function fetchAvailableStocks() {
  if (!API_BASE) {
    return [];
  }

  const url = `${API_BASE}/api/stocks`;
  try {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new ApiError(`Stocks list API returned ${res.status}`, res.status);
    return await res.json();
  } catch (e) {
    throw new ApiError(`Error fetching available stocks: ${(e as Error).message}`);
  }
}

/**
 * Sends a message to the Support & XAI Bot
 */
export async function sendChatMessage(
  message: string,
  ticker?: string,
  analysisContext?: any
): Promise<string> {
  if (!API_BASE) {
    await new Promise((r) => setTimeout(r, 800));
    return "The bot is currently in offline/mock mode. Please connect the backend to chat with Gemini.";
  }

  const url = `${API_BASE}/api/chat`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "application/json" 
      },
      body: JSON.stringify({ message, ticker, analysis_context: analysisContext }),
    });
    
    if (!res.ok) {
      const errorData = await res.text();
      throw new ApiError(`Chat API returned ${res.status}: ${errorData}`, res.status);
    }
    
    const data = await res.json();
    return data.response;
  } catch (e) {
    throw new ApiError(`Error communicating with Gemini: ${(e as Error).message}`);
  }
}

export const isUsingMock = !API_BASE;

