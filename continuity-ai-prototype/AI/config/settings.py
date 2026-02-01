import os
from dotenv import load_dotenv

load_dotenv()

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")
MODEL_PATH = os.getenv("MODEL_PATH", "./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")

# Web API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_TITLE = "Entity Extraction API"
API_VERSION = "1.0.0"

<<<<<<< Updated upstream
# Entity Extraction Configuration
ENTITY_EXTRACTION_MODE = os.getenv("ENTITY_EXTRACTION_MODE", "hybrid").lower()
if ENTITY_EXTRACTION_MODE not in ["hybrid", "slm-only"]:
    raise ValueError(f"Invalid ENTITY_EXTRACTION_MODE: {ENTITY_EXTRACTION_MODE}. Must be 'hybrid' or 'slm-only'")

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_PREFIX = "!"

=======
>>>>>>> Stashed changes
# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/app.log"

# Performance Configuration
RESPONSE_TIMEOUT = 120  # seconds for LLM classification
MAX_CONCURRENT_REQUESTS = 10
