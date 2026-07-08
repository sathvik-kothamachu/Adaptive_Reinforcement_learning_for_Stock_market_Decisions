import React from 'react';
import { Bot, MessageSquare } from 'lucide-react';

const AssistantPage = () => {
  return (
    <div className="animate-fade-up flex flex-col h-[calc(100vh-12rem)] md:h-auto">
      <header className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Nifty Assistant</h1>
        <p className="text-muted-foreground mt-2 flex items-center gap-2">
          <Bot size={16} className="text-primary" />
          Powered by Gemini 1.5 Flash
        </p>
      </header>

      <div className="flex-1 flex items-center justify-center glass-dark rounded-3xl p-10 text-center border-none">
        <div className="max-w-md space-y-6">
          <div className="mx-auto w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
            <MessageSquare className="text-primary w-8 h-8" />
          </div>
          <h2 className="text-xl font-semibold text-foreground">Mobile Chat Interface</h2>
          <p className="text-muted-foreground leading-relaxed">
            The full-screen conversational interface is optimized for the mobile tab. 
            On desktop, use the floating widget in the corner for a multitasking experience.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AssistantPage;
