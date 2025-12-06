QUERY_GENERATION_PROMPT = """You are an expert in Cypher query language and biomedical knowledge graphs.

{conversation_history}

Your task: Generate an accurate Cypher query based on the user's question.

Question: {question}
Type: {question_type}
Extracted Entities: {entities}

Database Schema:
Nodes: {node_labels}
Relationships: {relationship_types}
{property_info}
{relationship_guide}

Here's your thought process:
1. Understand what the user is asking for
2. Identify which nodes and relationships are needed
3. Determine how to filter using the extracted entities
4. Construct the MATCH pattern
5. Add WHERE clauses for filtering
6. Define what to RETURN
7. Add LIMIT 10

Guidelines:
- Use exact label names from the schema
- For filtering, use: WHERE property IN [value1, value2] or WHERE property = 'value'
- Do NOT use elementId() or other internal functions
- Always add LIMIT 10

Example:
Question: "Which drugs treat Hypertension?"
Thought: Need Drug nodes that TREAT Disease nodes. Filter Disease by name = "Hypertension".
Query: MATCH (dr:Drug)-[:TREATS]->(d:Disease {{disease_name: 'Hypertension'}}) RETURN dr.drug_name LIMIT 10

Now generate the query. Think step-by-step, then provide ONLY the Cypher query on the last line starting with "Query:"
"""