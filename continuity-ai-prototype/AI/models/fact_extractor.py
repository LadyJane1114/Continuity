from __future__ import annotations
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

Sentence = Tuple[int, int, str]  # (start, end, sentence_text)


class FactExtractor:
    def __init__(
        self,
        llm=None,
        use_llm: bool = True,
        max_facts_per_entity: int = 3,
        rules_fallback: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 160,
    ):
        self.llm = llm
        self.use_llm = use_llm
        self.max_facts_per_entity = max_facts_per_entity
        self.rules_fallback = rules_fallback
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Optional regex rules (fallback only)
        self._apposition = re.compile(
            r"\b(?P<name>[A-Z][\w\-]*(?:\s+(?:van|von|de|del|da|di|la|le))?(?:\s+[A-Z][\w\-]+)?)\s*,\s+"
            r"(?P<role>(?:the|a|an)\s+[a-z][^,]+?),",
            re.IGNORECASE,
        )
        self._possessive = re.compile(
            r"\b(?P<name>[A-Z][\w\-]*(?:\s+[A-Z][\w\-]+)*)[’']s\s+(?P<object>(?:[a-z]+(?:\s+|-))+[a-z]+)",
            re.IGNORECASE,
        )
        self._svo = re.compile(
            r"\b(?P<name>[A-Z][\w\-]*(?:\s+(?:van|von|de|del|da|di|la|le))?(?:\s+[A-Z][\w\-]+)*)\s+"
            r"(?P<verb>(?:is|was|leads|led|holds|held|owns|owned|built|builds|found|finds|"
            r"discovered|discovers|guards|guarded|sails|sailed|manages|managed|directs|directed))\s+"
            r"(?P<object>[^,.;:]{1,60})",
            re.IGNORECASE,
        )

    # ---------------- Public API ----------------

    async def extract_facts_for_entities(
        self, text: str, entities: List[dict], time_id: str
    ) -> Dict[str, List[dict]]:
        sentences = self._split_sentences_with_spans(text)
        results: Dict[str, List[dict]] = {}

        for ent in entities:
            name = (ent.get("name") or "").strip()
            ent_id = ent.get("id")
            if not name or not ent_id:
                continue

            aliases = ent.get("aliases") or []
            mention_sents = self._find_mention_sentences(name, sentences, aliases)

            facts: List[dict] = []
            for start, end, sent_text in mention_sents:
                llm_facts = await self._llm_extract_facts_for_sentence(name, sent_text)
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

                if self.rules_fallback and not llm_facts:
                    facts.extend(
                        self._facts_from_sentence_rules(
                            name, (start, end, sent_text), time_id, aliases
                        )
                    )

                if len(facts) >= self.max_facts_per_entity:
                    break

            # de-dup by (fact text + span), then cap
            uniq, seen = [], set()
            for f in facts:
                key = (f["fact"].strip().lower(), f["evidence"]["start"], f["evidence"]["end"])
                if key not in seen:
                    uniq.append(f)
                    seen.add(key)
            results[ent_id] = uniq[: self.max_facts_per_entity]

        return results

    # ---------------- LLM extraction ----------------

    async def _llm_extract_facts_for_sentence(self, name: str, sentence: str) -> List[str]:
        if not self.llm or not self.use_llm:
            return []

        prompt = (
            "You extract facts strictly from the given sentence.\n"
            f"Target entity: {name}\n"
            'Return JSON ONLY with EXACTLY this schema:\n{"facts": ["<fact-1>", "<fact-2>"]}\n'
            "Rules:\n"
            "- Include 0–3 facts explicitly supported by THIS sentence.\n"
            "- No external knowledge.\n"
            "- Use DOUBLE quotes. Do NOT use single quotes.\n"
            "- Do NOT include markdown/code fences or any extra text.\n"
            '- If no facts, return {"facts": []} exactly.\n\n'
            f"Sentence: {sentence}\n"
            'Example output: {"facts": ["Ludwig van Beethoven was a German composer.", "His early period lasted until 1802."]}'
        )

        text = await self.llm.generate_json(
            prompt, temperature=self.temperature, max_tokens=self.max_tokens  # type: ignore
        )
        data = self._safe_json(text)
        facts = [s.strip() for s in data.get("facts", []) if isinstance(s, str) and s.strip()]
        return facts

    # ---------------- Regex fallback (optional) ----------------

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
                    after = text[m.end() : m.end() + 12]
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
        unique, seen = [], set()
        for f in facts:
            k = f["fact"].lower()
            if k not in seen:
                unique.append(f)
                seen.add(k)
        return unique

    # ---------------- Helpers ----------------

    def _split_sentences_with_spans(self, text: str) -> List[Sentence]:
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

    def _name_patterns(self, name: str, aliases: Optional[List[str]] = None):
        parts = [p for p in re.split(r"\s+", name.strip()) if p]
        variants = [re.escape(name)]
        if len(parts) >= 2:
            variants.append(re.escape(parts[-1]))  # surname
        for a in (aliases or []):
            if a and a.lower() != name.lower():
                variants.append(re.escape(a))
        possessive = r"(?:'s|’s)?"
        pattern = rf"\b(?:{'|'.join(variants)}){possessive}\b"
        return re.compile(pattern, re.IGNORECASE)

    def _find_mention_sentences(
        self, name: str, sentences: List[Sentence], aliases: Optional[List[str]] = None
    ) -> List[Sentence]:
        name_re = self._name_patterns(name, aliases)
        return [s for s in sentences if name_re.search(s[2])]

    def _name_matches(self, target: str, text_name: str, aliases: Optional[List[str]] = None) -> bool:
        def canon(s: str) -> str:
            s = s.strip(' ,.;:!?"“”\'’')
            s = re.sub(r"(?:'s|’s)$", "", s)
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
        if not text:
            return {"facts": []}

        s = text.strip()
        s = s.replace("```json", "```").replace("```JSON", "```")
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("`").strip()

        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end != -1 and end > start:
            s = s[start : end + 1]

        s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‛", "'")

        try:
            return json.loads(s)
        except Exception:
            pass

        s2 = re.sub(r"(?P<pre>[\{,\s])'(?P<key>\w+)'(?P<post>\s*:)", r'\g<pre>"\g<key>"\g<post>', s)
        s2 = re.sub(r':\s*\'([^\'\n]*)\'', lambda m: ':"{}"'.format(m.group(1).replace('"', '\\"')), s2)
        try:
            return json.loads(s2)
        except Exception:
            pass

        m = re.search(r'\[(?:\s*".*?"\s*)(?:,\s*".*?"\s*)*\]', s)
        if m:
            try:
                arr = json.loads(m.group(0))
                return {"facts": arr}
            except Exception:
                pass

        return {"facts": []}