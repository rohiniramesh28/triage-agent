# Support Ticket Triage Agent

This project implements a small AI-assisted agent that helps classify and triage support tickets. The goal is to take a free-text issue description, extract key fields, check for related known issues in a knowledge base, and recommend the next action. The project is implemented using FastAPI with a modular structure that separates the API layer, the agent logic, and the knowledge base search.

---

## Overview

Support teams often receive large numbers of tickets, and manually categorizing and routing them can take time.
This agent attempts to automate part of this workflow by:

1. Extracting a short summary, category, and severity from a ticket description.
2. Searching a small JSON-based knowledge base for similar issues.
3. Determining whether the ticket looks like a known issue or a new one.
4. Returning a recommended next step.
5. Exposing the logic as an API endpoint (POST /triage).

The agent can run in two modes:

* Using a real OpenAI model, if an API key is provided.
* Using a mock extractor if no key is set.

---

## Project Structure


support-ticket-triage/
│── app/
│   ├── main.py          # FastAPI application entrypoint
│   └── router.py        # Defines the /triage endpoint
│
│── agent/
│   └── triage_agent.py  # Core triage logic and LLM integration
│
│── kb/
│   ├── kb.json          # Knowledge base entries
│   └── search.py        # KB loading and simple keyword scoring
│
│── models/
│   └── schemas.py       # Pydantic models for request/response
│
│── tests/
│   └── test_api.py      # Basic API tests
│
│── Dockerfile
│── requirements.txt
│── README.md


---

## How It Works

### 1. Field Extraction

The agent extracts summary, category, and severity from the ticket description.
If an OpenAI API key is present, a real LLM is used.
If not, the project falls back to a simple rule-based extractor.

### 2. KB Search

The agent loads the local knowledge base (kb.json) and performs a lightweight keyword match to find similar issues.
Top matches are scored and returned.

### 3. Decision Logic

If a match has a sufficiently high score, the issue is treated as known.
Otherwise, it is marked as a new issue.
The agent then recommends an appropriate next action.

---

## API Example

### Request


POST /triage


Example input:

json
{
  "description": "Checkout failing with error 500 when I try to pay on mobile."
}


### Example Output

json
{
  "summary": "Checkout failing with error 500 when I try to pay on mobile.",
  "category": "Bug",
  "severity": "High",
  "known_issue": true,
  "matched_kb": [
    {
      "id": "ISSUE-101",
      "title": "Checkout error 500 on mobile",
      "score": 4.218,
      "category": "Bug",
      "recommended_action": "Escalate to payments team; link incident INC-2023-09-10"
    }
  ],
  "suggested_action": "Known issue: Attach KB article and respond to the user."
}


---

## Local Setup

### Requirements

* Python 3.10 or above
* FastAPI
* Uvicorn
* (Optional) OpenAI API key for real LLM extraction

### Installation


python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt


### Running the Service


uvicorn app.main:app --reload


Open the interactive API docs at:


http://127.0.0.1:8000/docs


---

## Configuration

You can set the following environment variables in a .env file:


OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini


If no API key is provided, the service runs in mock mode.

---

## Testing

Basic tests are included. Run them using:


pytest


Tests cover:

* A valid triage request
* Empty description handling
* Response shape validation

---

## Docker

To build the container:


docker build -t triage-agent .


To run it:


docker run -p 8000:8000 triage-agent


---

## Production Considerations

If deployed in a real environment, the following factors should be considered:

* Running the API in a containerized environment such as AWS ECS, GCP Cloud Run, or Azure Container Apps
* Storing secrets using environment variables or a hosted secret manager
* Adding structured logging and monitoring
* Optionally using a more advanced similarity search (e.g., vector embeddings)
* Adding authentication and rate limiting if exposed publicly
* Ensuring retry logic and timeouts for LLM calls

---"# triage-agent" 
