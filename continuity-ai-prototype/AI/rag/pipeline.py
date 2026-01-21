"""Retrieval-Augmented Generation pipeline."""
import logging
from typing import List, Dict, Any, Tuple
import asyncio

from database.vector_db import VectorDB
from models.llm_manager import LLMManager
from rag.prompt_builder import PromptBuilder
from config.settings import TOP_K_RESULTS

logger = logging.getLogger(__name__)


class RAGPipeline:
    """End-to-end RAG pipeline combining retrieval and generation."""

    def __init__(self, vector_db: VectorDB, llm_manager: LLMManager):
        """
        Initialize RAG pipeline.

        Args:
            vector_db: Vector database instance
            llm_manager: LLM manager instance
        """
        self.vector_db = vector_db
        self.llm_manager = llm_manager
        self.prompt_builder = PromptBuilder()
        logger.info("RAGPipeline initialized")

    async def query(
        self,
        user_query: str,
        chat_history: List[Dict[str, str]] = None,
        top_k: int = TOP_K_RESULTS,
        use_context: bool = True,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user query through the RAG pipeline.

        Args:
            user_query: The user's question
            chat_history: Previous conversation messages
            top_k: Number of context documents to retrieve
            use_context: Whether to use retrieved context

        Returns:
            Tuple of (generated_response, source_documents)
        """
        try:
            # Step 1: Retrieve relevant context
            if use_context:
                context_docs = self._retrieve_context(user_query, top_k)
                logger.info(f"Retrieved {len(context_docs)} context documents")
            else:
                context_docs = []

            # Step 2: Build prompt
            prompt = self.prompt_builder.build_rag_prompt(
                query=user_query,
                context_documents=context_docs,
                chat_history=chat_history,
            )
            logger.debug(f"Built prompt: {len(prompt)} chars")

            # Step 3: Generate response
            response = await self.llm_manager.generate(
                prompt=prompt,
                temperature=0.7,
                top_p=0.9,
                stream=False,
            )
            logger.info("Generated response successfully")

            return response, context_docs

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            raise

    async def query_stream(
        self,
        user_query: str,
        chat_history: List[Dict[str, str]] = None,
        top_k: int = TOP_K_RESULTS,
    ):
        """
        Stream response from RAG pipeline (generator).

        Args:
            user_query: The user's question
            chat_history: Previous conversation messages
            top_k: Number of context documents to retrieve

        Yields:
            Response tokens as they're generated
        """
        try:
            # Retrieve context
            context_docs = self._retrieve_context(user_query, top_k)

            # Build prompt
            prompt = self.prompt_builder.build_rag_prompt(
                query=user_query,
                context_documents=context_docs,
                chat_history=chat_history,
            )

            # Stream response
            async for token in self.llm_manager._generate_stream(
                prompt=prompt,
                temperature=0.7,
                top_p=0.9,
            ):
                yield token

        except Exception as e:
            logger.error(f"Error in stream query: {e}")
            raise

    def _retrieve_context(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS,
    ) -> List[Dict[str, Any]]:
        """Retrieve context documents for a query."""
        try:
            results = self.vector_db.search(query, top_k=top_k)
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def add_knowledge_base(
        self,
        documents: List[str],
        metadata: List[Dict[str, Any]] = None,
    ) -> None:
        """Add documents to the knowledge base."""
        try:
            self.vector_db.add_documents(documents, metadata)
            logger.info(f"Added {len(documents)} documents to knowledge base")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
