**Kasparro --- Agentic Facebook Performance Analyst**

An autonomous, multi-agent AI system that acts as a full-stack marketing
analyst. It plans tasks, cleans messy data automatically, diagnoses
performance drops, and generates creative solutions using **Llama 3 (via
Groq)**.

**🏗 Architecture**

This system avoids linear scripting by implementing a
**Planner-Evaluator** architecture with a self-healing data layer.

graph TD

User(\[User Query\]) \--\> Planner{Planner Agent}

Planner \--\>\|\'analyze_metrics\'\| Insight\[Insight Agent\]

Planner \--\>\|\'generate_creatives\'\| Creative\[Creative Agent\]

subgraph \"Data Layer (Deterministic)\"

Data\[Data Agent\] \--\>\|Map-Reduce Cleaning\| LLM\[LLM (Groq)\]

Data \--\>\|Summary Stats\| Insight

end

Insight \--\>\|Hypothesis\| Evaluator{Evaluator Agent}

Evaluator \-- Validated \--\> Report\[Final Report\]

Evaluator \-- Rejected \--\> Insight

Creative \--\>\|Bad Ads\| LLM

LLM \--\> NewAds\[New Creatives\]

**Key Agents**

1.  **Planner Agent:** Decomposes complex user queries into subtasks
    (e.g., determines if the user wants just analysis or analysis +
    creative fixes).

2.  **Data Agent:** Implements a self-healing pipeline using LLM
    Map-Reduce to fix messy campaign names (e.g., normalizes Cooli-g -\>
    Cooling).

3.  **Insight Agent:** Generates hypothesis-driven diagnosis of ROAS
    trends.

4.  **Evaluator Agent:** Acts as a \"Critic,\" quantitatively validating
    text insights against raw data numbers (0-1 Confidence Score).

5.  **Creative Agent:** Rewrites underperforming ads using
    direct-response tactics (Hooks, Urgency, Benefits).

**🚀 Quick Start**

**Prerequisites**

-   Python \>= 3.10

-   A Groq API Key (Free beta keys available at
    [console.groq.com](https://console.groq.com))

**1. Installation**

Clone the repo and run the setup script (Mac/Linux/Git Bash):

chmod +x run.sh

./run.sh \"Why is ROAS dropping?\"

**Manual Setup (Windows/Standard):**

\# Create and activate virtual environment

python -m venv .venv

source .venv/bin/activate \# Windows: .venv\\Scripts\\activate

\# Install pinned dependencies

pip install -r requirements.txt

**2. Configuration**

Create a .env file in the root directory:

GROQ_API_KEY=gsk_your_key_here

**3. Run the Analyst**

**Diagnostic Mode (Fast):**

python src/run.py \"Why did ROAS drop last week?\"

*Planner Action: \[\'analyze_metrics\'\]*

**Full-Stack Mode (Diagnostic + Creative):**

python src/run.py \"Why did ROAS drop and please suggest new
creatives?\"

*Planner Action: \[\'analyze_metrics\', \'generate_creatives\'\]*

**⚙️ Configuration & Reproducibility**

Edit config/config.yaml to control system behavior. This project uses
**pinned random seeds** to ensure reproducible AI outputs.

  -----------------------------------------------------------------------------
  **Setting**            **Description**                          **Default**
  ---------------------- ---------------------------------------- -------------
  data.use_sample_data   Toggle for debugging (loads first 50     false
                         rows)                                    

  system.random_seed     Ensures deterministic results across     42
                         runs                                     

  thresholds.low_ctr     Cutoff for flagging underperforming ads  0.015

  thresholds.roas_drop   Sensitivity for performance alerts       0.10
  -----------------------------------------------------------------------------

**✅ Validation Layer (Quality Assurance)**

To prevent \"hallucinations,\" this system implements a strict
**Quantitative Validation Loop**:

1.  **Hypothesis Generation:** The Insight Agent proposes a reason for
    performance changes (e.g., \"Spend dropped by 10%\").

2.  **Verification:** The EvaluatorAgent receives the hypothesis and the
    raw data summary.

3.  **Scoring:** It assigns a **Confidence Score (0.0 - 1.0)**.

4.  **Reflection:** If Confidence \< 0.5, the Orchestrator rejects the
    insight and forces the Insight Agent to retry with a stricter
    \"Data-Driven\" prompt.

**📂 Outputs & Evidence**

After execution, artifacts are generated in the reports/ folder:

-   **report.md**: The final executive summary, including the diagnosis,
    validation logs, and recommended actions.

-   **creatives.json**: A JSON array of AI-generated ad variations
    mapped to their original failing ads.

-   **insights.json**: Structured performance metrics and validation
    confidence scores (ready for dashboard ingestion).

-   **logs/execution.jsonl**: Machine-readable logs for observability
    and debugging.

**🛠 Project Structure**

kasparro-agentic-fb-analyst/

├── config/ \# Configuration thresholds and paths

├── data/ \# Dataset location and documentation

├── logs/ \# JSONL execution logs (Gitignored, but folder structure
kept)

├── prompts/ \# Raw Prompt Engineering files (.md)

├── reports/ \# Generated artifacts (Markdown & JSON)

├── src/

│ ├── agents/ \# Individual Agent Logic (Planner, Data, Evaluator, etc.)

│ ├── utils/ \# Shared utilities (Logger, LLM Client)

│ └── run.py \# Main Orchestrator logic

├── tests/ \# Unit tests for the Evaluator

├── run.sh \# Automation script

├── requirements.txt \# Pinned dependencies

└── README.md \# Documentation

**🧪 Testing**

Run the unit test suite to verify the Data Agent and LLM connectivity:

python -m unittest tests/test_evaluator.py

**Architecture v1.0 implemented by \[Sunil Kumar\]**