# Entity Extraction Feature

## Overview
The AI system now includes sophisticated entity extraction capabilities for analyzing story text and identifying characters, objects, locations, events, organizations, and concepts.

## Entity Format

Each entity follows this structure:

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
    },
    {
      "key": "appearance_note",
      "value": "scar under left eye",
      "time": "t_002"
    }
  ],
  "version": 1
}
```

## Entity Types

- **character**: People, animals, creatures
- **object**: Items, weapons, tools, vehicles
- **location**: Places, buildings, cities
- **event**: Significant happenings, incidents
- **organization**: Groups, companies, factions
- **concept**: Ideas, powers, abilities

## API Endpoints

### Extract Entities from Text

**POST** `/entities/extract`

Extract all entities from story text in a single request.

```json
{
  "text": "Detective Mara Ellison stood in the rain...",
  "time_id": "t_001"
}
```

Response:
```json
{
  "message": "Extracted 5 entities",
  "count": 5,
  "entities": [...],
  "entity_ids": ["ent_000001", "ent_000002", ...]
}
```

### Extract Entities (Streaming)

**POST** `/entities/extract-stream`

Stream the extraction process with progress updates.

```json
{
  "text": "Detective Mara Ellison stood in the rain...",
  "time_id": "t_001"
}
```

Returns NDJSON stream:
```json
{"status": "extracting", "message": "Analyzing text for entities..."}
{"status": "complete", "message": "Extracted 5 entities", "entities": [...]}
```

### Get All Entities

**GET** `/entities`

Retrieve all stored entities.

Response:
```json
{
  "count": 42,
  "entities": [...]
}
```

### Get Entity by ID

**GET** `/entities/{entity_id}`

Get a specific entity.

Example: `GET /entities/ent_000001`

### Get Entities by Type

**GET** `/entities/type/{entity_type}`

Get all entities of a specific type.

Example: `GET /entities/type/character`

Response:
```json
{
  "type": "character",
  "count": 15,
  "entities": [...]
}
```

### Search Entities

**GET** `/entities/search/{query}`

Search entities by name or alias.

Example: `GET /entities/search/Mara`

Response:
```json
{
  "query": "Mara",
  "count": 2,
  "entities": [...]
}
```

### Update Entity

**PUT** `/entities/{entity_id}`

Update an existing entity. New facts and aliases are appended to existing ones.

```json
{
  "updates": {
    "facts": [
      {"key": "new_skill", "value": "expert marksman", "time": "t_005"}
    ],
    "aliases": ["The Detective"]
  }
}
```

Response:
```json
{
  "message": "Entity ent_000001 updated",
  "entity": {...}
}
```

### Delete Entity

**DELETE** `/entities/{entity_id}`

Delete a specific entity.

### Get Entity Statistics

**GET** `/entities-stats`

Get statistics about the entity store.

Response:
```json
{
  "total_entities": 42,
  "types": {
    "character": 15,
    "object": 10,
    "location": 8,
    "event": 5,
    "organization": 3,
    "concept": 1
  },
  "storage_path": "data/entities.json"
}
```

### Clear All Entities

**DELETE** `/entities`

Clear all entities from the store.

## Storage

Entities are stored in `data/entities.json` and persist across application restarts.

## Time Identifiers

The `time_id` parameter allows you to track when facts were added, useful for:
- Versioning entity information
- Tracking character development over time
- Managing story timeline

Example time IDs:
- `t_001` - Chapter 1
- `t_chapter_5` - Chapter 5
- `t_2024-01-15` - Specific date
- `t_scene_42` - Scene 42

## Usage Example

```python
import requests

# Extract entities from story text
response = requests.post("http://localhost:8000/entities/extract", json={
    "text": "Detective Mara Ellison examined the ancient sword...",
    "time_id": "t_chapter_1"
})

entities = response.json()["entities"]

# Search for a character
response = requests.get("http://localhost:8000/entities/search/Mara")
mara = response.json()["entities"][0]

# Update character with new information
requests.put(f"http://localhost:8000/entities/{mara['id']}", json={
    "updates": {
        "facts": [
            {"key": "status", "value": "investigating", "time": "t_chapter_2"}
        ]
    }
})
```

## Notes

- The LLM will attempt to extract as many entities as possible from the provided text
- Entity IDs are auto-generated in the format `ent_XXXXXX`
- Version numbers increment with each update
- Facts are never removed, only appended (maintains history)
- Aliases are deduplicated when merging
