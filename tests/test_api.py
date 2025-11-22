import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_triage_basic():
    data = {"description": "Checkout keeps failing with error 500 on mobile when I try to pay."}
    r = client.post("/triage", json=data)
    assert r.status_code == 200
    j = r.json()
    assert "summary" in j
    assert j["category"] in ["Bug","Login","Billing","Performance","Question/How-To"]
    assert j["severity"] in ["Low","Medium","High","Critical"]
    assert "suggested_action" in j

def test_empty_description():
    r = client.post("/triage", json={"description": ""})
    assert r.status_code == 400

def test_long_description():
    long_desc = "error " * 2000
    r = client.post("/triage", json={"description": long_desc})
    assert r.status_code in (200, 422, 400)
