from typing import Dict, List, Any
from src.agents.workflow_agent import WorkflowAgent
from src.agents.graph_interface import GraphInterface
import json
import os
import time
from tqdm import tqdm

class WorkflowEvaluator:
    """Evaluate Helix Navigator agent performance on benchmark questions."""
    def __init__(self, agent: WorkflowAgent, dataset_path: str):
        self.agent = agent
        with open(dataset_path, "r") as f:
            self.dataset = json.load(f)
    
    def evaluate(self) -> Dict[str, float]:
        classification_correct, entity_correct, answer_correct = 0, 0, 0
        total = len(self.dataset)
        query_durations = []

        for example in tqdm(self.dataset, desc="Evaluating workflow"):
            state = {
                "user_question": example["question"],
                "question_type": None,
                "entities": None,
                "cypher_query": None,
                "results": None,
                "final_answer": None
            }

            # Run full workflow and measure duration
            start_time = time.time()
            output = self.agent.workflow.invoke(state)
            end_time = time.time()
            query_durations.append(end_time - start_time)

            if output["question_type"] == example.get("expected_type"):
                classification_correct += 1
            if set(output.get("entities", [])) == set(example.get("expected_entities", [])):
                entity_correct += 1
            
            # For answer_correct, we need to compare the content of the results
            # The `output["results"]` will contain dictionaries like 
            # `{'g.gene_name': 'GENE_NAME'}` or `{'dr.drug_name': 'DRUG_NAME'}`
            # We need to extract just the values from these dictionaries for comparison.
            output_results_values = []
            if output.get("results"):
                for item in output["results"]:
                    if isinstance(item, dict):
                        for value in item.values():
                            if isinstance(value, list):
                                output_results_values.extend(value)
                            elif isinstance(value, dict):
                                # If a value is another dictionary, extract its values and flatten
                                for nested_val in value.values():
                                    if isinstance(nested_val, list):
                                        output_results_values.extend(nested_val)
                                    else:
                                        output_results_values.append(nested_val)
                            else:
                                output_results_values.append(value)
                    elif isinstance(item, list):
                        output_results_values.extend(item)
                    else:
                        output_results_values.append(item)

            if set(output_results_values) == set(example.get("expected_results", [])):
                answer_correct += 1

        avg_query_duration = sum(query_durations) / total if total > 0 else 0

        return {
            "classification_accuracy": classification_correct / total,
            "entity_accuracy": entity_correct / total,
            "answer_accuracy": answer_correct / total,
            "average_query_duration_seconds": avg_query_duration
        }


if __name__ == "__main__":
    # Load environment variables (assuming they are in .env in the project root)
    from dotenv import load_dotenv
    load_dotenv()

    # Get database credentials from environment
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    if not password:
        raise ValueError("NEO4J_PASSWORD environment variable not set")

    # Initialize GraphInterface and WorkflowAgent
    graph_interface = GraphInterface(uri, user, password)
    workflow_agent = WorkflowAgent(graph_interface, os.getenv("ANTHROPIC_API_KEY"))

    # Initialize and run evaluator
    evaluator = WorkflowEvaluator(workflow_agent, "data/golden_dataset.json")
    metrics = evaluator.evaluate()

    for metric, value in metrics.items():
        print(f"{metric}: {value:.2f}")

    # Close graph interface
    graph_interface.close()
