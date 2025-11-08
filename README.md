# DSC180A_Replication_Project - Parna Praveen
## The feature that I added is at the end of this README file. My feature is for evaluation metrics.

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

#### Classification Accuracy - 

Measures how well the agent identifies the intent of the user's question (e.g., distinguishing between gene-disease queries vs. drug-treatment queries). High classification accuracy ensures the agent follows the correct workflow path from the start.

#### Entity Accuracy - 

Measures how accurately the agent extracts key biomedical terms (e.g., "Hypertension," "Lisinopril," "Breast Cancer") from questions. This is foundational—if entities aren't correctly identified, the agent cannot construct precise database queries.

#### Answer Accuracy - 

Measures how well the agent's final generated answer matches the expected factual outcome. This is the ultimate end-to-end performance measure, confirming whether the entire workflow (classification → extraction → query generation → execution → formatting) produces correct results.

#### Average Query Duration - 

Measures the time taken to execute each query, providing insight into system efficiency and user experience. This metric is critical for evaluating real-world performance and scalability.

### Together, these metrics provide granular insights into where the agent may be failing:

1. Low classification + high entity accuracy → LLM struggles with context selection but excels at term identification
2. High classification + entity accuracy but low answer accuracy → Issues in query generation or answer formatting


To evaluate the workflow agent:

```bash
pdm run python src/agents/evaluation_metrics.py
```

Expected output:

```
classification_accuracy: 0.64
entity_accuracy: 0.64
answer_accuracy: 0.36
average_query_duration_seconds: 38.34
```

## License

MIT License
