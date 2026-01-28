"""Prompt building for RAG pipeline."""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for the LLM with context and history."""

    @staticmethod
    def build_rag_prompt(
        query: str,
        context_documents: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]] = None,
    ) -> str:
        """
        Build a prompt for RAG with context and history.

        Args:
            query: User query
            context_documents: List of retrieved context docs
            chat_history: Previous messages in conversation

        Returns:
            Formatted prompt string
        """
        prompt = "You are Nessie, a friendly NSCC assistant. Answer questions directly and concisely using the provided context. Do not explain your reasoning process - just give the answer in a natural, conversational way.\n\n"

        # Add context
        if context_documents:
            prompt += "## Context Information:\n"
            for i, doc in enumerate(context_documents, 1):
                text = doc.get("text", "")
                score = doc.get("distance", 1.0)
                prompt += f"\n[Document {i} - Relevance: {1-score:.2f}]\n{text}\n"
            prompt += "\n---\n\n"

        # Add chat history
        if chat_history:
            prompt += "## Conversation History:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                role = msg.get("role", "User").capitalize()
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
            prompt += "\n---\n\n"

        # Add current query
        prompt += f"## Current Question:\nUser: {query}\n\nAssistant: "

        return prompt

    @staticmethod
    def build_simple_prompt(query: str) -> str:
        """Build a simple prompt without context."""
        return f"User: {query}\n\nAssistant: "

    @staticmethod
    def build_classification_prompt(
        query: str,
        categories: List[str],
    ) -> str:
        """Build a prompt for classifying queries."""
        categories_str = "\n".join([f"- {cat}" for cat in categories])
        return f"""Classify the following query into one of these categories:
{categories_str}

Query: {query}

Category: """
