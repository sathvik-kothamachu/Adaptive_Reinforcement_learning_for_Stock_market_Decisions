import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";
import { REFETCH_INTERVAL_MS } from "@/lib/constants";

export function useAnalysis(ticker: string) {
  return useQuery({
    queryKey: ["analysis", ticker],
    queryFn: () => fetchAnalysis(ticker),
    refetchInterval: REFETCH_INTERVAL_MS,
    staleTime: REFETCH_INTERVAL_MS,
    refetchOnWindowFocus: false,
  });
}
