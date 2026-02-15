# settings.py
"""Configuration settings for entity extraction."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------- Model Configuration ----------------
# Primary (legacy) model path (used elsewhere in the app)
MODEL_NAME = os.getenv("MODEL_NAME", "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")
MODEL_PATH = os.getenv("MODEL_PATH", "./models/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")

# NEW: Fact extraction model (Qwen 2.5 3B Instruct Q6_K or any GGUF)
# Accept either a full path (FACT_MODEL_PATH), or a bare filename we resolve under ./models
FACT_MODEL_PATH = os.getenv("FACT_MODEL_PATH", "").strip()
if FACT_MODEL_PATH:
    # If it's not an absolute/relative path to a file, assume it's a filename under ./models
    p = Path(FACT_MODEL_PATH)
    if not p.exists():
        candidate = Path("./models") / FACT_MODEL_PATH
        if candidate.exists():
            FACT_MODEL_PATH = str(candidate.resolve())
        else:
            # Fall back to MODEL_PATH if nothing resolves
            FACT_MODEL_PATH = MODEL_PATH
else:
    # If not provided, default to the legacy MODEL_PATH
    FACT_MODEL_PATH = MODEL_PATH

# ---------------- Web API Configuration ----------------
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))  # .env sets 8002; this cast will pick that up
API_TITLE = "Entity Extraction API"
API_VERSION = "1.0.0"

# ---------------- Logging Configuration ----------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "./logs/app.log"

# ---------------- Performance Configuration ----------------
RESPONSE_TIMEOUT = 120  # seconds for LLM classification
MAX_CONCURRENT_REQUESTS = 10