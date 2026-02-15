# fact_extractor.py
"""
LLM-first fact extraction using a local Phi-4 mini model via LLMManager.
- Sentence-scoped, JSON-constrained prompts per (entity, sentence)
- Preserves evidence spans and your existing output schema
- Optional regex fallback (disabled by default)
"""

from __future__ import annotations
import re
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from typing import Dict, List, Any, Optional, Tuple

import logging
logger = logging.getLogger(__name__)

Sentence = Tuple[int, int, str]  # (start, end, sentence_text)


class FactExtractor:
    def __init__(
        self,
        llm=None,                      # LLMManager instance (Phi-4 mini)
        use_llm: bool = True,          # enable LLM extraction
        max_facts_per_entity: int = 3,
        rules_fallback: bool = False,  # keep regex rules as a fallback (off by default)
        temperature: float = 0.2,
        max_tokens: int = 160,
    ):
        """
        Args:
            llm: LLMManager instance (uses llama-cpp to run Phi-4 mini locally)
            use_llm: If True, use Phi-4 as the primary fact extractor
            max_facts_per_entity: hard cap per entity to avoid verbosity
            rules_fallback: if True, apply legacy regex rules when LLM returns no facts
            temperature / max_tokens: decoding & budget for generate_json
        """
        self.llm = llm
        self.use_llm = use_llm
        self.max_facts_per_entity = max_facts_per_entity
        self.rules_fallback = rules_fallback
        self.temperature = temperature
        self.max_tokens = max_tokens

        # --- Legacy rules (optional fallback only) ---
        # Apposition: "Ludwig van Beethoven, a German composer, ..."
        self._apposition = re.compile(
            r"\b(?P<name>[A-Z][\w\-]*(?:\s+(?:van|von|de|del|da|di|la|le))?(?:\s+[A-Z][\w\-]+)?)\s*,\s+"
            r"(?P<role>(?:the|a|an)\s+[a-z][^,]+?),",
            re.IGNORECASE,
        )
        # Possessive NP: "Beethoven’s early period ..."
        self._possessive = re.compile(
            r"\b(?P<name>[A-Z][\w\-]*(?:\s+[A-Z][\w\-]+)*)[’']s\s+(?P<object>(?:[a-z]+(?:\s+|\-))+[a-z]+)",
            re.IGNORECASE,
        )
        # Lightweight SVO: "Ludwig van Beethoven was a German composer ..."
        self._svo = re.compile(
            r"\b(?P<name>[A-Z][\w\-]*(?:\s+(?:van|von|de|del|da|di|la|le))?(?:\s+[A-Z][\w\-]+)*)\s+"
            r"(?P<verb>(?:is|was|leads|led|holds|held|owns|owned|built|builds|found|finds|"
            r"discovered|discovers|guards|guarded|sails|sailed|manages|managed|directs|directed))\s+"
            r"(?P<object>[^,.;:]{1,60})",
            re.IGNORECASE,
        )

    # ---------- Public API ----------
    
    async def extract_facts_for_entities(
        self, text: str, entities: list[dict], time_id: str
    ) -> dict[str, list[dict]]:
        """
        Async entry point used by the FastAPI route.
        """
        sentences = self._split_sentences_with_spans(text)
        index = self._build_sentence_index(sentences)
        results: dict[str, list[dict]] = {}

        for ent in entities:
            name = ent.get("name", "").strip()
            ent_id = ent.get("id")
            if not name or not ent_id:
                continue

            aliases = ent.get("aliases") or []
            mention_sents = self._find_mention_sentences(name, index, aliases)

            facts: list[dict] = []
            for (start, end, sent_text) in mention_sents:
                # LLM-first extraction
                llm_facts = await self._llm_extract_facts_for_sentence_async(name, sent_text)
                for sf in llm_facts:
                    facts.append(
                        self._mk_fact(
                            sf,
                            sent_text,
                            start,
                            end,
                            time_id,
                            confidence=0.80,
                            method="llm",
                        )
                    )

                # Optional: rule fallback if enabled and LLM returned nothing
                if self.rules_fallback and not llm_facts:
                    facts.extend(self._facts_from_sentence_rules(name, (start, end, sent_text), time_id, aliases))

                if len(facts) >= self.max_facts_per_entity:
                    break

            # de-dup + cap
            uniq, seen = [], set()
            for f in facts:
                k = (f["fact"].strip().lower(), f["evidence"]["start"], f["evidence"]["end"])
                if k not in seen:
                    uniq.append(f); seen.add(k)

            results[ent_id] = uniq[: self.max_facts_per_entity]
        
        # After we compute llm_facts
        if not llm_facts:
            # TEMP DEBUG: attach the raw text (first 300 chars) as a pseudo-fact so it shows up in the API
            # (We need the raw text here, so capture it in the helper instead of returning only facts.)
            results["__debug_raw_text"] = text[:300]

        return results



    # ---------- LLM extraction ----------
    
    # --- ADD/REPLACE inside class FactExtractor ---
    
    async def _llm_extract_facts_for_sentence_async(self, name: str, sentence: str) -> list[str]:
        if not self.llm or not self.use_llm:
            return []

        prompt = (
            "You extract facts strictly from the given sentence.\n"
            f"Target entity: {name}\n"
            "Return JSON ONLY with EXACTLY this schema:\n"
            "{ \"facts\": [\"<fact-1>\", \"<fact-2>\"] }\n"
            "Rules:\n"
            "- Include 0–3 facts explicitly supported by THIS sentence.\n"
            "- No external knowledge.\n"
            "- Use DOUBLE quotes. Do NOT use single quotes.\n"
            "- Do NOT include markdown, code fences, or any text outside the JSON object.\n"
            "- If no facts, return {\"facts\": []} exactly.\n\n"
            f"Sentence: {sentence}\n"
            "Example output: {\"facts\": [\"Ludwig van Beethoven was a German composer.\","
            " \"His early period lasted until 1802.\"]}"
        )

        # 1) Call Phi‑4 (await is required)
        
        print("\n[FACT DEBUG] -------- PROMPT BEGIN --------")
        print(prompt)
        print("[FACT DEBUG] -------- PROMPT END   --------\n")

        text = await self.llm.generate_json(prompt, temperature=self.temperature, max_tokens=self.max_tokens)  # type: ignore

        # 2) DEBUG/PRINTS — show the raw model output in the console
        print("\n[FACT DEBUG] -------- RAW LLM OUTPUT BEGIN --------")
        # Print first 800 chars to avoid overwhelming the console
        print(text[:800])
        if len(text) > 800:
            print("... (truncated) ...")
        print("[FACT DEBUG] -------- RAW LLM OUTPUT END   --------\n")

        # Also log via logger for file logs
        logger.debug("[LLM raw %d chars] %s", len(text), (text[:300].replace("\n", " ") + ("..." if len(text) > 300 else "")))

        # 3) Parse JSON
        data = self._safe_json(text)
        logger.debug("[LLM parsed] %s", data)

        facts = [s.strip() for s in data.get("facts", []) if isinstance(s, str) and s.strip()]
        logger.debug("[LLM facts] %s", facts)

        return facts


    # ---------- Legacy rules (fallback) ----------
    def _facts_from_sentence_rules(
        self, name: str, sent: Sentence, time_id: str, aliases: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        start, end, text = sent
        facts: List[Dict[str, Any]] = []

        # Apposition
        for m in self._apposition.finditer(text):
            if self._name_matches(name, m.group("name"), aliases):
                role = m.group("role").strip()
                facts.append(self._mk_fact(f"{name} is {role}.", text, start, end, time_id, 0.74, "rule"))

        # Possessive (guard against bare adjectives like "early")
        for m in self._possessive.finditer(text):
            if self._name_matches(name, m.group("name"), aliases):
                obj = re.sub(r"\s+", " ", m.group("object").strip())
                if obj.lower() in {"early", "middle", "late"}:
                    after = text[m.end(): m.end() + 12]
                    if re.match(r"\s*period\b", after, re.IGNORECASE):
                        obj = f"{obj} period"
                    else:
                        continue
                facts.append(self._mk_fact(f"{name} has {obj}.", text, start, end, time_id, 0.70, "rule"))

        # SVO
        for m in self._svo.finditer(text):
            if self._name_matches(name, m.group("name"), aliases):
                verb = m.group("verb").strip().lower()
                obj = m.group("object").strip()
                facts.append(self._mk_fact(f"{name} {verb} {obj}.", text, start, end, time_id, 0.70, "rule"))

        # De-dup by fact text
        seen = set()
        unique = []
        for f in facts:
            key = f["fact"].lower()
            if key not in seen:
                unique.append(f)
                seen.add(key)
        return unique

    # ---------- Helpers ----------
    def _split_sentences_with_spans(self, text: str) -> List[Sentence]:
        # Split on ., !, ? followed by whitespace OR end-of-string.
        sentences: List[Sentence] = []
        start = 0
        for m in re.finditer(r"[.!?](?:\s+|$)", text):
            end = m.end()
            chunk = text[start:end].strip()
            if chunk:
                sentences.append((start, end, chunk))
            start = end
        if start < len(text):
            chunk = text[start:].strip()
            if chunk:
                sentences.append((start, len(text), chunk))
        return sentences

    def _build_sentence_index(self, sentences: List[Sentence]) -> List[Sentence]:
        return sentences

    def _name_patterns(self, name: str, aliases: Optional[List[str]] = None):
        parts = [p for p in re.split(r"\s+", name.strip()) if p]
        variants = [re.escape(name)]
        if len(parts) >= 2:
            variants.append(re.escape(parts[-1]))  # surname
        for a in (aliases or []):
            if a and a.lower() != name.lower():
                variants.append(re.escape(a))
        possessive = r"(?:'s|’s)?"  # <-- use alternation, not newline
        pattern = rf"\b(?:{'|'.join(variants)}){possessive}\b"  # <-- use '|' to join
        return re.compile(pattern, re.IGNORECASE)

    def _find_mention_sentences(
        self, name: str, sentences: List[Sentence], aliases: Optional[List[str]] = None
    ) -> List[Sentence]:
        name_re = self._name_patterns(name, aliases)
        return [s for s in sentences if name_re.search(s[2])]

    def _name_matches(self, target: str, text_name: str, aliases: Optional[List[str]] = None) -> bool:
        def canon(s: str) -> str:
            s = s.strip(" ,.;:!?\"“”'’")
            s = re.sub(r"(?:'s|’s)$", "", s)  # strip possessive
            return s.lower()

        t = canon(target)
        x = canon(text_name)
        if t == x:
            return True
        parts = [p for p in re.split(r"\s+", target.strip()) if p]
        if len(parts) >= 2 and canon(parts[-1]) == x:
            return True
        for a in (aliases or []):
            if canon(a) == x:
                return True
        return False

    def _mk_fact(
        self,
        fact: str,
        source_text: str,
        s_start: int,
        s_end: int,
        time_id: str,
        confidence: float,
        method: str,
    ) -> Dict[str, Any]:
        return {
            "fact": fact,
            "sourceText": source_text,
            "evidence": {"timeId": time_id, "start": s_start, "end": s_end},
            "confidence": round(float(confidence), 3),
            "method": method,
        }

    def _safe_json(self, text: str) -> Dict[str, Any]:
        import json, re
        if not text:
            return {"facts": []}

        s = text.strip()

        # 1) Strip common wrappers (markdown fences / labels)
        s = s.replace("```json", "```").replace("```JSON", "```")
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("`").strip()

        # 2) Extract the first {...} block if present
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end != -1 and end > start:
            s = s[start : end + 1]

        # 3) Normalize smart quotes
        s = (s.replace("“", '"').replace("”", '"')
            .replace("’", "'").replace("‛", "'"))

        # 4) Try strict JSON first
        try:
            return json.loads(s)
        except Exception:
            pass

        # 5) Convert common JSON-ish outputs:
        #    a) single-quoted keys -> double-quoted
        s2 = re.sub(r"(?P<pre>[\{,\s])'(?P<key>\w+)'(?P<post>\s*:)", r'\g<pre>"\g<key>"\g<post>', s)
        #    b) single-quoted string values -> double-quoted
        s2 = re.sub(r':\s*\'([^\'\n]*)\'', lambda m: ':"{}"'.format(m.group(1).replace('"', '\\"')), s2)
        try:
            return json.loads(s2)
        except Exception:
            pass

        # 6) Last-resort: find ["...","..."] list and wrap
        m = re.search(r"\[(?:\s*\".*?\"\s*)(?:,\s*\".*?\"\s*)*\]", s)
        if m:
            try:
                arr = json.loads(m.group(0))
                return {"facts": arr}
            except Exception:
                pass

        return {"facts": []}