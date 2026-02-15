# interfaces/web_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from models.ner_extractor import HybridNERExtractor
from models.fact_extractor import FactExtractor

class ExtractRequest(BaseModel):
    text: str
    time_id: Optional[str] = "t_001"
    # Optional: toggle LLM-assisted facts per request
    use_llm: Optional[bool] = None

def create_app(
    ner_extractor: HybridNERExtractor,
    fact_extractor: Optional[FactExtractor] = None,
) -> FastAPI:
    app = FastAPI(title="Entity Extraction API", version="1.1.2")

    # --- CORS for local development ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # permissive for local dev
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"status": "ok"}

    @app.post("/entities/extract")
    async def extract(req: ExtractRequest) -> Dict[str, Any]:
        text = (req.text or "").strip()
        time_id = req.time_id or "t_001"

        # 1) Entities via NER (async)
        entities: List[Dict[str, Any]] = await ner_extractor.extract_entities(
            text=text, time_id=time_id
        )

        # 2) Facts via Phi‑4 mini (async) — AWAIT this call
        if entities and fact_extractor:
            if req.use_llm is not None:
                fact_extractor.use_llm = bool(req.use_llm)

            facts_map: Dict[str, List[Dict[str, Any]]] = await fact_extractor.extract_facts_for_entities(
                text, entities, time_id
            )

            for e in entities:
                e_id = e.get("id")
                e["facts"] = facts_map.get(e_id, [])

        return {"entities": entities, "count": len(entities)}

    return app