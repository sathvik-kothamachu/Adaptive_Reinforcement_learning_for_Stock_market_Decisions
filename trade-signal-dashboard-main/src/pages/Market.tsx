import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { TrendingUp } from 'lucide-react';

const MarketPage = () => {
  return (
    <div className="animate-fade-up">
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Market Overview</h1>
        <p className="text-muted-foreground mt-2">Real-time performance across the Nifty 50 universe.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="glass border-none">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Nifty 50 Index</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">22,453.80</div>
            <p className="text-xs text-green-500 font-medium">+1.2% (+267.30)</p>
          </CardContent>
        </Card>
        
        {/* More market cards will go here */}
      </div>
      
      <div className="mt-12 p-8 glass-dark rounded-3xl border-none flex items-center justify-center">
        <p className="text-muted-foreground italic">Market depth and multi-stock heatmap visualization coming soon...</p>
      </div>
    </div>
  );
};

export default MarketPage;
