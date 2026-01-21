"""FastAPI web interface."""
import logging
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from database.vector_db import VectorDB
from models.llm_manager import LLMManager
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
    
    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(vector_db, llm_manager)

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
        """Stream response for a query."""
        try:
            context_manager.add_message(request.user_id, "user", request.query)
            chat_history = context_manager.get_history(request.user_id)

            async def generate():
                response_text = ""
                async for token in rag_pipeline.query_stream(
                    user_query=request.query,
                    chat_history=chat_history,
                ):
                    response_text += token
                    yield token

                # Add to history
                context_manager.add_message(request.user_id, "assistant", response_text)

            return StreamingResponse(generate(), media_type="text/plain")
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

    return app
