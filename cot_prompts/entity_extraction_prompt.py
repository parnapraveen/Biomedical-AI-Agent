ENTITY_EXTRACTION_PROMPT = """Extract specific biomedical entities from this question.

{conversation_history}

ONLY extract:
- Specific disease names (e.g., "Hypertension", "Breast Cancer")
- Specific drug names (e.g., "Lisinopril")
- Specific gene names (e.g., "TP53")
- Property values (e.g., "approved", "common", "severe", "small molecule")

DO NOT extract:
- Generic types ("drugs", "genes", "diseases")
- Actions ("treat", "associated with")
- Question words ("what", "which")

Database context:
Nodes: {entity_types_str}
{property_info}

Question: {question}

Return ONLY a JSON list like: ["entity1", "entity2"] or []"""