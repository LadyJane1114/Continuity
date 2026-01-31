"""Segment Manager for data ingestion pipeline."""
import logging
from typing import Optional, Dict, Any
from database.vector_db import VectorDB
from database.entity_store import EntityStore
from models.entity_extractor import EntityExtractor
from utils.text_chunker import TextChunker
from config.settings import (
    MAX_SEGMENT_LENGTH,
    ENABLE_AUTO_CHUNKING,
    SIMILARITY_THRESHOLD,
    SEGMENT_COLLECTION_NAME,
)

logger = logging.getLogger(__name__)


class SegmentManager:
    """Manages the complete ingestion workflow for story segments."""

    def __init__(
        self,
        vector_db: VectorDB,
        entity_extractor: EntityExtractor,
        entity_store: EntityStore,
    ):
        """Initialize the segment manager."""
        self.vector_db = vector_db
        self.entity_extractor = entity_extractor
        self.entity_store = entity_store
        self.text_chunker = TextChunker()

    async def ingest_segment(
        self,
        text: str,
        user_id: str,
        time_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Ingest a story segment through the complete pipeline."""
        try:
            # Validate input
            if not text or len(text.strip()) == 0:
                return {
                    "status": "error",
                    "message": "Text cannot be empty",
                    "segment_id": None,
                }

            if len(text) > MAX_SEGMENT_LENGTH:
                return {
                    "status": "error",
                    "message": f"Text exceeds maximum length of {MAX_SEGMENT_LENGTH}",
                    "segment_id": None,
                }

            # Check for duplicates
            is_duplicate, dup_info = await self._check_duplicate(text, user_id)
            if is_duplicate:
                return {
                    "status": "duplicate",
                    "message": f"Similar content already exists (similarity: {dup_info['similarity']:.2%})",
                    "duplicate_info": dup_info,
                    "segment_id": None,
                }

            # Extract entities
            entities = []
            try:
                logger.info("Extracting entities from segment...")
                entities = await self.entity_extractor.extract_entities(
                    text=text, time_id=time_id or "t_default"
                )
                logger.info(f"Extracted {len(entities)} entities")
            except Exception as e:
                logger.warning(f"Entity extraction failed (non-blocking): {e}")

            # Store entities
            entity_ids = []
            if entities:
                try:
                    entity_ids = self.entity_store.add_entities(entities)
                    logger.info(f"Stored {len(entities)} entities")
                except Exception as e:
                    logger.warning(f"Entity storage failed (non-blocking): {e}")

            # Chunk the text
            chunks = self.text_chunker.chunk_text(
                text=text,
                segment_id=f"{user_id}_{time_id or 'default'}",
                metadata={
                    "user_id": user_id,
                    "time_id": time_id or "default",
                    **(metadata or {}),
                },
            )

            # Store chunks in vector database
            segment_id = self.vector_db.add_documents(
                documents=[chunk["text"] for chunk in chunks],
                ids=[chunk["id"] for chunk in chunks],
                metadata=[chunk["metadata"] for chunk in chunks],
            )

            logger.info(
                f"Successfully ingested segment {segment_id} with {len(chunks)} chunks"
            )

            return {
                "status": "success",
                "message": f"Segment ingested successfully",
                "segment_id": segment_id,
                "chunks_created": len(chunks),
                "entities_extracted": len(entities),
                "entity_ids": entity_ids,
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "segment_id": None,
            }

    async def _check_duplicate(
        self, text: str, user_id: str
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if similar content already exists."""
        try:
            # Get embedding for the text
            embedding = self.vector_db.embedder.encode(text)

            # Query for similar documents
            results = self.vector_db.query_documents(
                query_embedding=embedding,
                n_results=1,
                where={"user_id": user_id},
            )

            if results and len(results["distances"]) > 0:
                similarity = 1 - results["distances"][0][0]
                if similarity >= SIMILARITY_THRESHOLD:
                    return True, {
                        "similarity": similarity,
                        "existing_id": results["ids"][0][0]
                        if results["ids"]
                        else None,
                    }

            return False, {}

        except Exception as e:
            logger.warning(f"Duplicate check failed (non-blocking): {e}")
            return False, {}

    async def get_user_timeline(
        self, user_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Get user's story timeline."""
        try:
            # Query documents for this user
            results = self.vector_db.query_documents(
                query_embedding=self.vector_db.embedder.encode(""),
                where={"user_id": user_id},
                n_results=limit,
            )

            segments = []
            if results and results.get("metadatas"):
                for metadata in results["metadatas"][0]:
                    segments.append(metadata)

            return {
                "user_id": user_id,
                "count": len(segments),
                "timeline": segments,
            }

        except Exception as e:
            logger.error(f"Failed to get timeline: {e}")
            return {"user_id": user_id, "count": 0, "timeline": []}

    async def delete_segment(self, segment_id: str) -> Dict[str, Any]:
        """Delete a segment and its chunks."""
        try:
            self.vector_db.delete_documents(segment_id)
            return {"status": "success", "message": f"Segment {segment_id} deleted"}
        except Exception as e:
            logger.error(f"Failed to delete segment: {e}")
            return {"status": "error", "message": str(e)}

    async def batch_ingest(
        self, segments: list[Dict[str, Any]], user_id: str
    ) -> Dict[str, Any]:
        """Ingest multiple segments."""
        results = {
            "total": len(segments),
            "successful": 0,
            "failed": 0,
            "duplicates": 0,
            "details": [],
        }

        for segment in segments:
            result = await self.ingest_segment(
                text=segment.get("text", ""),
                user_id=user_id,
                time_id=segment.get("time_id"),
                metadata=segment.get("metadata"),
            )

            results["details"].append(result)

            if result["status"] == "success":
                results["successful"] += 1
            elif result["status"] == "duplicate":
                results["duplicates"] += 1
            else:
                results["failed"] += 1

        return results
