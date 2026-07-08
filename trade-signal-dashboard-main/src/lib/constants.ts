export const NIFTY_TICKERS = [
  { ticker: "RELIANCE.NS", name: "Reliance Industries" },
  { ticker: "TCS.NS", name: "Tata Consultancy Services" },
  { ticker: "HDFCBANK.NS", name: "HDFC Bank" },
  { ticker: "ICICIBANK.NS", name: "ICICI Bank" },
  { ticker: "INFY.NS", name: "Infosys" },
  { ticker: "KOTAKBANK.NS", name: "Kotak Mahindra Bank" },
  { ticker: "SBIN.NS", name: "State Bank of India" },
  { ticker: "BHARTIARTL.NS", name: "Bharti Airtel" },
  { ticker: "ITC.NS", name: "ITC Limited" },
  { ticker: "LT.NS", name: "Larsen & Toubro" },
] as const;

export type NiftyTicker = (typeof NIFTY_TICKERS)[number]["ticker"];

export const REFETCH_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
