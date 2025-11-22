from typing import List
from models.schemas import KBMatch
from kb.search import search_kb
from app.llm_client import extract_ticket_fields

def decide_known_or_new(matches: List[KBMatch], threshold: float = 2.0) -> bool:
    if not matches:
        return False
    top = matches[0]
    return top.score >= threshold

def propose_action(known_issue: bool, matches: List[KBMatch], category: str, severity: str) -> str:
    if known_issue and matches:
        return (
            f"Known issue ({matches[0].id}): Attach KB article '{matches[0].title}' "
            f"and respond to user. Recommended: {matches[0].recommended_action}"
        )

    if severity == "Critical":
        return "Escalate immediately to on-call SRE/backend team and request logs."
    if severity == "High":
        return "Escalate to engineering with priority; ask user for logs/screenshots."
    if severity == "Medium":
        return "Ask customer for more logs/screenshots; reproduce steps; assign to engineering backlog."
    
    return "Ask customer for more details / steps to reproduce."

def triage(description: str) -> dict:
    fields = extract_ticket_fields(description)
    summary = fields["summary"]
    category = fields["category"]
    severity = fields["severity"]
    matches = search_kb(description, top_k=3)
    known = decide_known_or_new(matches)
    action = propose_action(known, matches, category, severity)

    return {
        "summary": summary,
        "category": category,
        "severity": severity,
        "known_issue": known,
        "matched_kb": [m.dict() for m in matches],
        "suggested_action": action
    }
