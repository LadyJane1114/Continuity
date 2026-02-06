"""Configuration settings for entity extraction."""
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

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/app.log"

# Performance Configuration
RESPONSE_TIMEOUT = 120  # seconds for LLM classification
MAX_CONCURRENT_REQUESTS = 10
