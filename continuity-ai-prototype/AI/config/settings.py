"""Configuration settings for the AI solution."""
import os
from dotenv import load_dotenv

load_dotenv()

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "phi-4-reasoning-q6_k.gguf")
MODEL_PATH = os.getenv("MODEL_PATH", "./models/phi-4-reasoning-q6_k.gguf")
MODEL_PROVIDER = "llama-cpp"  # Options: "llama-cpp"

# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"  # Options: "chroma", "faiss"
VECTOR_DB_PATH = "./data/vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight, fast embedder

# RAG Configuration
TOP_K_RESULTS = 5  # Number of similar documents to retrieve
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks

# Web API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_TITLE = "AI Assistant API"
API_VERSION = "1.0.0"

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_PREFIX = "!"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/app.log"

# Performance Configuration
MAX_CONTEXT_TOKENS = 2000
RESPONSE_TIMEOUT = 60  # seconds
MAX_CONCURRENT_REQUESTS = 10
