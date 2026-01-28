"""FastAPI web interface."""
import logging
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio

from database.vector_db import VectorDB
from database.entity_store import EntityStore
from models.llm_manager import LLMManager
from models.entity_extractor import EntityExtractor
from rag.pipeline import RAGPipeline
from utils.context_manager import ContextManager
from config.settings import API_TITLE, API_VERSION, API_HOST, API_PORT

logger = logging.getLogger(__name__)


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    user_id: str = "default"
    use_context: bool = True
    stream: bool = False


class AddDocumentRequest(BaseModel):
    """Request model for adding documents."""
    documents: List[str]
    metadata: Optional[List[dict]] = None


class QueryResponse(BaseModel):
    """Response model for queries."""
    response: str
    sources: List[dict] = []
    user_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model: str
    vector_db: bool
    llm: bool


class ExtractEntitiesRequest(BaseModel):
    """Request model for entity extraction."""
    text: str
    time_id: str = "t_000"


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""
    updates: Dict[str, Any]


# Initialize FastAPI app
def create_app(
    vector_db: VectorDB,
    llm_manager: LLMManager,
    context_manager: ContextManager,
) -> FastAPI:
    """Create and configure FastAPI application."""

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
    rag_pipeline = RAGPipeline(vector_db, llm_manager)
    entity_extractor = EntityExtractor(llm_manager)
    entity_store = EntityStore()

    # Routes

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        try:
            llm_ok = await llm_manager.health_check()
            vector_db_info = vector_db.get_collection_info()
            
            return {
                "status": "healthy" if llm_ok else "degraded",
                "model": llm_manager.model,
                "vector_db": vector_db_info["document_count"] > 0,
                "llm": llm_ok,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/query", response_model=QueryResponse)
    async def query(request: QueryRequest):
        """Process a user query."""
        try:
            logger.info(f"Processing query from user {request.user_id}: {request.query[:50]}...")
            
            # Add user message to history
            context_manager.add_message(request.user_id, "user", request.query)

            # Get chat history
            chat_history = context_manager.get_history(request.user_id)

            logger.info("Running RAG pipeline...")
            # Run RAG pipeline
            response, sources = await rag_pipeline.query(
                user_query=request.query,
                chat_history=chat_history,
                use_context=request.use_context,
            )

            logger.info(f"Generated response of length {len(response)}")
            # Add assistant response to history
            context_manager.add_message(request.user_id, "assistant", response)

            return {
                "response": response,
                "sources": sources,
                "user_id": request.user_id,
            }
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/query-stream")
    async def query_stream(request: QueryRequest):
        """Stream response for a query as JSON."""
        try:
            import json
            
            context_manager.add_message(request.user_id, "user", request.query)
            chat_history = context_manager.get_history(request.user_id)

            async def generate():
                response_text = ""
                async for token in rag_pipeline.query_stream(
                    user_query=request.query,
                    chat_history=chat_history,
                ):
                    response_text += token
                    # Send each token as JSON
                    yield json.dumps({"token": token, "done": False}) + "\n"

                # Add to history
                context_manager.add_message(request.user_id, "assistant", response_text)
                
                # Send final completion message
                yield json.dumps({"token": "", "done": True, "response": response_text}) + "\n"

            return StreamingResponse(generate(), media_type="application/x-ndjson")
        except Exception as e:
            logger.error(f"Stream query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/documents")
    async def add_documents(request: AddDocumentRequest):
        """Add documents to the knowledge base."""
        try:
            rag_pipeline.add_knowledge_base(
                documents=request.documents,
                metadata=request.metadata,
            )
            return {
                "message": f"Added {len(request.documents)} documents",
                "count": len(request.documents),
            }
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/db-info")
    async def get_db_info():
        """Get vector database information."""
        try:
            return vector_db.get_collection_info()
        except Exception as e:
            logger.error(f"Failed to get DB info: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/history/{user_id}")
    async def clear_history(user_id: str):
        """Clear conversation history for a user."""
        context_manager.clear_history(user_id)
        return {"message": f"History cleared for user {user_id}"}

    # Entity extraction endpoints

    @app.post("/entities/extract")
    async def extract_entities(request: ExtractEntitiesRequest):
        """Extract entities from story text."""
        try:
            logger.info(f"Extracting entities from text (length: {len(request.text)})")
            logger.debug(f"Story text preview: {request.text[:200]}...")
            
            entities = await entity_extractor.extract_entities(
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

    @app.post("/entities/extract-stream")
    async def extract_entities_stream(request: ExtractEntitiesRequest):
        """Stream entity extraction from story text."""
        try:
            import json
            
            async def generate():
                async for update in entity_extractor.extract_entities_stream(
                    text=request.text,
                    time_id=request.time_id
                ):
                    yield update
                    
                    # If extraction is complete, store entities
                    try:
                        data = json.loads(update)
                        if data.get("status") == "complete" and "entities" in data:
                            entity_store.add_entities(data["entities"])
                    except:
                        pass

            return StreamingResponse(generate(), media_type="application/x-ndjson")
        except Exception as e:
            logger.error(f"Stream extraction failed: {e}")
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
