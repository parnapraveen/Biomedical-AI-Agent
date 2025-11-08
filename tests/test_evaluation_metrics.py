import unittest
from unittest.mock import MagicMock, patch
import json
from pathlib import Path
import os
import time

from src.agents.evaluation_metrics import WorkflowEvaluator
from src.agents.workflow_agent import WorkflowAgent
from src.agents.graph_interface import GraphInterface

class TestWorkflowEvaluator(unittest.TestCase):

    def setUp(self):
        self.dataset_path = Path("data/golden_dataset.json")
        self.mock_dataset_content = [
            {
                "question": "What genes are associated with Hypertension?",
                "expected_type": "gene_disease",
                "expected_entities": ["Hypertension"],
                "expected_query": "MATCH (g:Gene)-[:LINKED_TO]->(d:Disease {disease_name: 'Hypertension'}) RETURN g.gene_name",
                "expected_results": []
            },
            {
                "question": "Which drugs treat Hypertension?",
                "expected_type": "drug_treatment",
                "expected_entities": ["Hypertension"],
                "expected_query": "MATCH (dr:Drug)-[:TREATS]->(d:Disease {disease_name: 'Hypertension'}) RETURN dr.drug_name",
                "expected_results": ["Lisinopril", "Enalapril", "Captopril"]
            },
            {
                "question": "What is the category of Breast Cancer?",
                "expected_type": "general_knowledge",
                "expected_entities": ["Breast Cancer"],
                "expected_query": "MATCH (d:Disease {disease_name: 'Breast_Cancer'}) RETURN d.category",
                "expected_results": ["oncology"]
            }
        ]
        
        with open(self.dataset_path, "w") as f:
            json.dump(self.mock_dataset_content, f, indent=2)

    def tearDown(self):
        if self.dataset_path.exists():
            self.dataset_path.unlink()

    @patch('src.agents.workflow_agent.Anthropic')
    @patch('time.time')
    def test_evaluator_runs_and_calculates_metrics(self, mock_time, MockAnthropic):
        mock_anthropic_instance = MockAnthropic.return_value
        mock_anthropic_instance.messages.create.side_effect = [
            # Response for classify_question for "What genes are associated with Hypertension?"
            MagicMock(content=[MagicMock(text="gene_disease")]),
            # Response for extract_entities for "What genes are associated with Hypertension?"
            MagicMock(content=[MagicMock(text="Hypertension")]),
            # Response for generate_query (not used for metrics in this test)
            MagicMock(content=[MagicMock(text="some cypher query")]),
            # Response for format_answer for "What genes are associated with Hypertension?"
            MagicMock(content=[MagicMock(text=json.dumps([]))]),

            # Response for classify_question for "Which drugs treat Hypertension?"
            MagicMock(content=[MagicMock(text="drug_treatment")]),
            # Response for extract_entities for "Which drugs treat Hypertension?"
            MagicMock(content=[MagicMock(text="Hypertension")]),
            # Response for generate_query (not used for metrics in this test)
            MagicMock(content=[MagicMock(text="some cypher query")]),
            # Response for format_answer for "Which drugs treat Hypertension?"
            MagicMock(content=[MagicMock(text=json.dumps([{"dr.drug_name": "Lisinopril"}, {"dr.drug_name": "Enalapril"}, {"dr.drug_name": "Captopril"}]))]),

            # Response for classify_question for "What is the category of Breast Cancer?"
            MagicMock(content=[MagicMock(text="general_knowledge")]),
            # Response for extract_entities for "What is the category of Breast Cancer?"
            MagicMock(content=[MagicMock(text="Breast Cancer")]),
            # Response for generate_query (not used for metrics in this test)
            MagicMock(content=[MagicMock(text="some cypher query")]),
            # Response for format_answer for "What is the category of Breast Cancer?"
            MagicMock(content=[MagicMock(text=json.dumps([{"d.category": "oncology"}]))]),
        ]

        mock_graph_interface = MagicMock(spec=GraphInterface)
        mock_graph_interface.get_schem-info.return_value = {}
        mock_graph_interface.get_sample_property_values.return_value = {}
        mock_graph_interface.run_query.side_effect = [
            # For "What genes are associated with Hypertension?"
            MagicMock(data=[]),
            # For "Which drugs treat Hypertension?"
            MagicMock(data=[{"dr.drug_name": "Lisinopril"}, {"dr.drug_name": "Enalapril"}, {"dr.drug_name": "Captopril"}]),
            # For "What is the category of Breast Cancer?"
            MagicMock(data=[{"d.category": "oncology"}]),
        ]

        # Mock time to simulate query durations
        mock_time.side_effect = [1, 2, 3, 4, 5, 6] # 3 questions, each taking 1 second

        agent = WorkflowAgent(mock_graph_interface, "fake-api-key")
        evaluator = WorkflowEvaluator(agent, str(self.dataset_path))
        
        metrics = evaluator.evaluate()

        self.assertIn("classification_accuracy", metrics)
        self.assertIn("entity_accuracy", metrics)
        self.assertIn("answer_accuracy", metrics)
        self.assertIn("average_query_duration_seconds", metrics)

        self.assertEqual(metrics["classification_accuracy"], 1.0)
        self.assertEqual(metrics["entity_accuracy"], 1.0)
        self.assertEqual(metrics["answer_accuracy"], 1.0)
        self.assertEqual(metrics["average_query_duration_seconds"], 1.0) # (2-1) + (4-3) + (6-5) / 3 = 1.0

if __name__ == '__main__':
    unittest.main()
