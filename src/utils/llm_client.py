import os
from openai import OpenAI
from dotenv import load_dotenv
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("LLMClient")

class LLMClient:
    def __init__(self, config):
        self.config = config
        self.provider = config['llm'].get('provider', 'openai')
        self.client = None

        # Setup for Groq
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            base_url = config['llm']['base_url']
            if api_key:
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                logger.info("Connected to GROQ API.")
            else:
                logger.warning("GROQ_API_KEY not found in .env")

        # Fallback (Mock)
        if not self.client:
            logger.warning("Running in MOCK mode (No AI connected).")

    def generate(self, system_prompt, user_content):
        """Sends a request to the LLM."""
        if not self.client:
            return "MOCK RESPONSE: Set API Key to get real insights."

        try:
            response = self.client.chat.completions.create(
                model=self.config['llm']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=self.config['llm']['temperature']
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            return "Error generating insight."