from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_rag_query_endpoint():
    payload = {
        "query": "What is the key rotation policy?",
        "top_k": 2
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "sanitized_query" in data
    assert "faithfulness_score" in data
    assert len(data["retrieved_chunks"]) > 0
