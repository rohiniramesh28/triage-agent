from pydantic import BaseModel, Field
from typing import List

class TriageRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=10000)

class KBEntry(BaseModel):
    id: str
    title: str
    category: str
    symptoms: List[str]
    recommended_action: str

class KBMatch(BaseModel):
    id: str
    title: str
    score: float
    category: str
    recommended_action: str

class TriageResponse(BaseModel):
    summary: str
    category: str
    severity: str
    known_issue: bool
    matched_kb: List[KBMatch]
    suggested_action: str
