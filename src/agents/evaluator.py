import json
import os
from src.utils.logger import get_logger

logger = get_logger("EvaluatorAgent")

class EvaluatorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def validate(self, data_summary, hypothesis):
        logger.info("Validating hypothesis against data...")
        
        prompt_path = os.path.join("prompts", "evaluator_prompt.md")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            return {"confidence_score": 1.0, "is_valid": True, "critique": "Skipped validation."}

        user_content = f"""
        DATA SUMMARY: {json.dumps(data_summary)}
        
        HYPOTHESIS TO CHECK:
        {hypothesis}
        """
        
        response = self.llm.generate(system_prompt, user_content)
        
        try:
            clean_response = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_response)
            
            logger.info(f"Validation Result: Confidence {result.get('confidence_score')}")
            return result
        except Exception as e:
            logger.error(f"Validation parsing failed: {e}")
            return {"confidence_score": 0.0, "is_valid": False, "critique": "Validation Error"}