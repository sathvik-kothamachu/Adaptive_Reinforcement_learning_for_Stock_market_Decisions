import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
import ollama
import httpx

logger = logging.getLogger(__name__)

class OllamaSupportBot:
    def __init__(self, model_id: str = "llama3.2"):
        logger.info(f"🔄 Initializing Local Ollama Bot with model: {model_id}...")
        self.model_id = model_id
        self.client = ollama.AsyncClient()
        self.docs_context = self._load_docs()

    def _load_docs(self) -> str:
        docs_files = ['README.md', 'ARCHITECTURE.md', 'QUICK_REFERENCE.md', 'INTEGRATION_GUIDE.md']
        context = "Project Documentation Summary:\n"
        for file in docs_files:
            if os.path.exists(file):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        context += f"- {file}: {f.read()[:500]}...\n"
                except: pass
        return context

    async def check_connection(self) -> bool:
        """Verify if Ollama is running and accessible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def get_response(self, message: str, ticker: Optional[str] = None, analysis_context: Optional[Dict[str, Any]] = None) -> str:
        system_prompt = f"You are a professional stock analyst for the Nifty 50. Use the following context to answer questions about the project or stocks: {self.docs_context}"
        
        if ticker and analysis_context:
            user_input = f"Ticker: {ticker}\nAnalysis: {analysis_context}\nQuestion: {message}"
        else:
            user_input = message

        try:
            response = await self.client.chat(model=self.model_id, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input},
            ])
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama Error: {e}")
            if "not found" in str(e).lower():
                logger.info(f"Model {self.model_id} not found. Attempting to pull...")
                try:
                    await self.client.pull(self.model_id)
                    return "I was just setting up my brain (pulling the model). Please try asking again in a moment!"
                except: pass
            
            if "connection" in str(e).lower() or "connect" in str(e).lower():
                return "❌ Error: Cannot connect to local Ollama. Please ensure Ollama is running ('ollama serve')."
                
            raise

# Singleton instance
_bot_instance = None

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        # Always use local Ollama bot as per user request
        _bot_instance = OllamaSupportBot()
        logger.info("✅ Local Ollama Bot ready.")
    return _bot_instance
