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
    
    def _normalize_string(self, s: str) -> str:
        """Normalize string for comparison."""
        return str(s).lower().strip().replace('_', ' ').replace('-', ' ')
    
    def _extract_values_from_results(self, results: List[Dict]) -> set:
        """Extract all values from database results."""
        values = set()
        for item in results:
            if isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, (str, int, float)):
                        values.add(self._normalize_string(value))
                    elif isinstance(value, list):
                        for v in value:
                            values.add(self._normalize_string(v))
            elif isinstance(item, (str, int, float)):
                values.add(self._normalize_string(item))
        return values
    
    def evaluate(self) -> Dict[str, float]:
        """Evaluate agent performance on benchmark questions."""
        classification_correct = 0
        entity_correct = 0
        answer_correct = 0
        total_questions = len(self.dataset)
        query_durations = []
        
        # Group by conversation
        grouped_dataset = {}
        for example in self.dataset:
            conv_id = example.get("conversation_id", f"single_{len(grouped_dataset)}")
            if conv_id not in grouped_dataset:
                grouped_dataset[conv_id] = []
            grouped_dataset[conv_id].append(example)
        
        # Iterate through conversations
        for conv_id, conversation_examples in tqdm(grouped_dataset.items(), desc="Evaluating workflow"):
            # Clear memory for each new conversation
            if self.agent.conversation_memory_enabled and hasattr(self.agent, 'memory_manager'):
                self.agent.memory_manager.clear_history()
            
            for example in conversation_examples:
                # Run workflow and measure duration
                start_time = time.time()
                output = self.agent.answer_question(example["question"])
                end_time = time.time()
                query_durations.append(end_time - start_time)
                
                # Check classification
                if output["question_type"] == example.get("expected_type"):
                    classification_correct += 1
                
                # Check entities (normalized comparison)
                output_entities = {self._normalize_string(e) for e in output.get("entities", [])}
                expected_entities = {self._normalize_string(e) for e in example.get("expected_entities", [])}
                
                if output_entities == expected_entities:
                    entity_correct += 1
                
                # Check answer accuracy
                output_values = self._extract_values_from_results(output.get("raw_results", []))
                expected_values = {self._normalize_string(v) for v in example.get("expected_results", [])}
                
                # Handle empty expected results (general knowledge questions)
                if not expected_values and not output_values:
                    answer_correct += 1
                elif output_values == expected_values:
                    answer_correct += 1
        
        avg_query_duration = sum(query_durations) / total_questions if total_questions > 0 else 0
        
        return {
            "classification_accuracy": classification_correct / total_questions,
            "entity_accuracy": entity_correct / total_questions,
            "answer_accuracy": answer_correct / total_questions,
            "average_query_duration_seconds": avg_query_duration
        }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not password:
        raise ValueError("NEO4J_PASSWORD environment variable not set")
    
    graph_interface = GraphInterface(uri, user, password)
    
    # Scenario 1: Baseline (No Enhancements)
    print("\n" + "="*60)
    print("Scenario 1: Baseline (No Enhancements)")
    print("="*60)
    agent_baseline = WorkflowAgent(
        graph_interface, 
        os.getenv("ANTHROPIC_API_KEY"),
        conversation_memory=False,
        chain_of_thought=False
    )
    evaluator_baseline = WorkflowEvaluator(agent_baseline, "evaluation_metrics/golden_dataset.json")
    metrics_baseline = evaluator_baseline.evaluate()
    
    print("\nResults:")
    for metric, value in metrics_baseline.items():
        print(f"  {metric}: {value:.2f}")
    
    # Scenario 2: Conversation Memory Only
    print("\n" + "="*60)
    print("Scenario 2: Conversation Memory ON")
    print("="*60)
    agent_memory = WorkflowAgent(
        graph_interface,
        os.getenv("ANTHROPIC_API_KEY"),
        conversation_memory=True,
        chain_of_thought=False
    )
    evaluator_memory = WorkflowEvaluator(agent_memory, "evaluation_metrics/golden_dataset.json")
    metrics_memory = evaluator_memory.evaluate()
    
    print("\nResults:")
    for metric, value in metrics_memory.items():
        print(f"  {metric}: {value:.2f}")
    print(f"\nImprovement over baseline:")
    for metric in metrics_baseline.keys():
        diff = metrics_memory[metric] - metrics_baseline[metric]
        print(f"  {metric}: {diff:+.2f}")
    
    # Scenario 3: Chain-of-Thought Only
    print("\n" + "="*60)
    print("Scenario 3: Chain-of-Thought ON")
    print("="*60)
    agent_cot = WorkflowAgent(
        graph_interface,
        os.getenv("ANTHROPIC_API_KEY"),
        conversation_memory=False,
        chain_of_thought=True
    )
    evaluator_cot = WorkflowEvaluator(agent_cot, "evaluation_metrics/golden_dataset.json")
    metrics_cot = evaluator_cot.evaluate()
    
    print("\nResults:")
    for metric, value in metrics_cot.items():
        print(f"  {metric}: {value:.2f}")
    print(f"\nImprovement over baseline:")
    for metric in metrics_baseline.keys():
        diff = metrics_cot[metric] - metrics_baseline[metric]
        print(f"  {metric}: {diff:+.2f}")
    
    # Scenario 4: Both Enhancements
    print("\n" + "="*60)
    print("Scenario 4: Memory + Chain-of-Thought")
    print("="*60)
    agent_both = WorkflowAgent(
        graph_interface,
        os.getenv("ANTHROPIC_API_KEY"),
        conversation_memory=True,
        chain_of_thought=True
    )
    evaluator_both = WorkflowEvaluator(agent_both, "evaluation_metrics/golden_dataset.json")
    metrics_both = evaluator_both.evaluate()
    
    print("\nResults:")
    for metric, value in metrics_both.items():
        print(f"  {metric}: {value:.2f}")
    print(f"\nImprovement over baseline:")
    for metric in metrics_baseline.keys():
        diff = metrics_both[metric] - metrics_baseline[metric]
        print(f"  {metric}: {diff:+.2f}")
    
    # Save results
    print("\n" + "="*60)
    print("Saving results to evaluation_results.txt")
    print("="*60)
    
    with open("evaluation_results.txt", "w") as f:
        f.write("="*60 + "\n")
        f.write("EVALUATION RESULTS\n")
        f.write("="*60 + "\n\n")
        
        f.write("Scenario 1: Baseline (No Enhancements)\n")
        f.write("-"*60 + "\n")
        for metric, value in metrics_baseline.items():
            f.write(f"{metric}: {value:.2f}\n")
        
        f.write("\nScenario 2: Conversation Memory ON\n")
        f.write("-"*60 + "\n")
        for metric, value in metrics_memory.items():
            f.write(f"{metric}: {value:.2f}\n")
        f.write("Improvement over baseline:\n")
        for metric in metrics_baseline.keys():
            diff = metrics_memory[metric] - metrics_baseline[metric]
            f.write(f"  {metric}: {diff:+.2f}\n")
        
        f.write("\nScenario 3: Chain-of-Thought ON\n")
        f.write("-"*60 + "\n")
        for metric, value in metrics_cot.items():
            f.write(f"{metric}: {value:.2f}\n")
        f.write("Improvement over baseline:\n")
        for metric in metrics_baseline.keys():
            diff = metrics_cot[metric] - metrics_baseline[metric]
            f.write(f"  {metric}: {diff:+.2f}\n")
        
        f.write("\nScenario 4: Memory + Chain-of-Thought\n")
        f.write("-"*60 + "\n")
        for metric, value in metrics_both.items():
            f.write(f"{metric}: {value:.2f}\n")
        f.write("Improvement over baseline:\n")
        for metric in metrics_baseline.keys():
            diff = metrics_both[metric] - metrics_baseline[metric]
            f.write(f"  {metric}: {diff:+.2f}\n")
    
    graph_interface.close()
    print("\nEvaluation complete!")