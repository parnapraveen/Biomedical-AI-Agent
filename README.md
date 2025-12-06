# 🧬 Helix Navigator
## Life Sciences Knowledge Graph Agent

**Learn LangGraph and Knowledge Graphs through Biomedical AI**

An interactive educational project that teaches modern AI development through hands-on biomedical applications. Build AI agents that answer complex questions about genes, proteins, diseases, and drugs using graph databases and multi-step AI workflows.

## Introduction

This repository contains a Python-based framework for building AI agents that interact with biomedical knowledge graphs. The system uses LangGraph to orchestrate a multi-step workflow (Classify → Extract → Generate → Execute → Format) that combines Large Language Models (LLMs) with Neo4j graph databases to answer complex biomedical questions.

The primary goal of this project is to demonstrate how structured knowledge graphs can enhance LLM capabilities, providing accurate, verifiable answers to domain-specific questions while avoiding hallucinations. The framework includes enhancements for conversation memory and chain-of-thought reasoning to improve accuracy and enable multi-turn conversations.

## Folder Structure (Look for files)

```
DSC180A_Replication_Project/
│
├── data/                        <- Biomedical datasets (CSV files)
│   ├── diseases.csv
│   ├── drugs.csv
│   ├── genes.csv
│   ├── proteins.csv
│   ├── drug_disease_treatments.csv
│   ├── drug_protein_targets.csv
│   └── protein_disease_associations.csv
│
├── docs/                        <- Documentation and tutorials
│   ├── foundations-and-background.md
│   ├── getting-started.md
│   ├── reference.md
│   └── technical-guide.md
│
├── evaluation_metrics/          <- NEW: Evaluation framework and benchmark dataset
│   ├── evaluation_metrics.py    <- Main evaluation script (runs 4 scenarios)
│   ├── golden_dataset.json      <- Benchmark dataset with multi-turn conversations
│   ├── evaluation_results.txt   <- Output file with evaluation metrics
│   └── test_evaluation_metrics.py
│
├── langgraph-studio/            <- LangGraph Studio configuration
│   ├── langgraph_studio.py
│   └── langgraph.json
│
├── scripts/                     <- Data loading and utility scripts
│   ├── load_data.py
│   └── quickstart.py
│
├── src/                         <- Main source code
│   ├── agents/
│   │   ├── graph_interface.py   <- Neo4j database interface
│   │   └── workflow_agent.py    <- MODIFIED: Core LangGraph agent with enhancements
│   ├── memory/                  <- NEW: Conversation memory enhancement module
│   │   ├── __init__.py
│   │   └── memory_manager.py   <- MemoryManager class for storing conversation history
│   ├── prompts/                 <- NEW: Chain-of-thought reasoning prompts
│   │   ├── __init__.py
│   │   ├── classification_prompt.py
│   │   ├── entity_extraction_prompt.py
│   │   ├── query_generation_prompt.py
│   │   ├── answer_formatting_general_knowledge_prompt.py
│   │   └── answer_formatting_db_results_prompt.py
│   └── web/
│       └── app.py               <- Interactive Streamlit interface
│
├── tests/                       <- Test suite
│   ├── test_app.py
│   ├── test_graph_interface.py
│   └── test_workflow_agent.py
│
├── .env.example                 <- Environment variables template
├── .gitignore
├── pyproject.toml               <- Project configuration and dependencies
├── pytest.ini                   <- Pytest configuration
└── README.md                    <- This file
```

## Features

### Core Functionality
- **Multi-Step Workflow**: LangGraph-based agent with 5 distinct steps (Classify → Extract → Generate → Execute → Format)
- **Knowledge Graph Integration**: Direct integration with Neo4j for structured biomedical data
- **LLM-Powered**: Uses Anthropic Claude for natural language understanding and generation
- **Dynamic Schema Discovery**: Automatically discovers database schema and property values
- **Interactive Interface**: Streamlit web app for interactive question-answering

### Enhancements (NEW)

#### 1. Conversation Memory
- **Session History Tracking**: Remembers past conversation turns within a session
- **Context-Aware Responses**: Uses previous questions and answers to understand follow-up questions
- **Multi-Turn Support**: Handles pronoun references (e.g., "it", "they", "that disease") by leveraging conversation context
- **Memory Manager**: Clean API for storing and formatting conversation history

#### 2. Chain-of-Thought Reasoning
- **Step-by-Step Thinking**: Prompts the LLM to explicitly reason through each step
- **Enhanced Prompts**: Specialized CoT prompts for classification, entity extraction, query generation, and answer formatting
- **Improved Accuracy**: Forces the model to show its reasoning process, leading to more accurate outputs
- **Structured Reasoning**: Makes the LLM's internal decision-making process transparent

#### 3. Comprehensive Evaluation Framework
- **Four Evaluation Scenarios**: Baseline, Memory Only, CoT Only, and Both
- **Multi-Turn Benchmark Dataset**: Golden dataset with linked conversations to test memory capabilities
- **Four Key Metrics**: Classification accuracy, entity accuracy, answer accuracy, and query duration
- **Automated Comparison**: Calculates improvements over baseline for each scenario

## Methodology

The agent follows a structured workflow:

1. **Classification**: Determines the question type (gene_disease, drug_treatment, protein_function, general_db, general_knowledge)
2. **Entity Extraction**: Identifies specific biomedical entities and property values from the question
3. **Query Generation**: Constructs a Cypher query using the schema, entities, and question type
4. **Query Execution**: Runs the query against the Neo4j database
5. **Answer Formatting**: Converts raw database results into natural language responses

When enhancements are enabled:
- **Conversation Memory**: Provides previous conversation context at each step
- **Chain-of-Thought**: Uses specialized prompts that encourage step-by-step reasoning

## Installation and Setup

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: Python 3.10 or higher
- **Neo4j**: Neo4j database (local or remote)
- **Memory**: 8GB+ RAM recommended
- **API Keys**: Anthropic API key for Claude access

### Dependencies

This project uses PDM for dependency management. Key dependencies include:
- `langgraph`: AI workflow orchestration
- `anthropic`: Anthropic Claude API client
- `neo4j`: Neo4j Python driver
- `streamlit`: Web interface framework
- `pandas`: Data manipulation
- `tqdm`: Progress bars

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Biomedical-AI-Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install pdm
   pdm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Neo4j credentials
   ```

4. **Set up Neo4j**:
   - Install Neo4j Desktop or use a remote instance
   - Create a database
   - Update `.env` with your Neo4j URI, username, and password

5. **Load data into Neo4j**:
   ```bash
   pdm run load-data
   ```

## Usage

### Running the Interactive Web Interface

```bash
pdm run app
```

This starts the Streamlit web interface where you can interact with the agent through a user-friendly UI.

### Running Evaluations

To evaluate the agent's performance across different enhancement configurations:

```bash
python -m evaluation_metrics.evaluation_metrics
```

This command runs four distinct scenarios:

1. **Scenario 1: Baseline (No Enhancements)**
   - Conversation Memory: OFF
   - Chain-of-Thought: OFF
   - Represents the agent's baseline performance

2. **Scenario 2: Conversation Memory ON**
   - Conversation Memory: ON
   - Chain-of-Thought: OFF
   - Shows the impact of conversation memory in isolation

3. **Scenario 3: Chain-of-Thought ON**
   - Conversation Memory: OFF
   - Chain-of-Thought: ON
   - Shows the impact of chain-of-thought reasoning in isolation

4. **Scenario 4: Memory + Chain-of-Thought**
   - Conversation Memory: ON
   - Chain-of-Thought: ON
   - Demonstrates the combined impact of both enhancements

Results are saved to `evaluation_metrics/evaluation_results.txt` and include:
- Classification accuracy
- Entity accuracy
- Answer accuracy
- Average query duration
- Improvement deltas over baseline

### Visual Debugging

To use LangGraph Studio for workflow visualization:

```bash
pdm run langgraph
```

### Development

```bash
pdm run test            # Run tests
pdm run format          # Format code
pdm run lint            # Check code quality
```

## Evaluation Metrics

The evaluation framework measures four key metrics:

### Classification Accuracy
Measures how well the agent identifies the intent of the user's question (e.g., distinguishing between gene-disease queries vs. drug-treatment queries). High classification accuracy ensures the agent follows the correct workflow path from the start.

### Entity Accuracy
Measures how accurately the agent extracts key biomedical terms (e.g., "Hypertension," "Lisinopril," "Breast Cancer") from questions. This is foundational—if entities aren't correctly identified, the agent cannot construct precise database queries.

### Answer Accuracy
Measures how well the agent's final generated answer matches the expected factual outcome. This is the ultimate end-to-end performance measure, confirming whether the entire workflow produces correct results.

### Average Query Duration
Measures the time taken to execute each query, providing insight into system efficiency and user experience.

![Performance Comparison](figure/performance_comparison.pdf)

*Figure 2: Performance comparison across four evaluation scenarios showing classification, entity, and answer accuracy metrics.*

### Latest Evaluation Results

Results from the most recent evaluation run:

```
Scenario 1 (Baseline): 
  classification_accuracy: 0.75
  entity_accuracy: 0.12
  answer_accuracy: 0.12

Scenario 2 (Memory Only): 
  classification_accuracy: 0.75 (+0.00)
  entity_accuracy: 0.25 (+0.12)
  answer_accuracy: 0.12 (+0.00)

Scenario 3 (CoT Only): 
  classification_accuracy: 0.75 (+0.00)
  entity_accuracy: 0.38 (+0.25)
  answer_accuracy: 0.25 (+0.12)

Scenario 4 (Memory + CoT): 
  classification_accuracy: 0.88 (+0.12)
  entity_accuracy: 0.38 (+0.25)
  answer_accuracy: 0.25 (+0.12)
```

**Key Takeaways:**
- Memory alone improves entity recall on follow-up questions that depend on prior turns
- Chain-of-thought significantly boosts both entity and answer accuracy by forcing step-by-step reasoning
- Combining Memory + CoT yields the best classification accuracy (0.88) while maintaining the answer-quality gains

## Example Questions

The agent can answer questions such as:

- **"Which drugs treat Hypertension?"**
- **"What genes are associated with Breast Cancer?"**
- **"Which approved drugs are small molecules?"**
- **"What is the category of Breast Cancer?"**
- **"Which drugs treat it?"** (requires conversation memory to understand "it")
- **"Are they approved?"** (requires conversation memory to understand "they")

## Project Extensions

### New Folders and Files

The following enhancements were added to the original project:

**`evaluation_metrics/`** (at root level):
- `evaluation_metrics.py`: Main evaluation script that runs all four scenarios
- `golden_dataset.json`: Benchmark dataset with multi-turn conversations
- `evaluation_results.txt`: Output file with detailed metrics
- `test_evaluation_metrics.py`: Unit tests for the evaluation module

**`src/memory/`** (NEW - moved from root):
- `__init__.py`: Module initialization
- `memory_manager.py`: `MemoryManager` class for storing and formatting conversation history

**`src/prompts/`** (NEW - moved from root):
- `__init__.py`: Module initialization
- `classification_prompt.py`: CoT-enhanced prompt for question classification
- `entity_extraction_prompt.py`: CoT-enhanced prompt for entity extraction
- `query_generation_prompt.py`: CoT-enhanced prompt for Cypher query generation
- `answer_formatting_general_knowledge_prompt.py`: CoT-enhanced prompt for general knowledge answers
- `answer_formatting_db_results_prompt.py`: CoT-enhanced prompt for database result formatting

### Modified Files

**`src/agents/workflow_agent.py`**:
- Added `conversation_memory` and `chain_of_thought` flags to `__init__`
- Integrated `MemoryManager` for conversation history tracking
- Updated all workflow methods to conditionally use CoT prompts
- Enhanced prompts to include conversation history when memory is enabled
- Improved parsing logic for CoT responses

**`src/agents/graph_interface.py`**:
- No modifications (used as-is for database interactions)

## License

MIT License

## Acknowledgments

This project is based on the Helix Navigator educational framework for learning LangGraph and knowledge graphs. The enhancements (evaluation metrics, conversation memory, and chain-of-thought reasoning) were added as part of a replication and extension project.

**Technologies Used:**
- LangGraph by LangChain
- Neo4j Graph Database
- Anthropic Claude
- Streamlit
