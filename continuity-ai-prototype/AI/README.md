# Entity Extraction API

A minimal entity extraction system powered by local LLM (Phi-4/DeepSeek) for analyzing story text and identifying characters, objects, locations, events, organizations, and concepts.

## Features

- **Local LLM**: Phi-4 or DeepSeek model running via llama-cpp (GGUF)
- **Hybrid Extraction**: Regex pattern matching + LLM validation + LLM classification
- **Entity Storage**: JSON-based persistent storage
- **Web API**: FastAPI REST interface
- **Streaming**: Async streaming extraction for long texts

## Requirements

- Python 3.9+
- 8-16GB RAM (for Q4/Q6 quantized models)
- `llama-cpp-python` installed (via requirements)
- GGUF model file downloaded locally

## Installation

### 1. Set up environment

```bash
cd continuity-ai-prototype/AI
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create `.env` file in the AI directory:

```env
MODEL_PATH=./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 4. Download a model

Download a GGUF model file and place it in the `models/` directory:
- Phi-4 Q6_K: https://huggingface.co/bartowski/Phi-4-GGUF
- DeepSeek-R1-Distill Q4: https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF

## Usage

### Run the application

```bash
python main.py
```

The API will start on `http://localhost:8000`

### API Endpoints

#### Health Check
**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "model": "./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
  "llm": true
}
```

#### Extract Entities
**POST** `/entities/extract`

Request:
```json
{
  "text": "In the Faraway Kingdom, Princess Elara wielded the Sacred Sword against the Dark Guild.",
  "time_id": "t_001"
}
```

Response:
```json
{
  "message": "Extracted 4 entities",
  "count": 4,
  "entities": [
    {
      "id": "ent_000001",
      "entityType": "location",
      "name": "Faraway Kingdom",
      "aliases": [],
      "facts": [{"key": "source", "value": "extracted from text", "time": "t_001"}],
      "version": 1
    },
    {
      "id": "ent_000002",
      "entityType": "character",
      "name": "Elara",
      "aliases": [],
      "facts": [{"key": "source", "value": "extracted from text", "time": "t_001"}],
      "version": 1
    }
  ],
  "entity_ids": ["ent_000001", "ent_000002", "ent_000003", "ent_000004"]
}
```

#### Stream Entity Extraction
**POST** `/entities/extract-stream`

Returns NDJSON stream with status updates.

#### Get All Entities
**GET** `/entities`

#### Get Entity by ID
**GET** `/entities/{entity_id}`

#### Get Entities by Type
**GET** `/entities/type/{entity_type}`

Types: `character`, `location`, `object`, `event`, `organization`, `concept`

#### Search Entities
**GET** `/entities/search/{query}`

#### Update Entity
**PUT** `/entities/{entity_id}`

Request:
```json
{
  "updates": {
    "aliases": ["Princess Elara"],
    "facts": [{"key": "title", "value": "Princess", "time": "t_002"}]
  }
}
```

#### Delete Entity
**DELETE** `/entities/{entity_id}`

#### Get Entity Statistics
**GET** `/entities-stats`

#### Clear All Entities
**DELETE** `/entities`

## How It Works

### Entity Extraction Process

1. **Regex Capture** (High Recall):
   - Finds capitalized words (potential names)
   - Pattern matches for locations ("X Kingdom"), objects ("X Sword"), etc.

2. **LLM Validation** (Precision Filter):
   - Each candidate is validated by the LLM
   - Reduces false positives from common words

3. **LLM Classification**:
   - Validated entities are classified into types
   - Formatted with IDs, facts, and timestamps

### Entity Format

```json
{
  "id": "ent_000001",
  "entityType": "character",
  "name": "Mara Ellison",
  "aliases": ["Mara", "Detective Ellison"],
  "facts": [
    {
      "key": "occupation",
      "value": "detective",
      "time": "t_001"
    }
  ],
  "version": 1
}
```

## Project Structure

```
├── config/
│   └── settings.py          # Configuration
├── models/
│   ├── llm_manager.py       # LLM via llama-cpp
│   └── entity_extractor.py  # Entity extraction logic
├── database/
│   └── entity_store.py      # JSON storage
├── interfaces/
│   └── web_api.py           # FastAPI routes
├── utils/
│   └── logger.py            # Logging setup
├── data/
│   └── entities.json        # Stored entities
├── main.py                  # Entry point
└── requirements.txt
```

## Troubleshooting

**"Model file not found"**
- Verify `MODEL_PATH` in `.env` points to your GGUF file
- Confirm the GGUF file exists at that location

**"Out of memory"**
- Use a smaller quantization (Q4 instead of Q6)
- Reduce `n_ctx` in `llm_manager.py`

**Slow extraction**
- Normal for CPU-only mode
- Consider GPU acceleration by adjusting `n_gpu_layers` in `llm_manager.py`

## License

MIT

