"""Direct test of NER model to debug extraction issues."""
import asyncio
from models.ner_extractor import HybridNERExtractor

async def test_ner():
    print("Loading NER model...")
    extractor = HybridNERExtractor()
    
    # Test with simple text
    test_texts = [
        "John Smith works at Microsoft in Seattle.",
        "Dr. Alicia Moreno met with James O'Connor at NeuroPulse Labs in San Diego, California.",
        "In the Faraway Kingdom, Princess Elara wielded the Sacred Sword.",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {text}")
        print('='*60)
        
        entities = await extractor.extract_entities(text, f"t_{i:03d}")
        
        if entities:
            print(f"Found {len(entities)} entities:")
            for entity in entities:
                print(f"  - {entity['name']} ({entity['entityType']}) - confidence: {entity['confidence']:.2f}")
        else:
            print("No entities found!")

if __name__ == "__main__":
    asyncio.run(test_ner())

