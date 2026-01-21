"""Entity extraction from story text."""
import logging
import json
import re
from typing import List, Dict, Any
from models.llm_manager import LLMManager

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extracts story entities (characters, objects, events, etc.) from text."""

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize entity extractor.

        Args:
            llm_manager: LLM manager instance for entity extraction
        """
        self.llm_manager = llm_manager
        logger.info("EntityExtractor initialized")

    def _build_extraction_prompt(self, text: str) -> str:
        """
        Build a prompt for entity extraction.

        Args:
            text: Story text to extract entities from

        Returns:
            Formatted prompt string
        """
        # Simple prompt: just ask for names, roles
        prompt = f"""Extract character names from this text.

Text: {text}

Characters (comma-separated names):"""
        
        return prompt

    async def extract_entities(self, text: str, time_id: str = "t_000") -> List[Dict[str, Any]]:
        """
        Extract entities from story text.

        Args:
            text: Story text to analyze
            time_id: Time identifier for when this text was added (for versioning facts)

        Returns:
            List of entity dictionaries in the specified format
        """
        try:
            logger.info(f"Extracting entities from {len(text)} characters of text...")
            
            # WORKAROUND: LLM is hanging on entity extraction tasks
            # For now, extract common character names manually from text
            entities = self._extract_entities_heuristic(text, time_id)
            
            logger.info(f"Successfully extracted {len(entities)} entities (heuristic method)")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}", exc_info=True)
            return []

    def _extract_entities_heuristic(self, text: str, time_id: str) -> List[Dict[str, Any]]:
        """
        Extract entities using heuristic pattern matching (fallback when LLM fails).
        Looks for capitalized words that appear to be names.

        Args:
            text: Story text
            time_id: Time identifier

        Returns:
            List of entities
        """
        # Common character name patterns
        import re
        
        # Look for capitalized words (potential names)
        # More sophisticated: find capitalized words that appear early or multiple times
        potential_names = set()
        
        # Simple heuristic: find capitalized words in common contexts
        name_contexts = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        
        # Filter out common articles, conjunctions, pronouns that got capitalized
        common_words = {'The', 'And', 'But', 'Once', 'A', 'An', 'In', 'On', 'At', 'By', 'With', 'For', 
                       'They', 'He', 'She', 'It', 'We', 'You', 'I', 'That', 'This', 'Which', 'Who', 'What',
                       'Until', 'Their', 'Over', 'All', 'When', 'Where', 'Why', 'How'}
        
        for name in name_contexts:
            if name not in common_words and len(name) > 2:
                potential_names.add(name)
        
        # Convert to entities
        formatted_entities = []
        for i, name in enumerate(sorted(potential_names), 1):
            entity_id = f"ent_{i:06d}"
            formatted_entity = {
                "id": entity_id,
                "entityType": "character",
                "name": name,
                "aliases": [],
                "facts": [{
                    "key": "source",
                    "value": "extracted from text",
                    "time": time_id
                }],
                "version": 1
            }
            formatted_entities.append(formatted_entity)
        
        return formatted_entities

    def _parse_entities_response(self, response: str, time_id: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into entity format.

        Args:
            response: Raw LLM response
            time_id: Time identifier to add to facts

        Returns:
            List of formatted entities
        """
        try:
            clean_response = response.strip()

            if not clean_response:
                logger.warning("Empty response from LLM")
                return []

            # Check if response is JSON (from fallback)
            if clean_response.startswith("["):
                try:
                    raw_entities = json.loads(clean_response)
                    if isinstance(raw_entities, list):
                        return self._format_entities(raw_entities, time_id)
                except json.JSONDecodeError:
                    pass

            # Parse as comma-separated names (primary path)
            # Split by comma and create character entities
            names = [n.strip() for n in clean_response.split(",") if n.strip()]
            
            if not names:
                logger.warning("No entity names found in response")
                return []
            
            # Convert names to entity dictionaries
            raw_entities = [{"type": "character", "name": name} for name in names]
            return self._format_entities(raw_entities, time_id)
            
        except Exception as e:
            logger.error(f"Error parsing entities: {e}", exc_info=True)
            return []

    def _format_entities(self, raw_entities: List[Dict[str, Any]], time_id: str) -> List[Dict[str, Any]]:
        """
        Format raw entities into standardized format.

        Args:
            raw_entities: List of raw entity dicts
            time_id: Time identifier for facts

        Returns:
            List of formatted entities
        """
        formatted_entities = []
        for i, entity in enumerate(raw_entities, 1):
            entity_id = f"ent_{i:06d}"
            
            facts = []
            for fact in entity.get("facts", []):
                facts.append({
                    "key": fact.get("key", "unknown"),
                    "value": fact.get("value", ""),
                    "time": time_id
                })
            
            formatted_entity = {
                "id": entity_id,
                "entityType": entity.get("type") or entity.get("entityType", "character"),
                "name": entity.get("name", "Unnamed"),
                "aliases": entity.get("aliases", []),
                "facts": facts,
                "version": 1
            }
            
            formatted_entities.append(formatted_entity)
        
        return formatted_entities

    async def extract_entities_stream(self, text: str, time_id: str = "t_000"):
        """
        Stream entity extraction process (for long texts).

        Args:
            text: Story text to analyze
            time_id: Time identifier for facts

        Yields:
            Status updates and final entities
        """
        try:
            yield json.dumps({"status": "extracting", "message": "Analyzing text for entities..."}) + "\n"
            
            entities = await self.extract_entities(text, time_id)
            
            yield json.dumps({
                "status": "complete",
                "message": f"Extracted {len(entities)} entities",
                "entities": entities
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in stream extraction: {e}")
            yield json.dumps({"status": "error", "message": str(e)}) + "\n"
