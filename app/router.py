from fastapi import APIRouter, HTTPException, Request
from models.schemas import TriageRequest, TriageResponse, KBMatch
from agent.triage_agent import triage
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import os
import time

router = APIRouter()   
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
client_counters = {}  
def is_rate_limited(client_ip: str) -> bool:
    now = int(time.time())
    window = 60
    start, count = client_counters.get(client_ip, (now, 0))
    if now - start >= window:
        client_counters[client_ip] = (now, 1)
        return False
    if count + 1 > RATE_LIMIT:
        return True
    client_counters[client_ip] = (start, count + 1)
    return False

@router.post("/triage", response_model=TriageResponse)
async def triage_endpoint(req: TriageRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="Description must not be empty")
    result = triage(req.description)
    matched = [KBMatch(**m) for m in result["matched_kb"]]
    return {
        "summary": result["summary"],
        "category": result["category"],
        "severity": result["severity"],
        "known_issue": result["known_issue"],
        "matched_kb": matched,
        "suggested_action": result["suggested_action"]
    }
