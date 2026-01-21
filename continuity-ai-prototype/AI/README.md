# AI Assistant with RAG - Phi 4 Edition

An intelligent assistant powered by local Phi 4 GGUF models, vector embeddings, and RAG (Retrieval-Augmented Generation).

## Features

- **Local LLM**: Phi 4 reasoning model running via llama-cpp (GGUF)
- **Vector Database**: ChromaDB for semantic search
- **RAG Pipeline**: Context-aware responses using document retrieval
- **Web API**: FastAPI REST interface for integrations
- **Discord Bot**: Native Discord bot interface
- **Conversation Memory**: Per-user session management
- **Streaming**: Async streaming responses

## Requirements

- Python 3.9+
- 20-30GB RAM (for Q6_K Phi 4)
- `llama-cpp-python` installed (via requirements)
- Phi 4 Q6_K GGUF downloaded locally (e.g., `phi-4-reasoning-q6_k.gguf`)

## Installation

### 1. Set up environment

```bash
cd "c:\Hackathon 26"
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create `.env` file in project root:

```env
MODEL_PATH=./models/phi-4-reasoning-q6_k.gguf
DISCORD_TOKEN=your_token_here
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 4. Add your knowledge base

Create a script or use the API to add documents:

```python
from database.vector_db import VectorDB

db = VectorDB()
db.add_documents([
    "Your document text here...",
    "Another document...",
])
```

## Usage

### Ensure model is available

Place your GGUF file locally (default path `./models/phi-4-reasoning-q6_k.gguf`). Adjust `MODEL_PATH` in `.env` if needed.

### Run the application

**Web API only:**
```bash
python main.py --mode web
```

**Discord Bot only:**
```bash
python main.py --mode discord
```

**Both (default):**
```bash
python main.py
```

### API Endpoints

- `GET /health` - Health check
- `POST /query` - Process a query
- `POST /query-stream` - Stream response
- `POST /documents` - Add documents to knowledge base
- `GET /db-info` - Vector DB statistics
- `DELETE /history/{user_id}` - Clear user history

### Example API calls

**Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "user_id": "user123",
    "use_context": true
  }'
```

**Add documents:**
```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Machine learning is a subset of AI...",
      "Neural networks are inspired by..."
    ],
    "metadata": [
      {"source": "article1"},
      {"source": "article2"}
    ]
  }'
```

### Discord Bot

Mention the bot in a message:
```
@YourBot What is in your knowledge base?
```

Commands:
- `!help` - Show help
- `!clear` - Clear conversation history

## Project Structure

```
├── config/
│   └── settings.py          # Configuration
├── models/
│   ├── llm_manager.py       # Phi 4 via llama-cpp
│   └── embedder.py          # Embedding model
├── database/
│   └── vector_db.py         # ChromaDB interface
├── rag/
│   ├── pipeline.py          # RAG orchestration
│   └── prompt_builder.py    # Prompt construction
├── interfaces/
│   ├── web_api.py           # FastAPI routes
│   └── discord_bot.py       # Discord commands
├── utils/
│   ├── context_manager.py   # Session management
│   └── logger.py            # Logging setup
├── main.py                  # Entry point
└── requirements.txt
```

## Architecture

```
User Input (Web/Discord)
        ↓
Parse & Validate
        ↓
Embed Query
        ↓
Vector Search (ChromaDB)
        ↓
Retrieve Context
        ↓
Build RAG Prompt
        ↓
Phi 4 (llama-cpp)
        ↓
Stream/Format Response
        ↓
Return to User
```

## Performance Tips

- **Warm up model**: First inference is slower, subsequent calls are faster
- **Batch embeddings**: Add multiple documents at once
- **Adjust top_k**: Lower values (3-5) for faster retrieval
- **GPU acceleration**: Configure Ollama for GPU if available

## Troubleshooting

**"Model file not found"**
- Verify `MODEL_PATH` in `.env` points to your GGUF file
- Confirm the GGUF file exists at that location

**"Out of memory"**
- Reduce model context or use smaller quantization
- Check system RAM availability

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
