"""Quick test to see if the model works at all."""
from llama_cpp import Llama

print("Loading model...")
llm = Llama(
    model_path="./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=4,
    n_gpu_layers=0,
    verbose=True,
)

print("\nModel loaded! Testing simple generation...")

# Test 1: Very simple prompt
try:
    response = llm("Say hello", max_tokens=10)
    print(f"\nTest 1 - Simple: {response['choices'][0]['text']}")
except Exception as e:
    print(f"\nTest 1 FAILED: {e}")

# Test 2: JSON request
try:
    response = llm('Return JSON: [{"name":"test"}]', max_tokens=50, stop=["</s>"])
    print(f"\nTest 2 - JSON: {response['choices'][0]['text']}")
except Exception as e:
    print(f"\nTest 2 FAILED: {e}")

# Test 3: Longer generation
try:
    response = llm("List three animals:", max_tokens=100, stop=["</s>"])
    print(f"\nTest 3 - Longer: {response['choices'][0]['text']}")
except Exception as e:
    print(f"\nTest 3 FAILED: {e}")

print("\n✓ All tests completed")
