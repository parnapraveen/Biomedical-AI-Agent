from typing import List, Dict, Any

class MemoryManager:
    """Manages conversation history for an agent."""

    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_turn(self, user_question: str, agent_answer: str):
        """Adds a new user question and agent answer to the history."""
        self.history.append({"user_question": user_question, "agent_answer": agent_answer})

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the entire conversation history."""
        return self.history

    def clear_history(self):
        """Clears the entire conversation history."""
        self.history = []

    def format_history_for_prompt(self) -> str:
        """Formats the conversation history into a string suitable for LLM prompts."""
        formatted_history = []
        for i, turn in enumerate(self.history):
            formatted_history.append(f"User {i+1}: {turn["user_question"]}")
            formatted_history.append(f"Agent {i+1}: {turn["agent_answer"]}")
        return "\n".join(formatted_history)
