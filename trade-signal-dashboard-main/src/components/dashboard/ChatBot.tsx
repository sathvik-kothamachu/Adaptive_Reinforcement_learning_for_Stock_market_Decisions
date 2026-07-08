import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import { MessageSquare, Send, X, Bot, User, Loader2, Trash2, GripHorizontal } from 'lucide-react';
import { motion, useDragControls, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { sendChatMessage } from '@/lib/api';
import { type Analysis } from '@/lib/schema';

interface Message {
  role: 'bot' | 'user';
  content: string;
  timestamp: Date;
}

interface ChatBotProps {
  currentAnalysis?: Analysis | null;
}

const ChatMessage = memo(({ msg }: { msg: Message }) => {
  const formatContent = (content: string) => {
    return content.split(/(\*\*.*?\*\*)/g).map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex max-w-[85%] gap-2 rounded-2xl px-4 py-2.5 text-sm shadow-sm ${
          msg.role === 'user'
            ? 'bg-primary text-primary-foreground rounded-tr-none'
            : 'bg-muted rounded-tl-none border border-border/50'
        }`}
      >
        {msg.role === 'bot' && <Bot className="mt-1 h-4 w-4 shrink-0 text-primary/80" />}
        <div className="leading-relaxed whitespace-pre-wrap font-medium text-foreground">
          {formatContent(msg.content)}
        </div>
        {msg.role === 'user' && <User className="mt-1 h-4 w-4 shrink-0 opacity-70" />}
      </div>
    </div>
  );
});

ChatMessage.displayName = 'ChatMessage';

export const ChatBot = memo(({ currentAnalysis }: ChatBotProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      content: 'Hello! I am your Nifty 50 RL Analytical Assistant.\n\nAsk me to:\n• **Explain** current signals\n• **Analyze** technical data\n• **Summarize** project architecture',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dragControls = useDragControls();

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen, scrollToBottom]);

  const handleSendMessage = useCallback(async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMsg = inputValue.trim();
    setMessages((prev) => [...prev, { role: 'user', content: userMsg, timestamp: new Date() }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userMsg, currentAnalysis?.ticker, currentAnalysis);
      setMessages((prev) => [...prev, { role: 'bot', content: response, timestamp: new Date() }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content: `Error: ${error instanceof Error ? error.message : 'Connection failed'}.`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, currentAnalysis]);

  const clearChat = useCallback(() => {
    setMessages([{
      role: 'bot',
      content: 'Conversation reset. Ready for new analysis.',
      timestamp: new Date(),
    }]);
  }, []);

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            drag
            dragControls={dragControls}
            dragListener={false}
            dragMomentum={false}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="mb-4 touch-none"
            style={{ x: 0, y: 0 }}
          >
            <Card 
              className="flex flex-col shadow-2xl border-none bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 overflow-hidden resize both min-w-[320px] min-h-[400px] max-w-[90vw] max-h-[80vh]"
              style={{ width: '400px', height: '550px' }}
            >
              <CardHeader 
                className="flex flex-row items-center justify-between border-b border-border px-4 py-3 bg-foreground/5 cursor-move active:cursor-grabbing select-none"
                onPointerDown={(e) => dragControls.start(e)}
              >
                <div className="flex items-center gap-2">
                  <div className="bg-primary/10 p-1.5 rounded-lg">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-sm font-bold text-foreground">Nifty Assistant</CardTitle>
                    <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                      Gemini Flash 1.5
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <GripHorizontal className="h-4 w-4 text-muted-foreground/30 mr-2" />
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-destructive" onClick={clearChat}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsOpen(false)}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 overflow-hidden p-0 bg-dot-pattern">
                <ScrollArea className="h-full px-4 py-6">
                  <div className="flex flex-col gap-5">
                    {messages.map((msg, idx) => (
                      <ChatMessage key={idx} msg={msg} />
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="flex items-center gap-2 rounded-2xl bg-muted px-4 py-2.5 text-xs text-muted-foreground animate-in fade-in slide-in-from-left-2 duration-300">
                          <Loader2 className="h-3 w-3 animate-spin" />
                          Analysing data...
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>
              </CardContent>

              <CardFooter className="border-t border-border p-3 bg-background relative">
                <form onSubmit={handleSendMessage} className="flex w-full items-center gap-2">
                  <Input
                    placeholder="Ask about signals..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={isLoading}
                    className="flex-1 h-10 bg-muted/50 border-none focus-visible:ring-1 ring-primary/20 text-foreground"
                  />
                  <Button 
                    type="submit" 
                    size="icon" 
                    disabled={isLoading || !inputValue.trim()}
                    className="h-10 w-10 shrink-0 shadow-sm"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
                {/* Visual indicator for resizing */}
                <div className="absolute bottom-0 right-0 w-4 h-4 cursor-nwse-resize opacity-20 hover:opacity-100 transition-opacity">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full text-primary">
                    <line x1="21" y1="21" x2="14" y2="21" />
                    <line x1="21" y1="21" x2="21" y2="14" />
                  </svg>
                </div>
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <Button
        onClick={() => setIsOpen((prev) => !prev)}
        className={`h-14 w-14 rounded-full shadow-2xl transition-all hover:scale-105 active:scale-95 ${
          isOpen ? 'bg-destructive hover:bg-destructive/90' : 'bg-primary hover:bg-primary/90 text-primary-foreground'
        }`}
        size="icon"
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageSquare className="h-6 w-6" />}
      </Button>
    </div>
  );
});

ChatBot.displayName = 'ChatBot';
