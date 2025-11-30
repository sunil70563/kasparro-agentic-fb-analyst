import sys
import os
import yaml
import json
import random
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.creative_generator import CreativeGenerator
from src.agents.planner import PlannerAgent
from src.agents.evaluator import EvaluatorAgent
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger("Orchestrator")

def load_config():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(base_dir, "config", "config.yaml"), "r") as f:
        return yaml.safe_load(f)

def set_seed(seed):
    """Ensures reproducibility across runs."""
    random.seed(seed)
    np.random.seed(seed)
    logger.info(f"Random seed set to {seed}")

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "Analyze ROAS drop"
    
    logger.info("Starting Kasparro Agentic Analyst v1.1...")
    
    # 1. Setup
    config = load_config()
    set_seed(config['system']['random_seed'])
    
    llm_client = LLMClient(config)
    planner = PlannerAgent(llm_client)
    data_agent = DataAgent(config)
    insight_agent = InsightAgent(llm_client)
    evaluator = EvaluatorAgent(llm_client)
    creative_agent = CreativeGenerator(llm_client)

    # 2. Plan
    plan = planner.create_plan(query)
    
    # 3. Execute
    try:
        data_agent.load_and_clean()
        summary = data_agent.get_performance_summary()
    except Exception as e:
        logger.error(f"Data failure: {e}")
        return

    analysis = "No analysis requested."
    validation = None
    new_creatives = []

    if "analyze_metrics" in plan:
        analysis = insight_agent.analyze(summary, query)
        validation = evaluator.validate(summary, analysis)
        
        # Reflection Loop
        if validation.get('confidence_score', 0) < 0.5:
            logger.warning("Low confidence. Retrying...")
            analysis = insight_agent.analyze(summary, query + " Be strictly data-driven.")
            validation = evaluator.validate(summary, analysis)

    if "generate_creatives" in plan:
        bad_ads = data_agent.get_bad_creatives()
        new_creatives = creative_agent.generate_variations(bad_ads)

    # 4. Save
    base_dir = os.path.dirname(os.path.dirname(__file__))
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_path = os.path.join(reports_dir, "report.md")
    with open(report_path, "w") as f:
        f.write(f"# Analysis Report\n\n## Query: {query}\n\n## Diagnosis\n{analysis}\n\n## Validation\n{json.dumps(validation, indent=2)}")
        
    with open(os.path.join(reports_dir, "insights.json"), "w") as f:
        json.dump({"summary": summary, "validation": validation}, f, indent=2)
        
    with open(os.path.join(reports_dir, "creatives.json"), "w") as f:
        json.dump(new_creatives, f, indent=2)

    logger.info(f"Pipeline Complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()