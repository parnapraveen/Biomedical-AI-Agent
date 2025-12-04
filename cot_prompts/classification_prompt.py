CLASSIFICATION_PROMPT = """Classify this biomedical question into one category.

{conversation_history}

Categories:
- gene_disease: Questions about genes and diseases
- drug_treatment: Questions about drugs treating diseases
- protein_function: Questions about protein functions
- general_db: Questions about database structure
- general_knowledge: General biomedical facts

Question: {question}

Think about the main focus of the question, then respond with ONLY the category name."""