"""Entity extraction from story text."""
import logging
import json
import re
import asyncio
from typing import List, Dict, Any
from models.llm_manager import LLMManager
from config.settings import ENTITY_EXTRACTION_MODE

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
        Extract entities from story text using configured method.

        Args:
            text: Story text to analyze
            time_id: Time identifier for when this text was added

        Returns:
            List of entity dictionaries in the specified format
        """
        try:
            logger.info(f"Extracting entities from {len(text)} characters of text...")
<<<<<<< Updated upstream
            logger.info(f"Using extraction mode: {ENTITY_EXTRACTION_MODE}")
            
            if ENTITY_EXTRACTION_MODE == "hybrid":
                logger.info("Mode: HYBRID (regex candidates + SLM classification)")
                entities = await self._extract_entities_hybrid(text)
            elif ENTITY_EXTRACTION_MODE == "slm-only":
                logger.info("Mode: SLM-ONLY (full SLM extraction)")
                entities = await self._extract_entities_slm_only(text)
            else:
                logger.error(f"Unknown extraction mode: {ENTITY_EXTRACTION_MODE}")
                return []
            
            logger.info(f"Extracted {len(entities)} entities")
            
            # Format entities
            formatted_entities = self._format_entities(entities, time_id)
            logger.info(f"Successfully extracted {len(formatted_entities)} entities")
=======

            # Step 1: Loose regex capture (high recall, okay with noise)
            candidates = self._capture_entity_candidates(text)
            logger.info(f"Initial candidates: {len(candidates)}")
            print(f"[CANDIDATES] {candidates}")

            # Step 2: Validate each candidate with SLM (in batches to avoid context overflow)
            validated = []
            batch_size = 3  # Process only 3 candidates at a time

            for i in range(0, len(candidates), batch_size):
                batch = candidates[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {batch}")
                print(f"[BATCH {i//batch_size + 1}] Starting validation for: {batch}")

                # Force context reset before each batch
                try:
                    self.llm_manager.reset_context()
                    logger.info("Context reset before batch")
                except Exception as e:
                    logger.warning(f"Context reset failed: {e}")

                for idx, candidate in enumerate(batch):
                    try:
                        logger.info(f"Validating candidate {idx+1}/{len(batch)}: '{candidate}'")
                        print(f"[VALIDATING] {candidate}...")
                        is_entity = await self._validate_entity_candidate(candidate, text)
                        if is_entity:
                            validated.append(candidate)
                            print(f"[ENTITY FOUND] {candidate}")
                        else:
                            print(f"[REJECTED] {candidate}")
                    except Exception as e:
                        logger.error(f"Error validating '{candidate}': {e}", exc_info=True)
                        print(f"[ERROR] {candidate}: {e}")
                        continue

                # Small delay between batches
                logger.info(f"Batch {i//batch_size + 1} complete, waiting...")
                await asyncio.sleep(0.2)

            logger.info(f"Validated entities: {len(validated)}")

            # Step 3: Classify each validated entity (also in batches)
            entities = []
            for i in range(0, len(validated), batch_size):
                batch = validated[i:i+batch_size]
                logger.info(f"Classifying batch {i//batch_size + 1}: {batch}")

                # Force context reset before each batch
                try:
                    self.llm_manager.reset_context()
                except:
                    pass

                for entity_name in batch:
                    try:
                        entity_type = await self._classify_entity_type(entity_name, text)
                        if entity_type and entity_type != 'none':
                            entity_dict = {
                                'name': entity_name,
                                'type': entity_type
                            }
                            entities.append(entity_dict)
                            print(f"[CLASSIFIED] {entity_name} as {entity_type}")
                    except Exception as e:
                        logger.warning(f"Skipping classification for '{entity_name}': {e}")
                        continue

                # Small delay between batches
                await asyncio.sleep(0.1)

            # Format entities
            formatted_entities = self._format_entities(entities, time_id)
            logger.info(f"Successfully extracted {len(formatted_entities)} entities (hybrid regex+SLM)")
            print(f"[FINAL ENTITIES] {formatted_entities}")
>>>>>>> Stashed changes
            return formatted_entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}", exc_info=True)
            return []

    async def _extract_entities_hybrid(self, text: str) -> List[Dict[str, Any]]:
        """
        Hybrid approach: Use regex to capture candidates, then SLM to classify.
        
        Args:
            text: Story text to analyze
            
        Returns:
            List of entity dictionaries
        """
        try:
            # Step 1: Loose regex capture (high recall, okay with noise)
            candidates = self._capture_entity_candidates(text)
            logger.info(f"Initial candidates: {len(candidates)}")
            
            # Step 2: Classify each candidate
            entities = []
            for i, candidate in enumerate(candidates, 1):
                try:
                    logger.info(f"Processing {i}/{len(candidates)}: '{candidate}'")
                    entity_type = await asyncio.wait_for(
                        self._classify_entity_type(candidate, text),
                        timeout=10.0
                    )
                    if entity_type and entity_type != 'none':
                        entity_dict = {
                            'name': candidate,
                            'type': entity_type
                        }
                        entities.append(entity_dict)
                        logger.info(f"+ '{candidate}' -> {entity_type}")
                    else:
                        logger.info(f"- '{candidate}' (rejected)")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on '{candidate}', skipping")
                except Exception as e:
                    logger.error(f"Error on '{candidate}': {e}")
            
            logger.info(f"Hybrid extraction complete: {len(entities)} entities found")
            return entities
            
        except Exception as e:
            logger.error(f"Error in hybrid extraction: {e}", exc_info=True)
            return []

    async def _extract_entities_slm_only(self, text: str) -> List[Dict[str, Any]]:
        """
        SLM-only approach: Use SLM to directly extract entity names.
        
        Args:
            text: Story text to analyze
            
        Returns:
            List of entity dictionaries
        """
        try:
            # Truncate to prevent model issues
            context = text[:400] if len(text) > 400 else text
            
            prompt = f"""Example Story:
Deep within the mist‑soaked kingdom of Eldervale, a young mage named Liora discovered a silver seed glowing at the heart of an abandoned forest temple.

Example Names:
Liora

Now extract character names from this story. List one per line.

Story: {context}

Names:"""
            
            logger.info("Sending extraction request to SLM...")
            response = await self.llm_manager.generate(
                prompt=prompt,
                temperature=0.1,
            )
            
            # Log full response for debugging
            logger.info(f"=== SLM FULL RESPONSE ===")
            logger.info(f"{response}")
            logger.info(f"=== END RESPONSE ===")
            
            # Parse names line by line
            entities = []
            try:
                lines = response.strip().split('\n')
                logger.info(f"Found {len(lines)} lines in response")
                
                for line in lines:
                    line = line.strip()
                    if not line or len(line) < 2:
                        continue
                    
                    # Skip lines that look like explanations or metadata
                    if any(x in line.lower() for x in [':', '-', 'name', 'here', 'story', 'the ']):
                        continue
                    
                    # Skip if it's all lowercase (probably not a name)
                    if line.islower():
                        continue
                    
                    # This is likely a name
                    name = line.strip()
                    if len(name) > 2 and len(name) < 50:
                        entities.append({
                            'name': name,
                            'type': 'character'  # For now, assume all extracted names are characters
                        })
                        logger.info(f"+ Found name: '{name}'")
                    
            except Exception as e:
                logger.error(f"Error parsing SLM response: {e}")
                logger.debug(f"Response was: {response[:300]}")
            
            logger.info(f"SLM-only extraction complete: {len(entities)} names found")
            return entities
            
        except Exception as e:
            logger.error(f"Error in SLM-only extraction: {e}", exc_info=True)
            return []

    def _normalize_entity_type(self, entity_type: str) -> str:
        """
        Normalize entity type to standard types.
        
        Args:
            entity_type: Raw entity type from SLM
            
        Returns:
            Normalized entity type or 'none'
        """
        entity_type_lower = entity_type.lower().strip()
        
        # Map variations to standard types
        if any(x in entity_type_lower for x in ['person', 'character', 'human', 'animal']):
            return 'character'
        elif any(x in entity_type_lower for x in ['place', 'location', 'city', 'building', 'land']):
            return 'location'
        elif any(x in entity_type_lower for x in ['thing', 'object', 'item', 'weapon', 'tool']):
            return 'object'
        elif any(x in entity_type_lower for x in ['event', 'incident', 'happening']):
            return 'event'
        elif any(x in entity_type_lower for x in ['organization', 'org', 'group', 'company', 'faction']):
            return 'organization'
        elif any(x in entity_type_lower for x in ['concept', 'ability', 'power', 'idea']):
            return 'concept'
        else:
            return 'none'

    def _capture_entity_candidates(self, text: str) -> List[str]:
        """
        Capture potential entities using loose regex (high recall).

        Args:
            text: Story text

        Returns:
            List of candidate entity names
        """
        import re

        candidates = set()

        # Common words to exclude (articles, pronouns, common verbs, etc.)
        stopwords = {
            'The', 'A', 'An', 'This', 'That', 'These', 'Those', 'It', 'He', 'She',
            'They', 'We', 'You', 'I', 'My', 'Your', 'His', 'Her', 'Their', 'Our',
            'Was', 'Were', 'Is', 'Are', 'Be', 'Been', 'Being', 'Have', 'Has', 'Had',
            'Do', 'Does', 'Did', 'Will', 'Would', 'Could', 'Should', 'May', 'Might',
            'Must', 'Can', 'When', 'Where', 'Why', 'How', 'What', 'Which', 'Who',
            'If', 'Then', 'But', 'And', 'Or', 'Not', 'No', 'Yes', 'So', 'As', 'At',
            'By', 'For', 'From', 'In', 'Of', 'On', 'To', 'With', 'About', 'After',
            'Before', 'During', 'Since', 'Until', 'While'
        }

        # Capture all capitalized words (including multi-word names)
        capitalized = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        for word in capitalized:
            # Filter out stopwords and very short words
            if len(word) > 2 and len(word.split()) <= 3 and word not in stopwords:
                candidates.add(word)

        # Also capture keywords patterns
        keywords = ['kingdom', 'castle', 'sword', 'magic', 'battle', 'guild', 'curse']
        for keyword in keywords:
            pattern = r'(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+' + keyword + r'\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 2 and match not in stopwords:
                    candidates.add(match)

        logger.debug(f"Captured {len(candidates)} candidates: {sorted(candidates)}")
        return sorted(list(candidates))

    async def _validate_entity_candidate(self, candidate: str, text: str) -> bool:
        """
        Use SLM to validate if a candidate is an actual entity.

        Args:
            candidate: Potential entity name
            text: Story context

        Returns:
            True if it's a real entity, False otherwise
        """
        try:
            # Very minimal context
            context_match = text.find(candidate)
            if context_match != -1:
                start = max(0, context_match - 15)
                end = min(len(text), context_match + len(candidate) + 15)
                context = text[start:end]
            else:
                context = text[:50]

            # Ultra-short prompt
            prompt = f"'{candidate}' entity? {context}\nYES/NO:"

            response = await self.llm_manager.generate(
                prompt=prompt,
                temperature=0.1,
                reset_context=True,
            )

            is_entity = 'YES' in response.upper()
            logger.debug(f"Validation '{candidate}': {is_entity} (response: {response[:50]})")
            return is_entity

        except asyncio.TimeoutError:
            logger.warning(f"Validation timeout for '{candidate}' - skipping")
            return False  # Default to False on timeout to avoid bad data
        except Exception as e:
            logger.warning(f"Validation error for '{candidate}': {e}")
            return False

    async def _classify_entity_type(self, entity_name: str, text: str) -> str:
        """
        Use SLM to classify the type of entity.

        Args:
            entity_name: Validated entity name
            text: Story context

        Returns:
            Entity type: character, location, object, event, organization, concept, or none
        """
        try:
<<<<<<< Updated upstream
            # Ultra-short context to prevent crashes
            context = text[:150]
            
            # Very simple prompt
            prompt = f"""Is "{entity_name}" a person/character, place/location, or thing/object?

Story: {context}

Answer (person/place/thing/none):"""
            
=======
            # Very minimal context
            context_match = text.find(entity_name)
            if context_match != -1:
                start = max(0, context_match - 15)
                end = min(len(text), context_match + len(entity_name) + 15)
                context = text[start:end]
            else:
                context = text[:50]

            # Ultra-short prompt
            prompt = f"'{entity_name}' type?\n{context}\ncharacter/location/object/event/org/concept:"

>>>>>>> Stashed changes
            response = await self.llm_manager.generate(
                prompt=prompt,
                temperature=0.1,
                reset_context=True,
            )
<<<<<<< Updated upstream
            
            # Map response
            response_lower = response.strip().lower()
            logger.debug(f"'{entity_name}' -> '{response_lower}'")
            
            if 'person' in response_lower or 'character' in response_lower:
                return 'character'
            elif 'place' in response_lower or 'location' in response_lower:
                return 'location'
            elif 'thing' in response_lower or 'object' in response_lower:
                return 'object'
            else:
                return 'none'
            
=======

            # Extract the type from response
            response_lower = response.lower().strip()
            types = ['character', 'location', 'object', 'event', 'organization', 'org', 'concept']

            # First try exact match
            if response_lower in types:
                # Map 'org' to 'organization'
                if response_lower == 'org':
                    response_lower = 'organization'
                logger.debug(f"Classification '{entity_name}': {response_lower}")
                return response_lower

            # Then try substring match
            for entity_type in types:
                if entity_type in response_lower:
                    if entity_type == 'org':
                        entity_type = 'organization'
                    logger.debug(f"Classification '{entity_name}': {entity_type}")
                    return entity_type

            logger.warning(f"Could not classify '{entity_name}', response: {response[:50]}")
            return 'none'

>>>>>>> Stashed changes
        except Exception as e:
            logger.warning(f"Classification error for '{entity_name}': {e}")
            return 'none'

    def _extract_entities_heuristic(self, text: str, time_id: str) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Use the hybrid regex + SLM approach instead.
        """
        return []
        import re
        
        entities_dict = {}  # Deduplicate by normalized name only (first type wins)
        
        # Helper to normalize names (lowercase for dedup, keep original for display)
        def add_entity(name, entity_type):
            normalized = name.lower().strip()
            # Avoid very long captures (likely regex errors)
            if len(name) > 100:
                return
            # Avoid multi-word false positives like "protected the"
            if len(normalized.split()) > 3:
                return
            # Skip if already seen (first type wins)
            if normalized in entities_dict:
                return
            entities_dict[normalized] = {'type': entity_type, 'name': name}
        
        # ===== CHARACTERS: Capitalized words (excluding common words) =====
        name_contexts = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        common_words = {'The', 'And', 'But', 'Once', 'A', 'An', 'In', 'On', 'At', 'By', 'With', 'For', 
                       'They', 'He', 'She', 'It', 'We', 'You', 'I', 'That', 'This', 'Which', 'Who', 'What',
                       'Until', 'Their', 'Over', 'All', 'When', 'Where', 'Why', 'How', 'From', 'To', 'Is', 'Are',
                       'Was', 'Were', 'Be', 'Being', 'Been', 'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will',
                       'Would', 'Could', 'Should', 'May', 'Might', 'Must', 'Can', 'Not', 'No', 'Yes', 'Protected',
                       'Ruled', 'Lived', 'Threatened', 'Alongside',
                       # Descriptive words (adjectives, adverbs)
                       'Faraway', 'Dark', 'Brave', 'Fair', 'Great', 'Golden', 'Ancient', 'Sacred', 'Forbidden',
                       'Mighty', 'Evil', 'Good', 'Bad', 'Small', 'Large', 'Big', 'Little', 'New', 'Old', 'Young'}
        
        # Check if a word appears in lowercase (indicates it's probably an adjective, not a proper noun)
        # Only filter words that are KNOWN descriptive adjectives
        lowercase_words = re.findall(r'\b([a-z]+)\b', text.lower())
        
        # List of adjectives we know to filter (appear as both lowercase and capitalized)
        known_adjectives = {'faraway', 'dark', 'brave', 'fair', 'great', 'golden', 'ancient', 'sacred'}
        
        for name in name_contexts:
            if name not in common_words and len(name) > 2 and len(name.split()) <= 2:
                # Skip if it's a known adjective that appears in lowercase in the text
                if name.lower() not in known_adjectives or name.lower() not in lowercase_words:
                    add_entity(name, 'character')
        
        # ===== LOCATIONS: Only match clear location phrases =====
        location_keywords = ['kingdom', 'castle', 'realm', 'forest', 'village', 'city', 'land', 'tower']
        for keyword in location_keywords:
            # Match only 1-word adjective/name before location keyword, with "the" optional
            pattern = r'(?:the\s+)?([A-Z][a-z]+)\s+' + keyword + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                if name not in common_words:
                    add_entity(name, 'location')
        
        # ===== OBJECTS: Sword, crown, ring, etc. =====
        object_keywords = ['sword', 'crown', 'ring', 'amulet', 'artifact', 'weapon', 'staff', 'wand',
                          'shield', 'axe', 'bow', 'armor', 'gem', 'stone', 'chalice']
        for keyword in object_keywords:
            pattern = r'(?:the\s+)?([A-Z][a-z]+)\s+' + keyword + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                if name not in common_words:
                    add_entity(name, 'object')
        
        # ===== EVENTS: Battle, war, ceremony, etc. =====
        event_keywords = ['battle', 'war', 'ceremony', 'meeting', 'coronation', 'quest', 'siege']
        for keyword in event_keywords:
            pattern = r'(?:the\s+)?([A-Z][a-z]+)\s+' + keyword + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                if name not in common_words:
                    add_entity(name, 'event')
        
        # ===== ORGANIZATIONS: Kingdom, guild, order, etc. =====
        org_keywords = ['guild', 'order', 'council', 'empire', 'society', 'brotherhood', 'faction']
        for keyword in org_keywords:
            pattern = r'(?:the\s+)?([A-Z][a-z]+)\s+' + keyword + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                if name not in common_words:
                    add_entity(name, 'organization')
        
        # ===== CONCEPTS: Magic, curse, prophecy, etc. =====
        concept_keywords = ['magic', 'curse', 'prophecy', 'spell', 'power', 'fate', 'darkness', 'light']
        for keyword in concept_keywords:
            pattern = r'\b([A-Z][a-z]+)\s+' + keyword + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                if name not in common_words:
                    add_entity(name, 'concept')
        
        # Convert to formatted entities
        formatted_entities = []
        for i, (normalized_name, entity) in enumerate(sorted(entities_dict.items()), 1):
            entity_id = f"ent_{i:06d}"
            formatted_entity = {
                "id": entity_id,
                "entityType": entity['type'],
                "name": entity['name'],
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
