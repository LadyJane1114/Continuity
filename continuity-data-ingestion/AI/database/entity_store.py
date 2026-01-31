"""Entity storage and management."""
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EntityStore:
    """Manages storage and retrieval of story entities."""

    def __init__(self, storage_path: str = "data/entities.json"):
        """
        Initialize entity store.

        Args:
            storage_path: Path to JSON file for storing entities
        """
        self.storage_path = Path(storage_path)
        self.entities: Dict[str, Dict[str, Any]] = {}
        self._load_entities()
        logger.info(f"EntityStore initialized with {len(self.entities)} entities")

    def _load_entities(self):
        """Load entities from storage file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entities = {e["id"]: e for e in data.get("entities", [])}
                    logger.info(f"Loaded {len(self.entities)} entities from {self.storage_path}")
            else:
                logger.info(f"No existing entity store found at {self.storage_path}")
                self.entities = {}
        except Exception as e:
            logger.error(f"Error loading entities: {e}")
            self.entities = {}

    def _save_entities(self):
        """Save entities to storage file."""
        try:
            # Create directory if it doesn't exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save entities
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "entities": list(self.entities.values()),
                    "count": len(self.entities)
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.entities)} entities to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving entities: {e}")

    def add_entity(self, entity: Dict[str, Any]) -> str:
        """
        Add a new entity to the store.

        Args:
            entity: Entity dictionary

        Returns:
            Entity ID
        """
        entity_id = entity.get("id")
        if not entity_id:
            # Generate new ID if not provided
            entity_id = f"ent_{len(self.entities) + 1:06d}"
            entity["id"] = entity_id
        
        self.entities[entity_id] = entity
        self._save_entities()
        logger.info(f"Added entity: {entity_id} ({entity.get('name')})")
        return entity_id

    def add_entities(self, entities: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple entities to the store.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of entity IDs
        """
        entity_ids = []
        for entity in entities:
            entity_id = self.add_entity(entity)
            entity_ids.append(entity_id)
        return entity_ids

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity dictionary or None
        """
        return self.entities.get(entity_id)

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """
        Get all entities.

        Returns:
            List of all entities
        """
        return list(self.entities.values())

    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all entities of a specific type.

        Args:
            entity_type: Type of entity (character, object, location, etc.)

        Returns:
            List of matching entities
        """
        return [e for e in self.entities.values() if e.get("entityType") == entity_type]

    def search_entities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search entities by name or alias.

        Args:
            query: Search query

        Returns:
            List of matching entities
        """
        query_lower = query.lower()
        results = []
        
        for entity in self.entities.values():
            # Check name
            if query_lower in entity.get("name", "").lower():
                results.append(entity)
                continue
            
            # Check aliases
            aliases = entity.get("aliases", [])
            if any(query_lower in alias.lower() for alias in aliases):
                results.append(entity)
                continue
        
        return results

    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing entity.

        Args:
            entity_id: Entity ID
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        if entity_id not in self.entities:
            logger.warning(f"Entity {entity_id} not found")
            return False
        
        # Update entity
        entity = self.entities[entity_id]
        
        # Merge facts if provided
        if "facts" in updates:
            existing_facts = entity.get("facts", [])
            new_facts = updates["facts"]
            # Append new facts
            entity["facts"] = existing_facts + new_facts
            del updates["facts"]
        
        # Merge aliases if provided
        if "aliases" in updates:
            existing_aliases = set(entity.get("aliases", []))
            new_aliases = set(updates["aliases"])
            entity["aliases"] = list(existing_aliases | new_aliases)
            del updates["aliases"]
        
        # Update other fields
        entity.update(updates)
        
        # Increment version
        entity["version"] = entity.get("version", 1) + 1
        
        self._save_entities()
        logger.info(f"Updated entity: {entity_id}")
        return True

    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity ID

        Returns:
            True if successful, False otherwise
        """
        if entity_id in self.entities:
            del self.entities[entity_id]
            self._save_entities()
            logger.info(f"Deleted entity: {entity_id}")
            return True
        return False

    def clear_all(self):
        """Clear all entities from the store."""
        self.entities = {}
        self._save_entities()
        logger.info("Cleared all entities")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the entity store.

        Returns:
            Dictionary with stats
        """
        types = {}
        for entity in self.entities.values():
            entity_type = entity.get("entityType", "unknown")
            types[entity_type] = types.get(entity_type, 0) + 1
        
        return {
            "total_entities": len(self.entities),
            "types": types,
            "storage_path": str(self.storage_path)
        }
