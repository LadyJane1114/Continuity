"""Token classification-based entity extraction using transformers."""
import logging
from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch

logger = logging.getLogger(__name__)


class NERExtractor:
    """Extracts entities using token classification models (NuNER BERT-based)."""

    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        """
        Initialize the NER extractor.

        Args:
            model_name: HuggingFace model name for token classification
                       Default: dslim/bert-base-NER (reliable, well-tested)
                       Alternative: dbmdz/bert-large-cased-finetuned-conll03-english
        """
        self.model_name = model_name
        logger.info(f"Loading NER model: {model_name}")

        try:
            # Load the NER pipeline with proper aggregation
            self.ner_pipeline = pipeline(
                "ner",
                model=model_name,
                tokenizer=model_name,
                aggregation_strategy="simple",  # Simple aggregation works best
                device=0 if torch.cuda.is_available() else -1  # GPU if available
            )
            logger.info("[OK] NER model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            raise

        # Map NuNER labels to our entity types
        # NuNER uses more granular labels
        self.label_mapping = {
            # People
            'PER': 'character',
            'PERSON': 'character',

            # Locations
            'LOC': 'location',
            'LOCATION': 'location',
            'GPE': 'location',           # Geo-Political Entity
            'FACILITY': 'location',      # Buildings, airports, etc.

            # Organizations
            'ORG': 'organization',
            'ORGANIZATION': 'organization',

            # Objects
            'PRODUCT': 'object',
            'ARTIFACT': 'object',
            'WEAPON': 'object',

            # Events
            'EVENT': 'event',

            # Concepts
            'MISC': 'concept',
            'NORP': 'concept',           # Nationalities, religious/political groups
            'LAW': 'concept',
            'LANGUAGE': 'concept',
            'WORK_OF_ART': 'concept',
        }

    async def extract_entities(self, text: str, time_id: str = "t_000") -> List[Dict[str, Any]]:
        """
        Extract entities from text using token classification.

        Args:
            text: Story text to analyze
            time_id: Time identifier for when this text was added

        Returns:
            List of entity dictionaries in the specified format
        """
        try:
            logger.info(f"Extracting entities from {len(text)} characters of text...")

            # Run NER pipeline
            ner_results = self.ner_pipeline(text)
            logger.info(f"NER found {len(ner_results)} entities")

            # Debug: Print first result to see structure
            if ner_results:
                logger.debug(f"Sample NER result: {ner_results[0]}")

            # Convert to our format
            entities = []
            entity_counter = 1

            for result in ner_results:
                # Extract entity text - use 'word' field which contains the aggregated entity
                entity_name = result.get('word', '').strip()
                entity_label = result.get('entity_group', 'MISC')
                confidence = result.get('score', 0.0)

                # Skip empty or very short entities
                if len(entity_name) < 2:
                    logger.debug(f"Skipping short entity: '{entity_name}'")
                    continue

                # Map to our entity types
                entity_type = self.label_mapping.get(entity_label, 'concept')

                # Only include high-confidence entities
                if confidence >= 0.5:
                    entity_dict = {
                        'id': f"ent_{entity_counter:06d}",
                        'entityType': entity_type,
                        'name': entity_name,
                        'aliases': [],
                        'facts': [],
                        'firstMentionedAt': time_id,
                        'lastUpdatedAt': time_id,
                        'version': 1,
                        'confidence': float(confidence)  # Convert numpy.float32 to Python float
                    }
                    entities.append(entity_dict)
                    entity_counter += 1
                    logger.debug(f"Entity: {entity_name} ({entity_type}) - confidence: {confidence:.2f}")

            logger.info(f"Successfully extracted {len(entities)} entities (NER)")
            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}", exc_info=True)
            return []

    def get_supported_entity_types(self) -> List[str]:
        """Return list of supported entity types."""
        return list(set(self.label_mapping.values()))


class HybridNERExtractor(NERExtractor):
    """
    Enhanced NER extractor with custom rules for story-specific entities.
    Combines BERT NER token classification with pattern matching for better coverage.
    """

    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        super().__init__(model_name)
        
        # Story-specific patterns
        self.story_patterns = {
            'object': [
                r'\b(Sacred|Magic|Ancient|Legendary|Cursed)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
                r'\b([A-Z][a-z]+)\s+(Sword|Shield|Staff|Amulet|Ring|Crown|Orb)\b',
            ],
            'location': [
                r'\b([A-Z][a-z]+)\s+(Kingdom|Castle|Tower|Forest|Mountain|City|Village)\b',
            ],
            'event': [
                r'\b(Battle|War|Siege|Festival|Ceremony)\s+of\s+([A-Z][a-z]+)\b',
            ]
        }
    
    async def extract_entities(self, text: str, time_id: str = "t_000") -> List[Dict[str, Any]]:
        """Extract entities using both NER and pattern matching."""
        import re
        
        # Get NER entities
        entities = await super().extract_entities(text, time_id)
        entity_names = {e['name'].lower() for e in entities}
        entity_counter = len(entities) + 1
        
        # Add pattern-matched entities
        for entity_type, patterns in self.story_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity_name = match.group(0)
                    
                    # Skip if already found by NER
                    if entity_name.lower() in entity_names:
                        continue
                    
                    entity_dict = {
                        'id': f"ent_{entity_counter:06d}",
                        'entityType': entity_type,
                        'name': entity_name,
                        'aliases': [],
                        'facts': [],
                        'firstMentionedAt': time_id,
                        'lastUpdatedAt': time_id,
                        'version': 1,
                        'confidence': 0.9  # High confidence for pattern matches
                    }
                    entities.append(entity_dict)
                    entity_names.add(entity_name.lower())
                    entity_counter += 1
                    logger.debug(f"Pattern match: {entity_name} ({entity_type})")
        
        return entities

