import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Settings, Shield, Cpu, Terminal } from 'lucide-react';

const SettingsPage = () => {
  return (
    <div className="animate-fade-up">
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">System Setup</h1>
        <p className="text-muted-foreground mt-2">Configure backend parameters and model integration.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="glass border-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 text-lg">
              <Terminal className="h-5 w-5 text-primary" />
              API Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-black/40 rounded-xl border border-white/5 font-mono text-xs">
              VITE_API_BASE_URL=http://localhost:8000
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Ensure the FastAPI backend is running before accessing analysis data.
            </p>
          </CardContent>
        </Card>

        <Card className="glass border-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 text-lg">
              <Cpu className="h-5 w-5 text-primary" />
              Model Settings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Configure RL hyperparameters and backtest intervals (Coming soon).
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SettingsPage;
