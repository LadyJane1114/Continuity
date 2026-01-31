"""Embedder for converting text to vectors."""
import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class Embedder:
    """Handles text embedding using SentenceTransformers."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize embedder with specified model."""
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded successfully")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Convert single text to embedding vector.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1D numpy array)
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Convert multiple texts to embeddings.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error batch embedding: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.model.get_sentence_embedding_dimension()
