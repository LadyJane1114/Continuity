"""Text chunking utility for intelligent document splitting."""
import logging
from typing import List, Dict, Any
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class TextChunker:
    """Intelligently chunks text with overlap while preserving context."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """Initialize the text chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        segment_id: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks with metadata.
        
        Args:
            text: Text to chunk
            segment_id: ID of the segment
            metadata: Additional metadata for chunks
        
        Returns:
            List of chunk dictionaries with id, text, and metadata
        """
        if not text:
            return []

        chunks = []
        sentences = self._split_into_sentences(text)

        if not sentences:
            # Fallback to simple chunking if no sentences found
            return self._simple_chunk(text, segment_id, metadata)

        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            # Try adding the next sentence
            test_chunk = current_chunk + sentence

            if len(test_chunk) <= self.chunk_size:
                # Fits in current chunk
                current_chunk = test_chunk
            else:
                # Start new chunk
                if current_chunk:
                    chunk_dict = {
                        "id": f"{segment_id}_chunk_{chunk_index}",
                        "text": current_chunk.strip(),
                        "metadata": {
                            **(metadata or {}),
                            "chunk_index": chunk_index,
                            "segment_id": segment_id,
                        },
                    }
                    chunks.append(chunk_dict)
                    chunk_index += 1

                    # Add overlap
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = overlap_text + sentence
                else:
                    current_chunk = sentence

        # Add final chunk
        if current_chunk.strip():
            chunk_dict = {
                "id": f"{segment_id}_chunk_{chunk_index}",
                "text": current_chunk.strip(),
                "metadata": {
                    **(metadata or {}),
                    "chunk_index": chunk_index,
                    "segment_id": segment_id,
                },
            }
            chunks.append(chunk_dict)

        logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences intelligently."""
        # Simple sentence splitting on punctuation
        sentences = []
        current = ""

        for char in text:
            current += char
            if char in ".!?":
                if current.strip():
                    sentences.append(current.strip() + " ")
                current = ""

        if current.strip():
            sentences.append(current.strip())

        return sentences

    def _get_overlap(self, text: str) -> str:
        """Get the last chunk_overlap characters for next chunk."""
        if len(text) <= self.chunk_overlap:
            return text.strip()
        return text[-self.chunk_overlap:].strip()

    def _simple_chunk(
        self,
        text: str,
        segment_id: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Simple character-based chunking as fallback."""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i : i + self.chunk_size]
            if chunk_text.strip():
                chunk_dict = {
                    "id": f"{segment_id}_chunk_{len(chunks)}",
                    "text": chunk_text.strip(),
                    "metadata": {
                        **(metadata or {}),
                        "chunk_index": len(chunks),
                        "segment_id": segment_id,
                    },
                }
                chunks.append(chunk_dict)

        return chunks

    def reconstruct_text(self, chunks: List[Dict[str, Any]]) -> str:
        """Reconstruct original text from chunks, handling overlaps."""
        if not chunks:
            return ""

        # Sort chunks by index
        sorted_chunks = sorted(chunks, key=lambda x: x["metadata"].get("chunk_index", 0))

        reconstructed = ""
        for chunk in sorted_chunks:
            text = chunk["text"]

            if reconstructed:
                # Remove overlap from beginning of this chunk
                for i in range(len(text)):
                    if reconstructed.endswith(text[:i]):
                        text = text[i:]
                        break

            reconstructed += text

        return reconstructed
