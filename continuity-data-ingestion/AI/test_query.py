#!/usr/bin/env python
"""Quick test script for query endpoint."""
import requests
import time
import sys

# Wait for API to be ready
print("Waiting for API...")
time.sleep(12)

base_url = "http://localhost:8002"

try:
    # Test health
    print("\n=== Testing /health ===")
    resp = requests.get(f"{base_url}/health", timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    # Test query
    print("\n=== Testing /query ===")
    payload = {
        "query": "What is machine learning?",
        "user_id": "test"
    }
    resp = requests.post(f"{base_url}/query", json=payload, timeout=60)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Response: {result}")
    print(f"\n✓ Query successful!")
    print(f"Generated response: {result.get('response', 'N/A')}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
