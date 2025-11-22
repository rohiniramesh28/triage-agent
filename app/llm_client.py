import os
import time
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _mock_extract(description: str) -> dict:
    desc = description.lower()
    summary = description.strip().split("\n")[0][:200]
    
    if any(k in desc for k in ["fail", "error", "500", "exception", "crash"]):
        category = "Bug"
        severity = "High" if "500" in desc or "crash" in desc else "Medium"
    elif any(k in desc for k in ["login", "password", "401", "2fa", "reset"]):
        category = "Login"
        severity = "High" if "401" in desc else "Medium"
    elif any(k in desc for k in ["slow", "latency", "time out"]):
        category = "Performance"
        severity = "Medium"
    elif any(k in desc for k in ["how to", "how do i", "how to change", "question"]):
        category = "Question/How-To"
        severity = "Low"
    elif any(k in desc for k in ["invoice", "billing", "payment", "promo", "refund"]):
        category = "Billing"
        severity = "Medium"
    else:
        category = "Bug"
        severity = "Low"
    return {"summary": summary, "category": category, "severity": severity}


def extract_ticket_fields(description: str, retries: int = 2, backoff: float = 0.5) -> dict:
    print(">>> USING REAL OPENAI API <<<" if OPENAI_API_KEY else ">>> MOCK MODE <<<")

    if not OPENAI_API_KEY:
        return _mock_extract(description)
    import openai
    openai.api_key = OPENAI_API_KEY
    prompt = f"""
        Extract from the ticket description the following JSON:
        {{"summary":"", "category":"", "severity":""}}
        Rules:
        - summary: 1-2 lines
        - category: one of Billing, Login, Performance, Bug, Question/How-To
        - severity: Low, Medium, High, Critical
        Ticket description:
        \"\"\"{description}\"\"\"
        Only return valid JSON.
        """
    for i in range(retries+1):
        try:
            resp = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{"role":"user","content":prompt}],
                max_tokens=200,
                temperature=0.0
            )
            text = resp.choices[0].message.content.strip()
            import json
            data = json.loads(text)
            return {
                "summary": data.get("summary", "")[:400],
                "category": data.get("category", "Bug"),
                "severity": data.get("severity", "Low")
            }
        except Exception as e:
            if i == retries:
                return _mock_extract(description)
            time.sleep(backoff * (2 ** i))
    return _mock_extract(description)

