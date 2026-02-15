import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.ner_extractor import HybridNERExtractor
from models.fact_extractor import FactExtractor
from config.settings import EXPORT_JSON_DIR

class ExtractRequest(BaseModel):
    text: str
    time_id: Optional[str] = "t_001"
    use_llm: Optional[bool] = None

def create_app(
    ner_extractor: HybridNERExtractor,
    fact_extractor: Optional[FactExtractor] = None,
) -> FastAPI:
    app = FastAPI(title="Entity Extraction API", version="1.1.2")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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

        entities: List[Dict[str, Any]] = await ner_extractor.extract_entities(text=text, time_id=time_id)

        if entities and fact_extractor:
            if req.use_llm is not None:
                fact_extractor.use_llm = bool(req.use_llm)

            facts_map: Dict[str, List[Dict[str, Any]]] = await fact_extractor.extract_facts_for_entities(
                text, entities, time_id
            )
            for e in entities:
                e["facts"] = facts_map.get(e.get("id"), [])

        payload: Dict[str, Any] = {"entities": entities, "count": len(entities)}

        # export response JSON
        try:
            ts = time.strftime("%Y%m%d-%H%M%S")
            rid = uuid.uuid4().hex[:8]
            out_path = Path(EXPORT_JSON_DIR) / f"extract_{ts}_{rid}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            payload["exportPath"] = str(out_path)
        except Exception as ex:
            # non-fatal; avoid breaking the response
            print(f"[export] Failed to write JSON: {ex}")

        return payload

    return app