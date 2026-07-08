import { Skeleton } from "@/components/ui/skeleton";

export function DashboardSkeleton() {
  return (
    <div className="space-y-12" aria-busy="true" aria-label="Loading analysis">
      <Skeleton className="h-64 w-full rounded-[3rem] bg-white/5 border border-white/5" />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Skeleton className="h-44 rounded-[2rem] bg-white/5 border border-white/5" />
        <Skeleton className="h-44 rounded-[2rem] bg-white/5 border border-white/5" />
        <Skeleton className="h-44 rounded-[2rem] bg-white/5 border border-white/5" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Skeleton className="h-96 rounded-[2rem] bg-white/5 border border-white/5" />
        <Skeleton className="h-96 rounded-[2rem] bg-white/5 border border-white/5" />
        <Skeleton className="h-96 rounded-[2rem] bg-white/5 border border-white/5" />
      </div>
      <Skeleton className="h-40 rounded-[2rem] bg-white/5 border border-white/5" />
    </div>
  );
}
