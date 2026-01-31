"""Configuration settings for the AI solution."""
import os
from dotenv import load_dotenv

load_dotenv()

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")
MODEL_PATH = os.getenv("MODEL_PATH", "./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")
MODEL_PROVIDER = "llama-cpp"  # Options: "llama-cpp"

# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"  # Options: "chroma", "faiss"
VECTOR_DB_PATH = "./data/vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight, fast embedder

# RAG Configuration
TOP_K_RESULTS = 5  # Number of similar documents to retrieve
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks

# Data Ingestion Configuration
MAX_SEGMENT_LENGTH = int(os.getenv("MAX_SEGMENT_LENGTH", 30000))
ENABLE_AUTO_CHUNKING = os.getenv("ENABLE_AUTO_CHUNKING", "true").lower() == "true"
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.95))
SEGMENT_COLLECTION_NAME = os.getenv("SEGMENT_COLLECTION_NAME", "story_segments")

# Web API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_TITLE = "AI Assistant API"
API_VERSION = "1.0.0"

# Entity Extraction Configuration
ENTITY_EXTRACTION_MODE = os.getenv("ENTITY_EXTRACTION_MODE", "hybrid").lower()
if ENTITY_EXTRACTION_MODE not in ["hybrid", "slm-only"]:
    raise ValueError(f"Invalid ENTITY_EXTRACTION_MODE: {ENTITY_EXTRACTION_MODE}. Must be 'hybrid' or 'slm-only'")

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_PREFIX = "!"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/app.log"

# Performance Configuration
MAX_CONTEXT_TOKENS = 2000
RESPONSE_TIMEOUT = 120  # seconds (increased for SLM classification)
MAX_CONCURRENT_REQUESTS = 10
