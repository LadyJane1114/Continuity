"""Test NER with literary/creative fiction text."""
import asyncio
from models.ner_extractor import HybridNERExtractor

async def test_literary():
    print("Loading NER model...")
    extractor = HybridNERExtractor()
    
    # Your actual text
    text = """At dawn, the lighthouse keeper found a letter wedged beneath the door, its paper salted and soft, written in a hand he recognized as his own despite never remembering to write it, and as the fog lifted he saw a ship anchored offshore that bore his name on the hull, though he'd never owned a vessel, never even learned to sail."""
    
    print(f"\nText: {text}\n")
    print("="*80)
    
    entities = await extractor.extract_entities(text, "t_001")
    
    if entities:
        print(f"\nFound {len(entities)} entities:")
        for entity in entities:
            print(f"  - {entity['name']} ({entity['entityType']}) - confidence: {entity['confidence']:.2f}")
    else:
        print("\nNo entities found!")

if __name__ == "__main__":
    asyncio.run(test_literary())

