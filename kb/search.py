import json 
from pathlib import Path
from typing import List
from difflib import SequenceMatcher
import re
from models.schemas import KBEntry, KBMatch


KB_PATH = Path(__file__).resolve().parent / "kb.json"

def load_kb() -> List[KBEntry]:
    raw = json.loads(KB_PATH.read_text(encoding="utf-8"))
    return [KBEntry(**r) for r in raw]

def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def score_match(desc: str, kb_entry: KBEntry) -> float:
    desc_n = normalize_text(desc)
    tokens = set(desc_n.split())
    symptoms_token = set("".join(kb_entry.symptoms).lower().split())
    overlap = len(tokens & symptoms_token)
    title_n = normalize_text(kb_entry.title)
    fuzz = SequenceMatcher(None, desc_n, title_n).ratio()
    score = overlap * 1.0 + fuzz * 5.0
    return score

def search_kb(description: str, top_k: int = 3) -> List[KBMatch]:
    kb = load_kb()
    scored = []
    for e in kb:
        s = score_match(description, e)
        scored.append((s, e))
    scored.sort(key=lambda x: x[0], reverse=True)
    matches = []
    for s, e in scored[:top_k]:
        matches.append(KBMatch(
            id=e.id,
            title=e.title,
            score=round(s, 3),
            category=e.category,
            recommended_action=e.recommended_action
        ))
    return matches