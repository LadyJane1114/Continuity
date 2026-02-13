"""FastAPI web interface for entity extraction."""
import logging
from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import StreamingResponse # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List, Dict, Any
import json

from database.entity_store import EntityStore
from models.ner_extractor import HybridNERExtractor
from config.settings import API_TITLE, API_VERSION

logger = logging.getLogger(__name__)


# Pydantic models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model: str
    entity_types: List[str]


class ExtractEntitiesRequest(BaseModel):
    """Request model for entity extraction."""
    text: str
    time_id: str = "t_000"


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""
    updates: Dict[str, Any]


# Initialize FastAPI app
def create_app(ner_extractor: HybridNERExtractor) -> FastAPI:
    """Create and configure FastAPI application for entity extraction."""

    app = FastAPI(title=API_TITLE, version=API_VERSION)

    # CORS middleware enabled for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for testing
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize components
    entity_store = EntityStore()

    # Routes

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        try:
            return {
                "status": "healthy",
                "model": ner_extractor.model_name,
                "entity_types": ner_extractor.get_supported_entity_types(),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Entity extraction endpoints

    @app.post("/entities/extract")
    async def extract_entities(request: ExtractEntitiesRequest):
        """Extract entities from story text."""
        try:
            logger.info(f"Extracting entities from text (length: {len(request.text)})")
            logger.debug(f"Story text preview: {request.text[:200]}...")

            entities = await ner_extractor.extract_entities(
                text=request.text,
                time_id=request.time_id
            )

            logger.info(f"Extraction complete. Found {len(entities)} entities")

            # Store extracted entities
            if entities:
                entity_ids = entity_store.add_entities(entities)
                logger.info(f"Stored entities with IDs: {entity_ids}")
            else:
                entity_ids = []
                logger.warning("No entities were extracted from the text")

            return {
                "message": f"Extracted {len(entities)} entities",
                "count": len(entities),
                "entities": entities,
                "entity_ids": entity_ids
            }
        except Exception as e:
            logger.error(f"Failed to extract entities: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/entities")
    async def get_all_entities():
        """Get all stored entities."""
        try:
            entities = entity_store.get_all_entities()
            return {
                "count": len(entities),
                "entities": entities
            }
        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/entities/{entity_id}")
    async def get_entity(entity_id: str):
        """Get a specific entity by ID."""
        try:
            entity = entity_store.get_entity(entity_id)
            if not entity:
                raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
            return entity
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get entity: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/entities/type/{entity_type}")
    async def get_entities_by_type(entity_type: str):
        """Get all entities of a specific type."""
        try:
            entities = entity_store.get_entities_by_type(entity_type)
            return {
                "type": entity_type,
                "count": len(entities),
                "entities": entities
            }
        except Exception as e:
            logger.error(f"Failed to get entities by type: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/entities/search/{query}")
    async def search_entities(query: str):
        """Search entities by name or alias."""
        try:
            entities = entity_store.search_entities(query)
            return {
                "query": query,
                "count": len(entities),
                "entities": entities
            }
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/entities/{entity_id}")
    async def update_entity(entity_id: str, request: EntityUpdateRequest):
        """Update an existing entity."""
        try:
            success = entity_store.update_entity(entity_id, request.updates)
            if not success:
                raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
            
            updated_entity = entity_store.get_entity(entity_id)
            return {
                "message": f"Entity {entity_id} updated",
                "entity": updated_entity
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update entity: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/entities/{entity_id}")
    async def delete_entity(entity_id: str):
        """Delete an entity."""
        try:
            success = entity_store.delete_entity(entity_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
            return {"message": f"Entity {entity_id} deleted"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete entity: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/entities-stats")
    async def get_entity_stats():
        """Get statistics about stored entities."""
        try:
            return entity_store.get_stats()
        except Exception as e:
            logger.error(f"Failed to get entity stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/entities")
    async def clear_all_entities():
        """Clear all entities from the store."""
        try:
            entity_store.clear_all()
            return {"message": "All entities cleared"}
        except Exception as e:
            logger.error(f"Failed to clear entities: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return app
