import json
import os
from src.utils.logger import get_logger

logger = get_logger("PlannerAgent")

class PlannerAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def create_plan(self, user_query):
        logger.info(f"Decomposing query: {user_query}")
        
        prompt_path = os.path.join("prompts", "planner_prompt.md")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            # Fallback default plan
            return ["analyze_metrics", "generate_creatives"]

        response = self.llm.generate(system_prompt, f"User Query: {user_query}")
        
        try:
            # Clean and parse JSON
            clean_response = response.replace("```json", "").replace("```", "").strip()
            plan = json.loads(clean_response)
            logger.info(f"Plan generated: {plan}")
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}. using default full pipeline.")
            return ["analyze_metrics", "generate_creatives"]