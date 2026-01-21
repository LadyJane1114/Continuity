import time
from llama_cpp import Llama

llm = Llama(model_path='./models/Phi-4-reasoning-plus-Q6_K.gguf', n_ctx=512, n_threads=4, n_gpu_layers=0, verbose=False)
print('Model loaded, testing SIMPLIFIED entity extraction...')

prompt = """Extract entities from this text as a JSON array only.

[{"type":"character","name":"Name"}]

Text: Once upon a time, a brave knight named Arthur lived in the castle.
JSON:"""

print(f"Prompt length: {len(prompt)} chars")
print("Calling llama with max_tokens=256, temp=0.4...")
start = time.time()
resp = llm(prompt, max_tokens=256, temperature=0.4)
duration = time.time() - start
text = resp['choices'][0]['text'].strip()
print(f"Response ({duration:.1f}s): {text[:300] if text else '(empty)'}")
print(f"Full response length: {len(text)} chars")
