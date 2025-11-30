import json
import os
from src.utils.logger import get_logger

logger = get_logger("CreativeGenerator")

class CreativeGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_variations(self, low_performing_ads):
        logger.info(f"Creative Agent is rewriting {len(low_performing_ads)} ads...")
        
        if not low_performing_ads:
            return []

        prompt_path = os.path.join("prompts", "creative_prompt.md")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            return []

        ads_str = json.dumps(low_performing_ads, indent=2)
        response = self.llm.generate(system_prompt, f"Here are the failing ads: {ads_str}")
        
        # Clean response (Groq is usually good, but safety first)
        clean_response = response.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_response)
        except:
            logger.warning("Failed to parse JSON from LLM.")
            return []