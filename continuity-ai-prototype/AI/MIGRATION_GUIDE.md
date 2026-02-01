# Migration Guide: Full RAG System → Entity Extraction Only

This document explains the changes made to reduce the AI prototype to only include entity extraction functionality.

## What Was Removed

### Dependencies (requirements.txt)
- ❌ `discord.py` - Discord bot integration
- ❌ `chromadb` - Vector database
- ❌ `sentence-transformers` - Text embeddings
- ❌ `aiohttp` - HTTP client for Discord
- ❌ `asyncio-contextmanager` - Context management utilities

### Files Deleted
- ❌ `interfaces/discord_bot.py` - Discord bot interface
- ❌ `rag/pipeline.py` - RAG orchestration
- ❌ `rag/prompt_builder.py` - Prompt construction for RAG
- ❌ `database/vector_db.py` - ChromaDB interface
- ❌ `models/embedder.py` - Embedding model
- ❌ `utils/context_manager.py` - Conversation history management

### Configuration Removed (config/settings.py)
- ❌ Vector database settings (VECTOR_DB_TYPE, VECTOR_DB_PATH, EMBEDDING_MODEL)
- ❌ RAG settings (TOP_K_RESULTS, CHUNK_SIZE, CHUNK_OVERLAP)
- ❌ Discord settings (DISCORD_TOKEN, DISCORD_PREFIX)
- ❌ Context management settings (MAX_CONTEXT_TOKENS)

### API Endpoints Removed (interfaces/web_api.py)
- ❌ `POST /query` - RAG query processing
- ❌ `POST /query-stream` - Streaming RAG responses
- ❌ `POST /documents` - Add documents to knowledge base
- ❌ `GET /db-info` - Vector database statistics
- ❌ `DELETE /history/{user_id}` - Clear conversation history

## What Was Kept

### Core Dependencies
- ✅ `llama-cpp-python` - Local LLM inference
- ✅ `fastapi` - Web API framework
- ✅ `uvicorn` - ASGI server
- ✅ `pydantic` - Data validation
- ✅ `python-dotenv` - Environment configuration

### Core Files
- ✅ `models/llm_manager.py` - LLM management
- ✅ `models/entity_extractor.py` - Entity extraction logic
- ✅ `database/entity_store.py` - Entity storage (JSON)
- ✅ `interfaces/web_api.py` - Web API (entity endpoints only)
- ✅ `utils/logger.py` - Logging setup
- ✅ `config/settings.py` - Minimal configuration
- ✅ `main.py` - Entry point (simplified)

### API Endpoints Kept
- ✅ `GET /health` - Health check
- ✅ `POST /entities/extract` - Extract entities from text
- ✅ `POST /entities/extract-stream` - Stream entity extraction
- ✅ `GET /entities` - Get all entities
- ✅ `GET /entities/{entity_id}` - Get entity by ID
- ✅ `GET /entities/type/{entity_type}` - Get entities by type
- ✅ `GET /entities/search/{query}` - Search entities
- ✅ `PUT /entities/{entity_id}` - Update entity
- ✅ `DELETE /entities/{entity_id}` - Delete entity
- ✅ `GET /entities-stats` - Entity statistics
- ✅ `DELETE /entities` - Clear all entities

## Files That Still Reference Removed Components

These files are **NOT NEEDED** for entity extraction but were kept for reference:

- ⚠️ `load_knowledge_base.py` - References VectorDB (used for RAG)
- ⚠️ `nscc_data.py` - NSCC knowledge base data (used for RAG)
- ⚠️ `test_query.py` - Tests RAG queries (if exists)

You can safely **delete or ignore** these files.

## How to Use the Minimal System

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
MODEL_PATH=./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 3. Run the Server
```bash
python main.py
```

### 4. Extract Entities
```bash
curl -X POST http://localhost:8000/entities/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "In the Faraway Kingdom, Princess Elara wielded the Sacred Sword.",
    "time_id": "t_001"
  }'
```

## Architecture Comparison

### Before (Full RAG System)
```
User → Web API/Discord Bot
  ↓
RAG Pipeline
  ↓
Vector DB (ChromaDB) + Embedder
  ↓
LLM Manager
  ↓
Response
```

### After (Entity Extraction Only)
```
User → Web API
  ↓
Entity Extractor
  ↓
LLM Manager
  ↓
Entity Store (JSON)
  ↓
Response
```

## Memory Requirements

- **Before**: 20-30GB RAM (for RAG + embeddings + LLM)
- **After**: 8-16GB RAM (for LLM only)

## Disk Space

- **Before**: ~5GB (ChromaDB + embeddings + model)
- **After**: ~1-2GB (model only)

## Documentation

- **Full documentation**: `README.md` (original, references removed features)
- **Minimal documentation**: `README_MINIMAL.md` (entity extraction only)

Use `README_MINIMAL.md` as your primary reference.

