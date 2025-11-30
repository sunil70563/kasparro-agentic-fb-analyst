import json
import os
from src.utils.logger import get_logger

logger = get_logger("InsightAgent")

class InsightAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze(self, data_summary, user_query):
        logger.info("Analyst Agent is thinking...")
        
        prompt_path = os.path.join("prompts", "insight_prompt.md")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            return "Error: Prompt file missing."

        # Pass data to LLM
        user_content = f"""
        User Query: {user_query}
        Data Summary:
        {json.dumps(data_summary, indent=2)}
        """

        return self.llm.generate(system_prompt, user_content)