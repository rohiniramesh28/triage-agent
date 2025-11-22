from fastapi import FastAPI
from app.router import router
import uvicorn
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI(title="Support Ticket Triage Agent")
app.include_router(router)

@app.get("/")
async def root():
    return {"status": "ok", "service": "support-ticket-triage"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
