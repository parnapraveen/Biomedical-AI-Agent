"""
LangGraph workflow agent for biomedical knowledge graphs with enhancements.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, TypedDict

from anthropic import Anthropic
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from .graph_interface import GraphInterface
from ..memory import MemoryManager
from ..prompts import CLASSIFICATION_PROMPT, ENTITY_EXTRACTION_PROMPT


class WorkflowState(TypedDict):
    """State that flows through the workflow steps."""
    user_question: str
    question_type: Optional[str]
    entities: Optional[List[str]]
    cypher_query: Optional[str]
    results: Optional[List[Dict]]
    final_answer: Optional[str]
    error: Optional[str]


class WorkflowAgent:
    """LangGraph workflow agent for biomedical knowledge graphs."""

    MODEL_NAME = "claude-sonnet-4-20250514"
    DEFAULT_MAX_TOKENS = 200
    SCHEMA_QUERY = (
        "MATCH (n) RETURN labels(n) as node_type, count(n) as count "
        "ORDER BY count DESC LIMIT 10"
    )

    def __init__(self, graph_interface: GraphInterface, anthropic_api_key: str, 
                 conversation_memory: bool = False, chain_of_thought: bool = False):
        self.graph_db = graph_interface
        self.anthropic = Anthropic(api_key=anthropic_api_key)
        self.schema = self.graph_db.get_schema_info()
        self.property_values = self._get_key_property_values()
        self.workflow = self._create_workflow()
        
        # Enhancement flags
        self.conversation_memory_enabled = conversation_memory
        self.chain_of_thought = chain_of_thought
        
        if self.conversation_memory_enabled:
            self.memory_manager = MemoryManager()

    def _get_key_property_values(self) -> Dict[str, List[Any]]:
        """Get property values dynamically from all nodes and relationships."""
        values = {}
        try:
            for node_label in self.schema.get("node_labels", []):
                node_props = self.schema.get("node_properties", {}).get(node_label, [])
                for prop_name in node_props:
                    if prop_name not in values:
                        prop_values = self.graph_db.get_property_values(node_label, prop_name)
                        if prop_values:
                            values[prop_name] = prop_values

            for rel_type in self.schema.get("relationship_types", []):
                rel_label = f"REL_{rel_type}"
                rel_props = self.schema.get("relationship_properties", {}).get(rel_type, [])
                for prop_name in rel_props:
                    if prop_name not in values:
                        try:
                            prop_values = self.graph_db.get_property_values(rel_label, prop_name)
                            if prop_values:
                                values[prop_name] = prop_values
                        except Exception:
                            continue
        except Exception:
            pass
        return values

    def _get_llm_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Get response from LLM and handle content extraction."""
        if max_tokens is None:
            max_tokens = self.DEFAULT_MAX_TOKENS

        try:
            response = self.anthropic.messages.create(
                model=self.MODEL_NAME,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Deterministic for evaluation
            )
            content = response.content[0]
            return content.text.strip() if hasattr(content, "text") else str(content)
        except Exception as e:
            raise RuntimeError(f"LLM response failed: {str(e)}")

    def _create_workflow(self) -> Any:
        """Create the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)
        workflow.add_node("classify", self.classify_question)
        workflow.add_node("extract", self.extract_entities)
        workflow.add_node("generate", self.generate_query)
        workflow.add_node("execute", self.execute_query)
        workflow.add_node("format", self.format_answer)
        workflow.add_edge("classify", "extract")
        workflow.add_edge("extract", "generate")
        workflow.add_edge("generate", "execute")
        workflow.add_edge("execute", "format")
        workflow.add_edge("format", END)
        workflow.set_entry_point("classify")
        return workflow.compile()

    def _build_classification_prompt(self, question: str) -> str:
        """Build classification prompt."""
        conversation_history = ""
        if self.conversation_memory_enabled and hasattr(self, 'memory_manager'):
            history = self.memory_manager.get_history()
            if history:
                conversation_history = "Previous conversation:\n" + self.memory_manager.format_history_for_prompt() + "\n\n"
        
        if self.chain_of_thought:
            return CLASSIFICATION_PROMPT.format(
                question=question,
                conversation_history=conversation_history
            )
        else:
            return f"""{conversation_history}Classify this biomedical question. Choose one:
- gene_disease: genes and diseases
- drug_treatment: drugs and treatments  
- protein_function: proteins and functions
- general_db: database exploration
- general_knowledge: biomedical concepts

Question: {question}

Respond with just the type."""

    def classify_question(self, state: WorkflowState) -> WorkflowState:
        """Classify the biomedical question type."""
        try:
            prompt = self._build_classification_prompt(state["user_question"])
            response = self._get_llm_response(prompt, max_tokens=50)
            
            # Clean response
            response = response.strip().lower().rstrip(".,;:!?")
            
            # Validate
            valid_types = ["gene_disease", "drug_treatment", "protein_function", "general_db", "general_knowledge"]
            if response in valid_types:
                state["question_type"] = response
            else:
                # Try to find valid type in response
                for vtype in valid_types:
                    if vtype in response:
                        state["question_type"] = vtype
                        break
                else:
                    state["question_type"] = "general_knowledge"
                    
        except Exception as e:
            state["error"] = f"Classification failed: {str(e)}"
            state["question_type"] = "general_knowledge"
        return state

    def extract_entities(self, state: WorkflowState) -> WorkflowState:
        """Extract biomedical entities from the question."""
        question_type = state.get("question_type")
        if question_type in ["general_db", "general_knowledge"]:
            state["entities"] = []
            return state

        property_info = []
        for prop_name, values in self.property_values.items():
            if values:
                sample_values = ", ".join(str(v) for v in values[:3])
                property_info.append(f"- {prop_name}: {sample_values}")

        entity_types_str = ", ".join(self.schema.get("node_labels", []))
        
        conversation_history = ""
        if self.conversation_memory_enabled and hasattr(self, 'memory_manager'):
            history = self.memory_manager.get_history()
            if history:
                conversation_history = "Previous conversation:\n" + self.memory_manager.format_history_for_prompt() + "\n\n"

        if self.chain_of_thought:
            prompt = ENTITY_EXTRACTION_PROMPT.format(
                question=state["user_question"],
                entity_types_str=entity_types_str,
                property_info='\n'.join(property_info),
                conversation_history=conversation_history
            )
        else:
            prompt = f"""{conversation_history}Extract specific biomedical entities from this question.

Available entity types: {entity_types_str}
Available property values:
{chr(10).join(property_info) if property_info else "- No property values available"}

Question: {state['user_question']}

Extract specific names and property values. Return JSON list: ["term1", "term2"] or []"""

        try:
            response = self._get_llm_response(prompt, max_tokens=100)
            
            # Extract JSON from response
            response = response.strip()
            response = response.replace('```json', '').replace('```', '').strip()
            
            # Find JSON array
            match = re.search(r'\[.*?\]', response, re.DOTALL)
            if match:
                json_str = match.group(0)
                state["entities"] = json.loads(json_str)
            else:
                state["entities"] = []
                
        except (json.JSONDecodeError, AttributeError):
            state["entities"] = []

        return state

    def generate_query(self, state: WorkflowState) -> WorkflowState:
        """Generate Cypher query based on question type."""
        question_type = state.get("question_type", "general")

        if question_type == "general_db":
            state["cypher_query"] = self.SCHEMA_QUERY
            return state

        if question_type == "general_knowledge":
            state["cypher_query"] = None
            return state

        relationship_guide = f"""
Available relationships:
{' | '.join([f'- {rel}' for rel in self.schema['relationship_types']])}"""

        property_details = []
        for prop_name, values in self.property_values.items():
            if values:
                value_type = "text values" if isinstance(values[0], str) else "numeric values"
                property_details.append(f"- {prop_name}: {values} ({value_type})")

        property_info = f"""Property names and values:
Node properties: {self.schema['node_properties']}
Available property values:
{chr(10).join(property_details) if property_details else "- No values available"}
Use WHERE property IN [value1, value2] for filtering."""

        prompt = f"""Create a Cypher query for this biomedical question:

Question: {state['user_question']}
Type: {question_type}
Schema:
Nodes: {', '.join(self.schema['node_labels'])}
Relations: {', '.join(self.schema['relationship_types'])}
{property_info}
{relationship_guide}
Entities: {state.get('entities', [])}

Use MATCH, WHERE with CONTAINS for filtering, RETURN, LIMIT 10.
IMPORTANT: Use property names from schema above and IN filtering for property values.
Return only the Cypher query."""

        cypher_query = self._get_llm_response(prompt, max_tokens=150)

        if cypher_query.startswith("```"):
            cypher_query = "\n".join(
                line for line in cypher_query.split("\n")
                if not line.startswith("```") and not line.startswith("cypher")
            ).strip()

        state["cypher_query"] = cypher_query
        return state

    def execute_query(self, state: WorkflowState) -> WorkflowState:
        """Execute the generated Cypher query."""
        try:
            query = state.get("cypher_query")
            state["results"] = self.graph_db.execute_query(query) if query else []
        except Exception as e:
            state["error"] = f"Query failed: {str(e)}"
            state["results"] = []
        return state

    def format_answer(self, state: WorkflowState) -> WorkflowState:
        """Format database results into human-readable answer."""
        if state.get("error"):
            state["final_answer"] = f"Sorry, I had trouble with that question: {state['error']}"
            return state

        question_type = state.get("question_type")

        if question_type == "general_knowledge":
            state["final_answer"] = self._get_llm_response(
                f"""Answer this general biomedical question using your knowledge:

Question: {state['user_question']}

Provide a clear, informative answer about biomedical concepts.""",
                max_tokens=300,
            )
            return state

        results = state.get("results", [])
        if not results:
            state["final_answer"] = (
                "I didn't find any information for that question. Try asking about "
                "genes, diseases, or drugs in our database."
            )
            return state

        state["final_answer"] = self._get_llm_response(
            f"""Convert these database results into a clear answer:

Question: {state['user_question']}
Results: {json.dumps(results[:5], indent=2)}
Total found: {len(results)}

Make it concise and informative.""",
            max_tokens=250,
        )
        return state

    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a biomedical question using the LangGraph workflow."""
        initial_state = WorkflowState(
            user_question=question,
            question_type=None,
            entities=None,
            cypher_query=None,
            results=None,
            final_answer=None,
            error=None,
        )

        final_state = self.workflow.invoke(initial_state)
        
        final_answer = final_state.get("final_answer", "No answer generated")
        
        # Add to conversation memory if enabled
        if self.conversation_memory_enabled and hasattr(self, 'memory_manager'):
            self.memory_manager.add_turn(question, final_answer)

        return {
            "answer": final_answer,
            "question_type": final_state.get("question_type"),
            "entities": final_state.get("entities", []),
            "cypher_query": final_state.get("cypher_query"),
            "results_count": len(final_state.get("results", [])),
            "raw_results": final_state.get("results", [])[:3],
            "error": final_state.get("error"),
        }


def create_workflow_graph() -> Any:
    """Factory function for LangGraph Studio."""
    load_dotenv()

    graph_interface = GraphInterface(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", ""),
    )

    agent = WorkflowAgent(
        graph_interface=graph_interface,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        conversation_memory=os.getenv("CONVERSATION_MEMORY", "false").lower() == "true",
        chain_of_thought=os.getenv("CHAIN_OF_THOUGHT", "false").lower() == "true",
    )

    return agent.workflow