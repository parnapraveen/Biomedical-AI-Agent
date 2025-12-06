"""Chain-of-thought reasoning prompts for the workflow agent."""

from .classification_prompt import CLASSIFICATION_PROMPT
from .entity_extraction_prompt import ENTITY_EXTRACTION_PROMPT
from .query_generation_prompt import QUERY_GENERATION_PROMPT
from .answer_formatting_general_knowledge_prompt import ANSWER_FORMATTING_GENERAL_KNOWLEDGE_PROMPT
from .answer_formatting_db_results_prompt import ANSWER_FORMATTING_DB_RESULTS_PROMPT

__all__ = [
    "CLASSIFICATION_PROMPT",
    "ENTITY_EXTRACTION_PROMPT",
    "QUERY_GENERATION_PROMPT",
    "ANSWER_FORMATTING_GENERAL_KNOWLEDGE_PROMPT",
    "ANSWER_FORMATTING_DB_RESULTS_PROMPT",
]

