import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { Header } from "@/components/dashboard/Header";
import { HeroSignal } from "@/components/dashboard/HeroSignal";
import { ScoreCard } from "@/components/dashboard/ScoreCard";
import { IndicatorsPanel } from "@/components/dashboard/IndicatorsPanel";
import { SentimentPanel } from "@/components/dashboard/SentimentPanel";
import { RegimePanel } from "@/components/dashboard/RegimePanel";
import { BacktestPanel } from "@/components/dashboard/BacktestPanel";
import { ChatBot } from "@/components/dashboard/ChatBot";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { useAnalysis } from "@/hooks/useAnalysis";
import { isUsingMock } from "@/lib/api";
import { NIFTY_TICKERS } from "@/lib/constants";

export default function Index() {
  const [ticker, setTicker] = useState<string>(NIFTY_TICKERS[0].ticker); // Reliance default
  const queryClient = useQueryClient();
  const { data, isLoading, isFetching, error, dataUpdatedAt, refetch } = useAnalysis(ticker);
  const lastErrorRef = useRef<string | null>(null);
  const mockToastShown = useRef(false);

  useEffect(() => {
    if (error) {
      const msg = (error as Error).message;
      if (lastErrorRef.current !== msg) {
        lastErrorRef.current = msg;
        toast.error("Could not load analysis", { description: msg });
      }
    } else {
      lastErrorRef.current = null;
    }
  }, [error]);

  useEffect(() => {
    if (isUsingMock && !mockToastShown.current) {
      mockToastShown.current = true;
      toast("Demo mode", {
        description: "Set VITE_API_BASE_URL to connect your Python API.",
      });
    }
  }, []);

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["analysis", ticker] });
    refetch();
  };

  const lastUpdated = useMemo(
    () => (dataUpdatedAt ? new Date(dataUpdatedAt) : undefined),
    [dataUpdatedAt]
  );

  return (
    <div className="animate-fade-in">
      <Header
        ticker={ticker}
        onTickerChange={setTicker}
        onRefresh={handleRefresh}
        isFetching={isFetching}
        lastUpdated={lastUpdated}
        hasError={!!error && !data}
      />

      <div className="mt-8">
        <AnimatePresence mode="wait">
          {isLoading || !data ? (
            <motion.div
              key="skeleton"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-12"
            >
              <DashboardSkeleton />
            </motion.div>
          ) : (
            <motion.div
              key={ticker}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-12"
            >
              {/* Hero Section */}
              <section className="mb-16">
                <HeroSignal
                  signal={data.signal}
                  ticker={data.ticker}
                  name={data.name}
                />
              </section>

              {/* Data Modules (Staggered Entry) */}
              <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
                <ScoreCard delay={0.1} label="Technical Score" score={data.technical_score} description="Price-action and indicator confluence" />
                <ScoreCard delay={0.2} label="Sentiment Score" score={data.sentiment_score} description="News + headline polarity" />
                <ScoreCard delay={0.3} label="Regime Score" score={data.regime_score} description="Macro market context" />
              </section>

              <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                <div className="animate-fade-up" style={{ animationDelay: '0.4s' }}>
                  <IndicatorsPanel indicators={data.indicators} />
                </div>
                <div className="animate-fade-up" style={{ animationDelay: '0.5s' }}>
                  <SentimentPanel
                    dates={data.sentiment_chart.dates}
                    scores={data.sentiment_chart.scores}
                    headlines={data.headlines}
                  />
                </div>
                <div className="animate-fade-up" style={{ animationDelay: '0.6s' }}>
                  <RegimePanel regime={data.market_regime} />
                </div>
              </section>

              <section className="animate-fade-up" style={{ animationDelay: '0.7s' }}>
                <BacktestPanel backtest={data.backtest} />
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <footer className="mt-16 py-8 text-center text-xs text-foreground/40 font-medium">
        Recommendations are model outputs, not financial advice. Auto-refreshes every 5 minutes.
      </footer>

      <ChatBot currentAnalysis={data} />
    </div>
  );
}
