# DSC180A_Replication_Project - Parna Praveen
## The features that I added is at the end of this README file. My feature is for evaluation metrics.

# Life Sciences Knowledge Graph Agent
# 🧬 Helix Navigator

**Learn LangGraph and Knowledge Graphs through Biomedical AI**

An interactive educational project that teaches modern AI development through hands-on biomedical applications. Build AI agents that answer complex questions about genes, proteins, diseases, and drugs using graph databases and multi-step AI workflows.


## What You'll Learn

- **Knowledge Graphs**: Represent domain knowledge as nodes and relationships
- **LangGraph**: Build multi-step AI workflows with state management  
- **Cypher Queries**: Query graph databases effectively
- **AI Integration**: Combine language models with structured knowledge
- **Biomedical Applications**: Apply AI to drug discovery and personalized medicine

## Quick Start

1. **New to these concepts?** Read the [Foundations Guide](docs/foundations-and-background.md)
2. **Setup**: Follow [Getting Started](docs/getting-started.md) for installation
3. **Learn**: Use the interactive Streamlit web interface
4. **Practice**: Work through the exercises in the web app

## Technology Stack

- **LangGraph**: AI workflow orchestration
- **Neo4j**: Graph database
- **Anthropic Claude**: Language model
- **Streamlit**: Interactive web interface
- **LangGraph Studio**: Visual debugging

## Installation

**Quick Setup**: Python 3.10+, Neo4j, PDM

```bash
# Install dependencies
pdm install

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Load data and start
pdm run load-data
pdm run app
```

## Project Structure

```
├── src/agents/              # AI agent implementations
├── src/web/app.py          # Interactive Streamlit interface
├── docs/                   # Documentation and tutorials
├── data/                   # Biomedical datasets
├── scripts/                # Data loading utilities
└── tests/                  # Test suite
```

**Key Files**:
- `src/agents/workflow_agent.py` - Main LangGraph agent
- `src/web/app.py` - Interactive Streamlit interface
- `docs/` - Complete documentation

## Running the Application

### Basic Usage
```bash
pdm run load-data         # Load biomedical data
pdm run app              # Start web interface
```

### Visual Debugging
```bash
pdm run langgraph    # Start LangGraph Studio
```

### Development
```bash
pdm run test            # Run tests (14 tests)
pdm run format          # Format code
pdm run lint            # Check quality
```

**Full commands**: See [Reference Guide](docs/reference.md)

## AI Agent

**WorkflowAgent** - LangGraph implementation with transparent processing for learning core LangGraph concepts through biomedical applications

## Example Questions

- **"Which drugs have high efficacy for treating diseases?"**
- **"Which approved drugs treat cardiovascular diseases?"**
- **"Which genes encode proteins that are biomarkers for diseases?"**
- **"What drugs target proteins with high confidence disease associations?"**
- **"Which approved drugs target specific proteins?"**
- **"Which genes are linked to multiple disease categories?"**
- **"What proteins have causal associations with diseases?"** 

## Evaluation Module - I ADDED THIS PART

### Note: This is starter code for adding evaluation metrics for each query. I have not made that much progress on this yet but the idea is to include node or system level evaluation metrics to help improve the system over time. 

### The system evaluates AI agent performance using four key metrics:

#### Classification Accuracy

Measures how well the agent identifies the intent of the user's question (e.g., distinguishing between gene-disease queries vs. drug-treatment queries). High classification accuracy ensures the agent follows the correct workflow path from the start.

#### Entity Accuracy

Measures how accurately the agent extracts key biomedical terms (e.g., "Hypertension," "Lisinopril," "Breast Cancer") from questions. This is foundational—if entities aren't correctly identified, the agent cannot construct precise database queries.

#### Answer Accuracy

Measures how well the agent's final generated answer matches the expected factual outcome. This is the ultimate end-to-end performance measure, confirming whether the entire workflow (classification → extraction → query generation → execution → formatting) produces correct results.

#### Average Query Duration 

Measures the time taken to execute each query, providing insight into system efficiency and user experience. This metric is critical for evaluating real-world performance and scalability.

### Conversation Memory Enhancement (NEW)

This enhancement introduces session history tracking, allowing the agent to remember past turns in a conversation. By providing the LLM with context from previous questions and answers, the agent can better understand follow-up questions and generate more coherent and accurate responses in multi-turn interactions. This leads to improved performance on related questions within a single session.

The benchmark dataset in `evaluation_metrics/golden_dataset.json` now contains linked multi-turn conversations (e.g., “What genes are associated with Hypertension?” followed by “Which drugs treat it?”). These scenarios ensure that the Conversation Memory flag has measurable impact during evaluation.

### Chain-of-Thought Reasoning Enhancement (NEW)

This enhancement integrates chain-of-thought prompting into the agent's workflow. Instead of directly providing an answer, the LLM is prompted to "think step-by-step" through its reasoning process for tasks like question classification, entity extraction, query generation, and answer formatting. This approach aims to improve the quality and accuracy of the LLM's outputs by making its internal reasoning more explicit and structured.

### Project Extensions and Modified Files (NEW)

To implement the evaluation metrics, conversation memory, and chain-of-thought reasoning, the following new folders and files were added, and existing core files were modified:

#### New Folders and Their Contents:

*   `evaluation_metrics/`:
    *   `evaluation_metrics.py`: The main script for running evaluations.
    *   `golden_dataset.json`: The benchmark dataset used for evaluation.
    *   `test_evaluation_metrics.py`: Unit tests for the evaluation module.
*   `conversation_memory/`:
    *   `memory_manager.py`: Contains the `MemoryManager` class for storing and formatting conversation history.
*   `cot_prompts/`:
    *   `classification_prompt.py`: Chain-of-Thought enhanced prompt for question classification.
    *   `entity_extraction_prompt.py`: Chain-of-Thought enhanced prompt for entity extraction.
    *   `query_generation_prompt.py`: Chain-of-Thought enhanced prompt for Cypher query generation.
    *   `answer_formatting_general_knowledge_prompt.py`: Chain-of-Thought enhanced prompt for formatting general knowledge answers.
    *   `answer_formatting_db_results_prompt.py`: Chain-of-Thought enhanced prompt for formatting database results.

#### Main Modified Files:

*   `src/agents/workflow_agent.py`: This core agent file was modified to:
    *   Import `MemoryManager` and the CoT prompts.
    *   Integrate a `conversation_memory` flag to enable/disable session history.
    *   Integrate a `chain_of_thought` flag to enable/disable CoT prompts.
    *   Update `__init__`, `_get_llm_response`, `answer_question`, `_build_classification_prompt`, `extract_entities`, `generate_query`, and `format_answer` to incorporate the new logic and conditional prompt usage.
*   `evaluation_metrics/evaluation_metrics.py`: Modified to orchestrate the running of four distinct evaluation scenarios (Baseline, Memory Only, CoT Only, Both) and to clearly separate their results for comparison.
*   `README.md` (this file): Updated to reflect the new features and evaluation instructions.

### Together, these metrics provide granular insights into where the agent may be failing:

1. Low classification + high entity accuracy → LLM struggles with context selection but excels at term identification
2. High classification + entity accuracy but low answer accuracy → Issues in query generation or answer formatting


To evaluate the workflow agent:

To run the comprehensive evaluation across different configurations, you can use the `evaluation_metrics.py` script. This script will run four distinct scenarios and output their performance metrics.

### Running the Evaluation

```bash
python -m evaluation_metrics.evaluation_metrics
```

This command will execute the evaluation for the following scenarios:

1.  **Scenario 1: No Enhancements (Baseline)**:
    *   Conversation Memory: OFF
    *   Chain-of-Thought: OFF
    *   This represents the agent's performance without any of the added enhancements.

2.  **Scenario 2: Conversation Memory ON Only**:
    *   Conversation Memory: ON
    *   Chain-of-Thought: OFF
    *   This shows the impact of enabling conversation memory in isolation.

3.  **Scenario 3: Chain-of-Thought ON Only**:
    *   Conversation Memory: OFF
    *   Chain-of-Thought: ON
    *   This shows the impact of enabling chain-of-thought reasoning in isolation.

4.  **Scenario 4: Conversation Memory ON & Chain-of-Thought ON**:
    *   Conversation Memory: ON
    *   Chain-of-Thought: ON
    *   This demonstrates the combined impact of both enhancements.

### Interpreting Results

The results for each scenario will be printed to your terminal and also saved to `evaluation_metrics/evaluation_results.txt`. Each scenario's metrics are clearly labeled and include deltas relative to the baseline. Look for improvements in `classification_accuracy`, `entity_accuracy`, and `answer_accuracy` when enhancements are active. A slight increase in `average_query_duration_seconds` is expected when more complex reasoning or context processing is involved.

### Latest Evaluation Snapshot

Results from the most recent run (`evaluation_metrics/evaluation_results.txt`):

```5:46:evaluation_metrics/evaluation_results.txt
Scenario 1 (Baseline): classification 0.75, entity 0.12, answer 0.12
Scenario 2 (Memory): classification 0.75, entity 0.25, answer 0.12
Scenario 3 (CoT): classification 0.75, entity 0.38, answer 0.25
Scenario 4 (Memory + CoT): classification 0.88, entity 0.38, answer 0.25
```

Key takeaways:
- Memory alone improves entity recall on follow-up questions that depend on prior turns.
- Chain-of-thought significantly boosts both entity and answer accuracy by forcing step-by-step reasoning.
- Combining Memory + CoT yields the best classification accuracy (0.88) while maintaining the answer-quality gains.

## License

MIT License
