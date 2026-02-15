"""Token classification-based entity extraction using transformers, with de-duplication and span sanity checks."""
import logging
from typing import List, Dict, Any, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification  # type: ignore
import torch  # type: ignore
import re

logger = logging.getLogger(__name__)

# --- Person name utilities (simple and robust) ---
_PERSON_PARTICLES = {"van", "von", "de", "del", "da", "di", "la", "le"}

def _split_person_name(name: str):
    """
    Return (tokens, last_name, has_particle). Preserves casing in tokens but returns last_name lowercased.
    Examples:
      "Ludwig van Beethoven" -> (["Ludwig","van","Beethoven"], "beethoven", True)
      "Beethoven" -> (["Beethoven"], "beethoven", False)
    """
    toks = [t for t in re.split(r"\s+", name.strip()) if t]
    if not toks:
        return [], "", False
    last = toks[-1].lower()
    has_particle = any(t.lower() in _PERSON_PARTICLES for t in toks[:-1])
    return toks, last, has_particle

def _is_single_surname_form(name: str, full_last: str) -> bool:
    toks = [t for t in re.split(r"\s+", name.strip()) if t]
    return len(toks) == 1 and toks[0].lower() == full_last


def _is_word_boundary(text: str, start: int, end: int) -> bool:
    """Return True if [start:end] aligns with word boundaries in text."""
    left_ok = start == 0 or not text[start - 1].isalnum()
    right_ok = end == len(text) or not text[end].isalnum()
    return left_ok and right_ok


def _strip_possessive(name: str) -> str:
    """Normalize possessives like “Goldstein's”/“Goldstein’s” -> “Goldstein”."""
    return re.sub(r"[’']s\b", "", name.strip())


def _normalize_name(name: str) -> str:
    """Lowercase + strip possessive + collapse whitespace."""
    name = _strip_possessive(name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.lower()


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
                device=0 if torch.cuda.is_available() else -1,  # GPU if available
            )
            logger.info("[OK] NER model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            raise

        # Map common labels to your schema
        self.label_mapping = {
            # People
            "PER": "character",
            "PERSON": "character",
            # Locations
            "LOC": "location",
            "LOCATION": "location",
            "GPE": "location",  # Geo-Political Entity
            "FACILITY": "location",  # Buildings, airports, etc.
            # Organizations
            "ORG": "organization",
            "ORGANIZATION": "organization",
            # Objects
            "PRODUCT": "object",
            "ARTIFACT": "object",
            "WEAPON": "object",
            # Events
            "EVENT": "event",
            # Concepts
            "MISC": "concept",
            "NORP": "concept",  # Nationalities, religious/political groups
            "LAW": "concept",
            "LANGUAGE": "concept",
            "WORK_OF_ART": "concept",
        }

    async def extract_entities(self, text: str, time_id: str = "t_000") -> List[Dict[str, Any]]:
        """
        Extract entities from text using token classification.
        Args:
            text: Story text to analyze
            time_id: Time identifier for when this text was added
        Returns:
            List of entity dictionaries in the specified format (de-duplicated)
        """
        try:
            logger.info(f"Extracting entities from {len(text)} characters of text...")
            logger.info(f"Text preview: {text[:200]}...")

            # Run NER pipeline
            ner_results = self.ner_pipeline(text)
            logger.info(f"NER found {len(ner_results)} entities")
            if ner_results:
                logger.info(f"Sample NER result: {ner_results[0]}")

            # Build de-duped collection: (entityType, normalized_name) -> entity_dict
            by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
            entity_counter = 1

            for result in ner_results:
                start = result.get("start")
                end = result.get("end")
                if start is not None and end is not None:
                    entity_name = text[start:end].strip()
                else:
                    entity_name = result.get("word", "").replace("##", "").strip()

                raw_label = result.get("entity_group", "MISC")
                confidence = float(result.get("score", 0.0))

                # Skip invalid/low-quality items early
                if len(entity_name) < 2:
                    continue

                # Remove obvious punctuation fragments
                if len(entity_name.replace(".", "").replace(",", "").replace("-", "").strip()) < 2:
                    continue

                # Reject spans that don't align with word boundaries to avoid fragments like "tal"
                if start is not None and end is not None and not _is_word_boundary(text, start, end):
                    # still allow known abbreviations like "U.S." which are boundaries, so above check is fine
                    logger.debug(f"Rejecting non-boundary span: '{entity_name}' at [{start}:{end}]")
                    continue

                # Normalize name (handle possessives like "Goldstein's")
                normalized = _normalize_name(entity_name)

                # Skip single letters (unless includes dots like U.S.)
                if len(normalized) == 1 and normalized.isalpha():
                    continue

                # Map to your entity types
                entity_type = self.label_mapping.get(raw_label, "concept")

                # Confidence threshold
                if confidence < 0.85:
                    continue

                # Prepare entity
                key = (entity_type, normalized)
                if key not in by_key:
                    by_key[key] = {
                        "id": f"ent_{entity_counter:06d}",
                        "entityType": entity_type,
                        "name": _strip_possessive(entity_name).strip(),
                        "aliases": [],
                        "facts": [],
                        "firstMentionedAt": time_id,
                        "lastUpdatedAt": time_id,
                        "version": 1,
                        "confidence": confidence,
                        # keep a set of surface forms we saw to later emit as aliases if desired
                        "_seen_forms": { _strip_possessive(entity_name).strip() },
                    }
                    entity_counter += 1
                else:
                    # Merge: keep the canonical display name as the first-seen surface form
                    ent = by_key[key]
                    ent["_seen_forms"].add(_strip_possessive(entity_name).strip())
                    # bump confidence to the max seen
                    if confidence > ent["confidence"]:
                        ent["confidence"] = confidence
                    # version bump to indicate consolidation
                    ent["version"] = ent.get("version", 1) + 1
                    ent["lastUpdatedAt"] = time_id

            # --- After building by_key; before finalization ---
            # Build a map from last_name -> canonical entity (prefer the longest full name)
            surname_index = {}  # last_name -> entity key
            for key, ent in list(by_key.items()):
                if ent["entityType"] != "character":
                    continue
                toks, last, _ = _split_person_name(ent["name"])
                if not last:
                    continue
                # Prefer entities with more tokens (e.g., "Ludwig van Beethoven" over "Beethoven")
                prev_key = surname_index.get(last)
                if prev_key is None:
                    surname_index[last] = key
                else:
                    prev_ent = by_key[prev_key]
                    if len(prev_ent["name"].split()) < len(ent["name"].split()):
                        surname_index[last] = key

            # Second pass: if we see a single-token surname entity separate from its full form, merge it
            for key, ent in list(by_key.items()):
                if ent["entityType"] != "character":
                    continue
                toks, last, _ = _split_person_name(ent["name"])
                if not last:
                    continue
                canonical_key = surname_index.get(last)
                if canonical_key is None or canonical_key == key:
                    continue
                # Merge this entity into the canonical one
                canon = by_key[canonical_key]
                canon["_seen_forms"].update(ent.get("_seen_forms", set()) | {ent["name"]})
                canon["version"] = canon.get("version", 1) + 1
                canon["lastUpdatedAt"] = time_id
                # Keep highest confidence
                if ent["confidence"] > canon["confidence"]:
                    canon["confidence"] = ent["confidence"]
                # Drop the merged entry
                by_key.pop(key, None)

            # Finalize entities
            entities = []
            for ent in by_key.values():
                # Optional: expose extra seen forms as aliases (excluding the primary name)
                primary = ent["name"]
                aliases = sorted({a for a in ent["_seen_forms"] if a and a != primary})
                ent["aliases"] = aliases
                ent.pop("_seen_forms", None)
                entities.append(ent)

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
            "character": [
                # Roles/titles (the lighthouse keeper, the king, etc.)
                r"\bthe\s+(lighthouse\s+keeper|king|queen|prince|princess|wizard|knight|merchant|captain|doctor|professor|detective|priest|monk|sailor|guard|soldier)\b",
                # Capitalized names followed by say/think verbs
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|asked|replied|thought|wondered|remembered|knew|felt)\b",
            ],
            "object": [
                # Magical/special items (capitalized)
                r"\b(Sacred|Magic|Ancient|Legendary|Cursed)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
                r"\b([A-Z][a-z]+)\s+(Sword|Shield|Staff|Amulet|Ring|Crown|Orb)\b",
                # Common story objects
                r"\b(?:the|a)\s+(letter|map|key|book|scroll|diary|journal|compass|lantern|mirror)\b",
            ],
            "location": [
                # Capitalized locations
                r"\b([A-Z][a-z]+)\s+(Kingdom|Castle|Tower|Forest|Mountain|City|Village|Island|Bay|Harbor)\b",
                # Common locations
                r"\b(?:the|a)\s+(lighthouse|tavern|inn|church|cathedral|library|market|square|bridge|gate|harbor|port)\b",
            ],
            "event": [
                r"\b(Battle|War|Siege|Festival|Ceremony)\s+of\s+([A-Z][a-z]+)\b",
            ],
        }

    async def extract_entities(self, text: str, time_id: str = "t_000") -> List[Dict[str, Any]]:
        """Extract entities using both NER and pattern matching, then de-duplicate."""
        import re as _re

        # First, run NER with base logic (which de-dupes already)
        entities = await super().extract_entities(text, time_id)
        nameset = {(e["entityType"], _normalize_name(e["name"])) for e in entities}
        entity_counter = len(entities) + 1

        # Pattern-matched additions
        for entity_type, patterns in self.story_patterns.items():
            for pattern in patterns:
                for match in _re.finditer(pattern, text):
                    entity_name = match.group(0).strip()
                    norm = _normalize_name(entity_name)
                    key = (entity_type, norm)
                    if key in nameset:
                        continue  # already captured by NER

                    # Guard against fragments / spurious short tokens
                    if len(norm) < 2:
                        continue

                    entities.append({
                        "id": f"ent_{entity_counter:06d}",
                        "entityType": entity_type,
                        "name": _strip_possessive(entity_name),
                        "aliases": [],
                        "facts": [],
                        "firstMentionedAt": time_id,
                        "lastUpdatedAt": time_id,
                        "version": 1,
                        "confidence": 0.90,  # high for strict patterns
                    })
                    nameset.add(key)
                    entity_counter += 1
                    logger.debug(f"Pattern match: {entity_name} ({entity_type})")

        return entities
