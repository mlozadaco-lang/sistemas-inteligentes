# -*- coding: utf-8 -*-
# "Inteligencia" simple y helpers de cálculo

from typing import Dict, List, Tuple, Optional
from data.catalog import AREAS, SMART_KEYWORDS, QUESTIONS

def smart_infer_area(message: str) -> Tuple[str, int, List[str]]:
    low = message.lower()
    scores: Dict[str, int] = {a: 0 for a in SMART_KEYWORDS}
    hits: Dict[str, List[str]] = {a: [] for a in SMART_KEYWORDS}
    for area, keys in SMART_KEYWORDS.items():
        for k in keys:
            if k in low:
                scores[area] += 1
                hits[area].append(k)
    area = max(scores.items(), key=lambda kv: kv[1])[0]
    return area, scores[area], hits[area]

def suggest_profession(area: str, used: Optional[List[str]] = None) -> Optional[str]:
    roles = AREAS.get(area, [])
    if not roles:
        return None
    used = set(used or [])
    for r in roles:
        if r not in used:
            return r
    return roles[0] if roles else None

def area_counts_in_questions() -> Dict[str, int]:
    counts = {a: 0 for a in AREAS}
    for q in QUESTIONS:
        for _, ar in q["opts"]:
            counts[ar] += 1
    return counts

def normalized_scores(scores: Dict[str, int]) -> Dict[str, float]:
    counts = area_counts_in_questions()
    return {a: (scores[a] / max(1, counts[a])) for a in scores}
